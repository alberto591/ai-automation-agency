from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Property:
    title: str
    price: float
    sqm: float
    rooms: int
    bathrooms: int
    floor: int
    energy_class: str
    price_per_mq: float
    zone: str
    city: str
    portal_url: str | None = None
    id: str | None = None


@dataclass
class Lead:
    phone: str
    name: str | None = None
    agency: str | None = None
    postcode: str | None = None
    interest: str | None = None
    score: int = 0
    status: str | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    last_msg: str | None = None
    ai_notes: str | None = None
    updated_at: datetime | None = None
