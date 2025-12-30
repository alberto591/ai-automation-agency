from typing import TypedDict

from domain.qualification import (
    FinancingStatus,
    Intent,
    LeadCategory,
    LeadScore,
    QualificationData,
    Timeline,
)


class QuestionTemplate(TypedDict):
    step_id: str
    text: str
    field_name: str


class LeadScoringService:
    """
    Manages the 7-Step Lead Qualification Flow and Scoring.
    Implements strict Italian scripting and 0-21 point scoring logic.
    """

    QUESTIONS: list[QuestionTemplate] = [
        {
            "step_id": "q1_intent",
            "text": "Cerchi di comprare, vendere, o solo informarti?",
            "field_name": "intent",
        },
        {
            "step_id": "q2_timeline",
            "text": "Quando hai bisogno di una casa?",
            "field_name": "timeline",
        },
        {
            "step_id": "q3_budget",
            "text": "Qual è il tuo budget massimo approssimativo (in €)?",
            "field_name": "budget",
        },
        {
            "step_id": "q4_financing",
            "text": "Hai già un'ipoteca approvata o disponibilità liquida?",
            "field_name": "financing",
        },
        {
            "step_id": "q5_location",
            "text": "In quale zona preferiresti (es. Firenze Centro, Colline, ecc.)?",
            "field_name": "location_specific",
        },
        {
            "step_id": "q6_property_type",
            "text": "Che tipo di proprietà cerchi? (Appartamento, Villa, ecc.)",
            "field_name": "property_specific",
        },
        {
            "step_id": "q7_contact",
            "text": "Per poterti assegnare un agente dedicato, mi lasci il tuo Nome e Cognome?",
            "field_name": "contact_complete",
        },
    ]

    @staticmethod
    def calculate_score(data: QualificationData) -> LeadScore:
        """
        Calculates the score based on the 0-21 point system.
        Normalizes to 1-10.
        Categorizes as HOT/WARM/COLD.
        """
        raw_score = data.calculate_raw_score()

        # Normalize to 1-10
        # Max score is 21.
        # normalized = round((raw / 21) * 10)
        normalized_score = min(10, round((raw_score / 21) * 10))
        # Ensure minimum 1 if userengaged
        normalized_score = max(1, normalized_score)

        category = LeadCategory.COLD
        action = "Automated drip campaign"

        if normalized_score >= 9:
            category = LeadCategory.HOT
            action = "Assign to senior agent immediately (Call < 5 min)"
        elif normalized_score >= 6:
            category = LeadCategory.WARM
            action = "Email + SMS nurture sequence"

        # KILL SWITCH
        # IF Budget < €50k AND Timeline = "Not sure" -> DISQUALIFIED
        if (
            data.budget
            and data.budget < 50_000
            and data.timeline == Timeline.UNKNOWN
            and data.intent == Intent.BUY
        ):
            category = LeadCategory.DISQUALIFIED
            action = "Do not contact (Budget/Timeline mismatch)"

        return LeadScore(
            raw_score=raw_score,
            normalized_score=normalized_score,
            category=category,
            details=data,
            action_item=action,
        )

    @classmethod
    def get_next_question(cls, data: QualificationData) -> QuestionTemplate | None:  # noqa: PLR0911
        """
        Determines the next question to ask based on missing data fields.
        Returns None if qualification is complete.
        """
        # Q1: Intent
        if data.intent == Intent.UNKNOWN:
            return cls.QUESTIONS[0]

        # Optimization: If intent is INFO, we might skip some Qs or have a different flow.
        # But for now, we follow the standard flow for BUY/SELL/RENT.
        if data.intent == Intent.INFO:
            # Maybe skip to contact? For now, stick to flow but be lenient.
            pass

        # Q2: Timeline
        if data.timeline == Timeline.UNKNOWN:
            return cls.QUESTIONS[1]

        # Q3: Budget
        if data.budget is None:
            return cls.QUESTIONS[2]

        # Q4: Financing
        if data.financing == FinancingStatus.UNKNOWN:
            return cls.QUESTIONS[3]

        # Q5: Location
        if data.location_specific is None:
            return cls.QUESTIONS[4]

        # Q6: Property Type
        if data.property_specific is None:
            return cls.QUESTIONS[5]

        # Q7: Contact
        if data.contact_complete is None:
            return cls.QUESTIONS[6]

        return None

    @classmethod
    def get_question_by_step(cls, step_index: int) -> QuestionTemplate | None:
        """Returns the question for the given 0-indexed step."""
        if 0 <= step_index < len(cls.QUESTIONS):
            return cls.QUESTIONS[step_index]
        return None
