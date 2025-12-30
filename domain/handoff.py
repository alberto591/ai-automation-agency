from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class HandoffReason(str, Enum):
    UNCERTAINTY = "UNCERTAINTY"  # Low confidence score
    HIGH_VALUE = "HIGH_VALUE"  # Property value > threshold (e.g. 2M)
    POLICY = "POLICY"  # Policy violation or restriction
    SENTIMENT = "SENTIMENT"  # User frustration or explicit request
    USER_REQUEST = "USER_REQUEST"  # Explicit "talk to human"
    COMPLEXITY = "COMPLEXITY"  # Request too complex for AI


class HandoffRequest(BaseModel):
    """
    Represents a request to transfer a lead to a human agent.
    """

    lead_id: str
    reason: HandoffReason
    priority: str = Field(default="normal", description="urgent, normal, or low")
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Context snapshots
    user_message: str | None = None
    ai_analysis: str | None = None
