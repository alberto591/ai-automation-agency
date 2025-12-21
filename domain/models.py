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
    has_terrace: bool = False
    has_garden: bool = False
    has_parking: bool = False
    has_air_conditioning: bool = False
    has_elevator: bool = False
    condition: str | None = None  # e.g., "Ristrutturato", "Nuova costruzione"
    heating_type: str | None = None  # e.g., "Autonomo", "Centralizzato"
    construction_year: int | None = None
    image_url: str | None = None
    images: list[str] = field(default_factory=list)
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
