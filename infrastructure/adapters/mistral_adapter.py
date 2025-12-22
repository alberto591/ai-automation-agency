from mistralai import Mistral
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import AIPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class MistralAdapter(AIPort):
    def __init__(self) -> None:
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_response(self, prompt: str) -> str:
        try:
            chat_response = self.client.chat.complete(
                model=settings.MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}],  # type: ignore
            )
            if chat_response and chat_response.choices:
                content = chat_response.choices[0].message.content
                return str(content) if content else ""
            return ""
        except Exception as e:
            logger.error("MISTRAL_GENERATE_FAILED", context={"error": str(e)})
            raise ExternalServiceError("Failed to generate AI response", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embedding(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                model=settings.MISTRAL_EMBEDDING_MODEL, inputs=[text]
            )
            if response and response.data:
                return response.data[0].embedding  # type: ignore
            return []
        except Exception as e:
            logger.error("MISTRAL_EMBED_FAILED", context={"error": str(e)})
            raise ExternalServiceError("Failed to generate embedding", cause=str(e)) from e
