from enum import StrEnum


class LeadStatus(StrEnum):
    ACTIVE = "active"
    QUALIFICATION_IN_PROGRESS = "qualification_in_progress"
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    DISQUALIFIED = "disqualified"
    QUALIFIED = "qualified"
    APPOINTMENT_REQUESTED = "appointment_requested"
    SCHEDULED = "scheduled"
    VIEWED = "viewed"
    CONTRACT_PENDING = "contract_pending"
    CLOSED = "closed"
    HUMAN_MODE = "human_mode"
    ARCHIVED = "archived"
