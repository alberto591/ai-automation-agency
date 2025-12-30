from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PropertyFeatures(BaseModel):
    """Structured features for property valuation."""

    sqm: int = Field(..., description="Surface area in square meters")
    bedrooms: int = Field(default=1, description="Number of bedrooms")
    bathrooms: int = Field(default=1, description="Number of bathrooms")
    floor: int = Field(default=0, description="Floor level (0 for ground)")
    has_elevator: bool = Field(default=False)
    has_balcony: bool = Field(default=False)
    has_garden: bool = Field(default=False)
    condition: Literal["luxury", "excellent", "good", "fair", "poor"] = Field(default="good")
    energy_class: str | None = Field(default=None)
    property_age_years: int | None = Field(default=None)
    cadastral_category: str | None = Field(default="A/3")

    # Geospatial (Enriched)
    zone_slug: str | None = None
    distance_to_metro_m: int | None = None
    walkability_score: int | None = None


def extract_property_features(description: str, address: str | None = None) -> PropertyFeatures:
    """
    Extracts structured features from a raw property description using LLM logic.
    Uses Mistral with structured output for reliable feature extraction.
    """
    logger.info("EXTRACTING_FEATURES", context={"description_len": len(description)})

    # Use Mistral with structured output
    llm = ChatMistralAI(
        api_key=settings.MISTRAL_API_KEY,
        model_name=settings.MISTRAL_MODEL,
    ).with_structured_output(PropertyFeatures)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract structured property features from the description. Language: Italian/English. "
                "If features like sqm, floor, or elevator are missing, use sensible defaults based on typical urban apartments.",
            ),
            ("human", "{input}"),
        ]
    )

    try:
        extraction = llm.invoke(prompt.format(input=description))

        # Add address if provided
        if address and not extraction.zone_slug:
            # We could do geocoding/zone resolution here in the future
            extraction.zone_slug = address.split(",")[0].lower().replace(" ", "-")

        return extraction  # type: ignore[no-any-return]
    except Exception as e:
        logger.error("FEATURE_EXTRACTION_FAILED", context={"error": str(e)})
        # Fallback to default/minimal features
        return PropertyFeatures(sqm=80, condition="good")
