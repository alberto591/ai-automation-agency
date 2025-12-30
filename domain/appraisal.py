from enum import Enum

from pydantic import BaseModel


class PropertyCondition(str, Enum):
    RENOVATED = "renovated"  # +10-15%
    GOOD = "good"  # Baseline
    NEEDS_WORK = "needs_work"  # -15-20%


class AppraisalRequest(BaseModel):
    city: str
    zone: str
    property_type: str = "apartment"
    surface_sqm: int
    condition: PropertyCondition = PropertyCondition.GOOD
    bedrooms: int | None = None


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
    disclaimer: str = (
        "This is an AI-generated estimate based on online data. "
        "It is not a formal professional appraisal."
    )
