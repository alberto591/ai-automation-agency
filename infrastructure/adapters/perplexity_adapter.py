from openai import OpenAI

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import ResearchPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PerplexityAdapter(ResearchPort):
    """Perplexity Labs API adapter for real-time research."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai"
        )
        self.model = "llama-3-sonar-large-32k-online"

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

            response = self.client.chat.completions.create(model=self.model, messages=messages)

            result = response.choices[0].message.content or ""
            logger.info("PERPLEXITY_SUCCESS", context={"result_length": len(result)})

            return result

        except Exception as e:
            logger.error("PERPLEXITY_FAILED", context={"error": str(e)})
            raise ExternalServiceError(
                f"Perplexity API search failed: {str(e)}", cause=str(e)
            ) from e
