from enum import Enum

from pydantic import BaseModel


class Intent(str, Enum):
    BUY = "buy"  # +3
    SELL = "sell"  # +2
    RENT = "rent"  # +1
    INFO = "info"  # 0
    UNKNOWN = "unknown"


class Timeline(str, Enum):
    URGENT = "urgent"  # < 30 days (+3)
    MEDIUM = "medium"  # 2-3 months (+2)
    LONG = "long"  # 6+ months (+1)
    UNKNOWN = "unknown"  # (0)


class FinancingStatus(str, Enum):
    APPROVED = "approved"  # (+3)
    PROCESSING = "processing"  # (+2)
    TODO = "todo"  # (+1)
    UNKNOWN = "unknown"  # (0)


class LeadCategory(str, Enum):
    HOT = "HOT"  # 9-10
    WARM = "WARM"  # 6-8
    COLD = "COLD"  # < 6
    DISQUALIFIED = "DISQUALIFIED"


class QualificationData(BaseModel):
    """Answers collected during the 7-step qualification flow."""

    intent: Intent = Intent.UNKNOWN
    timeline: Timeline = Timeline.UNKNOWN
    budget: float | None = None  # <100k(+1), 100-300(+2), 300-600(+3), 600+(+3)
    financing: FinancingStatus = FinancingStatus.UNKNOWN
    location_specific: bool = False  # True(+2), False(+1 for general)
    property_specific: bool = False  # True(+2), False(+1 for open)
    has_contact_info: bool = False  # Derived from having phone & email (+2)


class LeadScore(BaseModel):
    """Calculated score and categorization."""

    raw_score: int  # 0-21
    normalized_score: int  # 1-10
    category: LeadCategory
    details: QualificationData
    action_item: str  # Suggestion for the agent/system
