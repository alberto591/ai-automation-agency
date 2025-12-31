from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

# Import InvestmentMetrics from application layer
# Note: This creates a dependency from domain -> application
# For proper hexagonal architecture, we could define InvestmentMetrics in domain
# But for MVP speed, we'll use TYPE_CHECKING to avoid circular imports

if TYPE_CHECKING:
    pass


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

    # Investment Analysis (NEW)
    investment_metrics: dict[str, Any] | None = None  # Serialized InvestmentMetrics
    confidence_level: int | None = None  # 1-100
    reliability_stars: int | None = None  # 1-5 stars

    disclaimer: str = (
        "This is an AI-generated estimate based on online data. "
        "It is not a formal professional appraisal."
    )

    class Config:
        # Allow arbitrary types for investment_metrics
        arbitrary_types_allowed = True
