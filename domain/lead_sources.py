from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LeadSourceType(str, Enum):
    FACEBOOK = "facebook"
    GOOGLE = "google"
    WEBSITE = "website"
    ZAPIER = "zapier"
    MANUAL = "manual"


@dataclass
class ExternalLead:
    source: LeadSourceType
    external_id: str
    data: dict[str, Any]  # The raw payload
    raw_payload: dict[str, Any] | None = None
    form_id: str | None = None
    ad_id: str | None = None
    created_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
