import re
import time
from dataclasses import asdict

from application.services.investment_calculator import InvestmentCalculator
from application.services.local_property_search import LocalPropertySearchService
from domain.appraisal import (
    AppraisalRequest,
    AppraisalResult,
    Comparable,
    PropertyCondition,
)
from domain.ports import ResearchPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AppraisalService:
    def __init__(
        self,
        research_port: ResearchPort,
        local_search: LocalPropertySearchService | None = None,
        performance_logger=None,
    ):
        self.research = research_port
        self.investment_calc = InvestmentCalculator()
        self.local_search = local_search
        self.performance_logger = performance_logger

    def estimate_value(self, request: AppraisalRequest) -> AppraisalResult:
        """
        Generates a property valuation using AI research for comparables.
        """
        # Start performance tracking
        start_time = time.time()
        used_local_search = False
        used_perplexity = False
        
        logger.info("APPRAISAL_START", context=request.model_dump())

        # 1. Try Local Database First (Performance Optimization Phase 1)
        comparables = []
        if self.local_search:
            try:
                comparables = self.local_search.search_local_comparables(
                    city=request.city,
                    zone=request.zone,
                    property_type=request.property_type,
                    surface_sqm=request.surface_sqm,
                    min_comparables=3,
                )
                if comparables:
                    used_local_search = True
                    logger.info("LOCAL_SEARCH_SUCCESS", context={"count": len(comparables)})
            except Exception as e:
                logger.warning("LOCAL_SEARCH_FAILED", context={"error": str(e)})

        # 2. Fall back to Perplexity if local search didn't find enough
        if not comparables:
            used_perplexity = True
            logger.info("FALLBACK_TO_PERPLEXITY")
            try:
                research_text = self.research.find_market_comparables(
                    city=request.city,
                    zone=request.zone,
                    property_type=request.property_type,
                    surface_sqm=request.surface_sqm,
                )
                comparables = self._parse_comparables(research_text)
            except Exception as e:
                logger.error("APPRAISAL_RESEARCH_FAILED", context={"error": str(e)})
                # Fallback or empty if research fails
                comparables = []

        # 2. Calculate Market Metrics
        if not comparables:
            # Fallback logic if no comps found (e.g. use generic city data or fail gracefully)
            # For MVP, we return a conservative estimate or error.
            # Let's assume a baseline if 0 comps.
            logger.warning("APPRAISAL_NO_COMPS_FOUND")
            # Logic: Return 0 or specific error state?
            # Let's fabricate a wide range based on generic assumptions? No, dangerous.
            # Return empty/safe result.
            return self._create_fallback_result(request)

        avg_sqm_price = sum(c.price_per_sqm for c in comparables) / len(comparables)

        # 3. Apply Adjustments
        # Condition Adjustment
        adjustment_factor = 1.0
        if request.condition == PropertyCondition.RENOVATED:
            adjustment_factor = 1.15  # +15%
        elif request.condition == PropertyCondition.NEEDS_WORK:
            adjustment_factor = 0.85  # -15%

        adjusted_sqm_price = avg_sqm_price * adjustment_factor

        # Calculate Totals
        estimated_value = adjusted_sqm_price * request.surface_sqm
        min_val = estimated_value * 0.95  # +/- 5% range
        max_val = estimated_value * 1.05

        reasoning = (
            f"Based on {len(comparables)} listings in {request.zone} with an average "
            f"price of €{avg_sqm_price:.0f}/sqm. "
            f"Adjusted for '{request.condition.value}' condition."
        )

        # Calculate investment metrics
        estimated_rent = self.investment_calc.estimate_monthly_rent(
            property_price=int(estimated_value), zone=request.zone
        )

        investment_metrics = self.investment_calc.calculate_metrics(
            property_price=int(estimated_value),
            estimated_monthly_rent=estimated_rent,
        )

        # Calculate confidence level based on data quality
        confidence_level = self._calculate_confidence(len(comparables))
        reliability_stars = self._calculate_reliability_stars(confidence_level)

        return AppraisalResult(
            estimated_value=round(estimated_value, -3),  # Round to nearest thousand
            estimated_range_min=round(min_val, -3),
            estimated_range_max=round(max_val, -3),
            avg_price_sqm=round(adjusted_sqm_price, 0),
            price_sqm_min=round(min(c.price_per_sqm for c in comparables), 0),
            price_sqm_max=round(max(c.price_per_sqm for c in comparables), 0),
            comparables=comparables,
            reasoning=reasoning,
            investment_metrics=asdict(investment_metrics) if investment_metrics else None,
            confidence_level=confidence_level,
            reliability_stars=reliability_stars,
        )

    def _parse_comparables(self, text: str) -> list[Comparable]:
        """
        Use Mistral LLM to extract structured comparable data from Perplexity's natural language response.
        This is more robust than regex for handling varied response formats.
        """
        from mistralai import Mistral

        from config.settings import settings

        try:
            client = Mistral(api_key=settings.MISTRAL_API_KEY)

            extraction_prompt = f"""Extract real estate comparable data from the following text.
Return ONLY a JSON array of objects, each with: title (string), price (number in euros), surface_sqm (number).

FILTERING RULES:
- Only include properties that have BOTH a sale price AND square meters specified
- EXCLUDE rental properties (monthly prices like "€1,300/month")
- EXCLUDE auction properties ("asta", "auction", "giudiziaria")
- EXCLUDE properties with incomplete data
- Prefer recent listings when available

Text to parse:
{text}

Return format: [{{"title": "...", "price": 450000, "surface_sqm": 95}}, ...]
If no valid comparables found, return: []"""

            response = client.chat.complete(
                model=settings.MISTRAL_MODEL,
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"},  # Phase 2 optimization: JSON mode
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            import json

            data = json.loads(result_text)

            comps = []
            for item in data:
                try:
                    price = float(item["price"])
                    sqm = int(item["surface_sqm"])

                    if sqm > 0 and price > 10000:
                        psqm = price / sqm
                        # Sanity check: €500-€15000/sqm for Florence
                        if 500 < psqm < 15000:
                            comps.append(
                                Comparable(
                                    title=str(item["title"])[:100],
                                    price=price,
                                    surface_sqm=sqm,
                                    price_per_sqm=round(psqm, 0),
                                    description=str(item.get("title", ""))[:200],
                                )
                            )
                except (KeyError, ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid comparable: {item}. Error: {e}")
                    continue

            logger.info(f"Extracted {len(comps)} comparables using LLM")
            return comps

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}. Falling back to regex.")
            # Fallback to simple regex if LLM fails
            return self._parse_comparables_regex(text)

    def _parse_comparables_regex(self, text: str) -> list[Comparable]:
        """Fallback regex parser."""
        comps = []
        lines = text.split("\n")

        for line in lines:
            if "|---" in line or (line.strip().startswith("|") and "Title" in line):
                continue

            try:
                price_match = None
                if "€" in line:
                    price_match = re.search(r"€\s?([\d\.,]+)|([\d\.,]+)\s?€", line)
                elif "EUR" in line:
                    price_match = re.search(r"EUR\s?([\d\.,]+)|([\d\.,]+)\s?EUR", line)

                sqm_match = re.search(r"(\d+)\s?(?:sqm|mq|m²|m2|m\^2)", line, re.IGNORECASE)

                if price_match and sqm_match:
                    price_str = price_match.group(1) or price_match.group(2)
                    if price_str.count(".") > 1:
                        price_str = price_str.replace(".", "")
                    elif price_str.count(",") > 1:
                        price_str = price_str.replace(",", "")
                    elif "." in price_str and len(price_str.split(".")[-1]) == 3:
                        price_str = price_str.replace(".", "")
                    elif "," in price_str and len(price_str.split(",")[-1]) == 3:
                        price_str = price_str.replace(",", "")

                    price = float(price_str)
                    sqm = int(sqm_match.group(1))

                    if sqm > 0 and price > 10000:
                        psqm = price / sqm
                        if 500 < psqm < 15000:
                            comps.append(
                                Comparable(
                                    title=line[:60].strip() + "...",
                                    price=price,
                                    surface_sqm=sqm,
                                    price_per_sqm=round(psqm, 0),
                                    description=line.strip(),
                                )
                            )
            except Exception:
                continue

        return comps

    def _create_fallback_result(self, request: AppraisalRequest) -> AppraisalResult:
        """Returns valid but empty result when research fails."""
        return AppraisalResult(
            estimated_value=0,
            estimated_range_min=0,
            estimated_range_max=0,
            avg_price_sqm=0,
            price_sqm_min=0,
            price_sqm_max=0,
            comparables=[],
            reasoning="Could not find sufficient data to generate an estimate.",
            market_trend="unknown",
            confidence_level=0,
            reliability_stars=1,
        )

    def _calculate_confidence(self, num_comparables: int) -> int:
        """Calculate confidence level (1-100) based on data quality."""
        if num_comparables >= 5:
            return 90
        elif num_comparables >= 3:
            return 75
        elif num_comparables >= 1:
            return 50
        else:
            return 20

    def _calculate_reliability_stars(self, confidence_level: int) -> int:
        """Convert confidence level to 1-5 star rating."""
        if confidence_level >= 85:
            return 5
        elif confidence_level >= 70:
            return 4
        elif confidence_level >= 55:
            return 3
        elif confidence_level >= 40:
            return 2
        else:
            return 1
