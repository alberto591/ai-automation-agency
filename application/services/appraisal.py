import re
from dataclasses import asdict

from application.services.investment_calculator import InvestmentCalculator
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
    def __init__(self, research_port: ResearchPort):
        self.research = research_port
        self.investment_calc = InvestmentCalculator()

    def estimate_value(self, request: AppraisalRequest) -> AppraisalResult:
        """
        Generates a property valuation using AI research for comparables.
        """
        logger.info("APPRAISAL_START", context=request.model_dump())

        # 1. Research Active Listings
        query = (
            f"Find 3 active real estate listings for a {request.property_type} in "
            f"{request.city} area {request.zone}, around {request.surface_sqm} sqm. "
            f"Format: Title | Price | Sqm. Return only the data list."
        )

        try:
            research_text = self.research.search(query)
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
        Naively parses Perplexity output.
        In a robust system, we'd use a structured extraction LLM chain here.
        This regex is a placeholder for the MVP.
        Expected format lines: "Title... €300,000 ... 100 sqm"
        """
        comps = []
        # Support formats: € 300.000, 300.000 €, EUR 300.000, €300,000
        # and 75 mq, 75 sqm, 75 m²

        lines = text.split("\n")
        for line in lines:
            try:
                # Find price (look for € or EUR)
                if "€" in line:
                    # Match numbers like 300.000 or 300,000 associated with €
                    price_match = re.search(r"€\s?([\d\.,]+)|([\d\.,]+)\s?€", line)
                elif "EUR" in line:
                    price_match = re.search(r"EUR\s?([\d\.,]+)|([\d\.,]+)\s?EUR", line)
                else:
                    continue

                # Find sqm
                sqm_match = re.search(r"(\d+)\s?(?:sqm|mq|m²|m2)", line, re.IGNORECASE)

                if price_match and sqm_match:
                    # Extract price group (could be group 1 or 2)
                    price_str = price_match.group(1) or price_match.group(2)
                    price_str = price_str.replace(".", "").replace(",", "")
                    price = float(price_str)

                    sqm = int(sqm_match.group(1))

                    if sqm > 0 and price > 10000:  # Basic sanity check
                        psqm = price / sqm
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
