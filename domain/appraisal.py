from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class PropertyCondition(str, Enum):
    LUXURY = "luxury"  # +15-20%
    EXCELLENT = "excellent"  # +10-15%
    GOOD = "good"  # Baseline
    FAIR = "fair"  # -10-15%
    POOR = "poor"  # -20-30%
    RENOVATED = "luxury"  # Alias
    NEEDS_WORK = "fair"  # Alias


class AppraisalRequest(BaseModel):
    city: str
    zone: str
    property_type: str = "apartment"
    surface_sqm: Any
    condition: PropertyCondition = PropertyCondition.GOOD
    bedrooms: int | None = None
    phone: str | None = None
    email: str | None = None
    name: str | None = None

    @field_validator("surface_sqm", mode="before")
    @classmethod
    def parse_sqm(cls, v: Any) -> int:
        if isinstance(v, str):
            import re

            nums = re.sub(r"[^\d]", "", v)
            return int(nums) if nums else 0
        try:
            return int(v) if v is not None else 0
        except (ValueError, TypeError):
            return 0


class Comparable(BaseModel):
    title: str
    price: float
    surface_sqm: int
    price_per_sqm: float
    description: str | None = None
    url: str | None = None


class AppraisalResult(BaseModel):
    estimated_value: float
    estimated_range_min: float
    estimated_range_max: float
    avg_price_sqm: float
    price_sqm_min: float
    price_sqm_max: float
    comparables: list[Comparable]
    reasoning: str
    market_trend: str = "stable"  # rising, falling, stable

    # Metadata (NEW)
    id: str | None = None  # UUID from performance tracking
    investment_metrics: dict[str, Any] | None = None  # Serialized InvestmentMetrics
    confidence_level: int | None = None  # 1-100
    reliability_stars: int | None = None  # 1-5 stars

    disclaimer: str = (
        "This is an AI-generated estimate based on online data. "
        "It is not a formal professional appraisal."
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
