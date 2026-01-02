import time

from openai import OpenAI

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import ResearchPort
from infrastructure.logging import get_logger
from infrastructure.metrics import perplexity_api_calls_total, perplexity_api_duration_seconds

logger = get_logger(__name__)


class PerplexityAdapter(ResearchPort):
    """Perplexity Labs API adapter for real-time research."""

    def __init__(self, cache=None) -> None:
        self.client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai"
        )
        self.model = "sonar-pro"  # Advanced search with grounding
        self.cache = cache  # Optional cache for responses

    def search(self, query: str, context: str | None = None) -> str:
        """
        Perform real-time web research using Perplexity API.

        Use cases:
        1. Legal compliance checks (Gazzetta Ufficiale, EU AI Act updates)
        2. Live market comparables (current listings without scraping)
        3. Entity vetting (construction companies, commercial tenants)

        Args:
            query: Research question
            context: Optional context for better results

        Returns:
            Research findings as formatted text
        """
        try:
            messages: list[dict[str, str]] = []

            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})

            messages.append({"role": "user", "content": query})

            logger.info(
                "PERPLEXITY_SEARCH", context={"query": query[:100], "has_context": bool(context)}
            )

            # Track API call metrics
            perplexity_api_calls_total.inc()
            start_time = time.time()

            response = self.client.chat.completions.create(model=self.model, messages=messages)

            duration = time.time() - start_time
            perplexity_api_duration_seconds.observe(duration)

            result = response.choices[0].message.content or ""
            logger.info(
                "PERPLEXITY_SUCCESS",
                context={"result_length": len(result), "duration_seconds": round(duration, 2)},
            )

            return result

        except Exception as e:
            logger.error("PERPLEXITY_FAILED", context={"error": str(e)})
            raise ExternalServiceError(
                f"Perplexity API search failed: {str(e)}", cause=str(e)
            ) from e

    def research_legal_compliance(self, topic: str) -> str:
        query = f"Ricerca aggiornamenti normativi e legali recenti (Gazzetta Ufficiale, normativa italiana ed europea) su: {topic}. Fornisci un riassunto dei punti chiave."
        return self.search(
            query,
            context="Sei un consulente legale esperto in intelligenza artificiale e diritto immobiliare.",
        )

    def find_market_comparables(
        self,
        city: str,
        zone: str,
        property_type: str = "appartamento",
        surface_sqm: int = 100,
        radius_km: float = 2.0,
    ) -> str:
        """
        Find market comparables with caching support.
        Uses Italian-language query for better local results.
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(city, zone, property_type, surface_sqm)
            if cached:
                return cached

        # Italian query for better local results
        query = (
            f"Cerca 3 annunci immobiliari IN VENDITA (non affitto) per {property_type} "
            f"a {city}, CAP {zone}, circa {surface_sqm} mq. "
            f"Includi SOLO immobili con prezzo di vendita e metratura specificati. "
            f"Per ogni immobile fornisci: Titolo, Prezzo in €, Superficie in mq. "
            f"Cerca su Idealista.it, Immobiliare.it, Casa.it. "
            f"Escludi aste giudiziarie."
        )

        result = self.search(
            query, context="Sei un analista immobiliare esperto nel mercato italiano."
        )

        # Cache the result
        if self.cache:
            self.cache.set(city, zone, property_type, surface_sqm, result)

        return result
