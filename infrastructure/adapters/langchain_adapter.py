from typing import cast

from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from pydantic import SecretStr

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import AIPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class LangChainAdapter(AIPort):
    def __init__(self) -> None:
        self.llm = ChatMistralAI(
            api_key=SecretStr(settings.MISTRAL_API_KEY),
            model=settings.MISTRAL_MODEL,
        )
        self.embeddings = MistralAIEmbeddings(
            api_key=SecretStr(settings.MISTRAL_API_KEY),
            model=settings.MISTRAL_EMBEDDING_MODEL,
        )

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return str(response.content)
        except Exception as e:
            logger.error("LANGCHAIN_GENERATE_FAILED", context={"error": str(e)})
            raise ExternalServiceError(
                "Failed to generate AI response via LangChain", cause=str(e)
            ) from e

    def get_embedding(self, text: str) -> list[float]:
        try:
            embedding = self.embeddings.embed_query(text)
            return cast(list[float], embedding)
        except Exception as e:
            logger.error("LANGCHAIN_EMBED_FAILED", context={"error": str(e)})
            raise ExternalServiceError(
                "Failed to generate embedding via LangChain", cause=str(e)
            ) from e
