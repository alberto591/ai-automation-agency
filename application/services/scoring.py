import math

from domain.qualification import (
    FinancingStatus,
    Intent,
    LeadCategory,
    LeadScore,
    QualificationData,
    Timeline,
)


class ScoringService:
    """
    Implements the lead scoring algorithm defined in docs/features/lead_qualification.md.
    Max Score: 18 points (normalized to 1-10)
    """

    @staticmethod
    def _score_intent(intent: Intent) -> int:
        match intent:
            case Intent.BUY:
                return 3
            case Intent.SELL:
                return 2
            case Intent.RENT:
                return 1
            case _:
                return 0

    @staticmethod
    def _score_timeline(timeline: Timeline) -> int:
        match timeline:
            case Timeline.URGENT:
                return 3
            case Timeline.MEDIUM:
                return 2
            case Timeline.LONG:
                return 1
            case _:
                return 0

    @staticmethod
    def _score_budget(budget: float | None) -> int:
        if not budget:
            return 0
        if budget >= 300_000:
            return 3
        if budget >= 100_000:
            return 2
        return 1

    @staticmethod
    def _score_financing(financing: FinancingStatus) -> int:
        match financing:
            case FinancingStatus.APPROVED:
                return 3
            case FinancingStatus.PROCESSING:
                return 2
            case FinancingStatus.TODO:
                return 1
            case _:
                return 0

    @classmethod
    def calculate_score(cls, data: QualificationData) -> LeadScore:
        score = 0
        score += cls._score_intent(data.intent)
        score += cls._score_timeline(data.timeline)
        score += cls._score_budget(data.budget)
        score += cls._score_financing(data.financing)
        score += 2 if data.location_specific else 0
        score += 2 if data.property_specific else 0
        # Contact info (+2) baseline (+1 implied)
        score += 2 if data.has_contact_info else 1

        # Normalize score (Max 18)
        # min(10, ceil(raw/18 * 10))
        normalized = min(10, math.ceil((score / 18) * 10))

        # Categorize
        category = LeadCategory.COLD
        action = "Nurture sequence"

        if normalized >= 9:
            category = LeadCategory.HOT
            action = "Call within 5 minutes"
        elif normalized >= 6:
            category = LeadCategory.WARM
            action = "Email + SMS nurture"

        # Disqualification: Budget too low for Buying
        if data.budget and data.budget < 50_000 and data.intent == Intent.BUY:
            category = LeadCategory.DISQUALIFIED
            action = "Disqualified (Budget too low)"

        return LeadScore(
            raw_score=score,
            normalized_score=normalized,
            category=category,
            details=data,
            action_item=action,
        )
