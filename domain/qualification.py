from enum import Enum

from pydantic import BaseModel


class Intent(str, Enum):
    BUY = "buy"
    SELL = "sell"
    RENT = "rent"
    INFO = "info"
    UNKNOWN = "unknown"

    @property
    def score(self) -> int:
        return {
            self.BUY: 3,
            self.SELL: 2,
            self.RENT: 1,
            self.INFO: 0,
            self.UNKNOWN: 0,
        }.get(self, 0)


class Timeline(str, Enum):
    URGENT = "urgent"  # < 30 days
    MEDIUM = "medium"  # 2-3 months
    LONG = "long"  # 6+ months
    UNKNOWN = "unknown"

    @property
    def score(self) -> int:
        return {
            self.URGENT: 3,
            self.MEDIUM: 2,
            self.LONG: 1,
            self.UNKNOWN: 0,
        }.get(self, 0)


class FinancingStatus(str, Enum):
    APPROVED = "approved"
    PROCESSING = "processing"
    TODO = "todo"
    UNKNOWN = "unknown"

    @property
    def score(self) -> int:
        return {
            self.APPROVED: 3,
            self.PROCESSING: 2,
            self.TODO: 1,
            self.UNKNOWN: 0,
        }.get(self, 0)


class LeadCategory(str, Enum):
    HOT = "HOT"  # 9-10
    WARM = "WARM"  # 6-8
    COLD = "COLD"  # < 6
    DISQUALIFIED = "DISQUALIFIED"


class QualificationData(BaseModel):
    """Answers collected during the 7-step qualification flow."""

    intent: Intent = Intent.UNKNOWN
    timeline: Timeline = Timeline.UNKNOWN
    budget: float | None = None
    financing: FinancingStatus = FinancingStatus.UNKNOWN
    location_specific: bool | None = None  # True(+2), False(+1 for general)
    property_specific: bool | None = None  # True(+2), False(+1 for open)
    contact_complete: bool | None = None  # True(+2), False(+1)

    def calculate_raw_score(self) -> int:
        score = 0
        score += self.intent.score
        score += self.timeline.score
        score += self.financing.score
        score += 2 if self.location_specific else 1
        score += 2 if self.property_specific else 1
        score += 2 if self.contact_complete else 1

        # Budget Scoring (Complex logic)
        if self.budget:
            if self.budget >= 600_000:  # noqa: PLR2004
                score += 3
            elif self.budget >= 300_000:  # noqa: PLR2004
                score += 3
            elif self.budget >= 100_000:  # noqa: PLR2004
                score += 2
            else:
                score += 1
        else:
            # If no budget provided but other intent signals are strong, default to 0
            pass

        return score


class LeadScore(BaseModel):
    """Calculated score and categorization."""

    raw_score: int  # 0-21
    normalized_score: int  # 1-10
    category: LeadCategory
    details: QualificationData
    action_item: str
