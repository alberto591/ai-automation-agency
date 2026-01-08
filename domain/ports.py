from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class DatabasePort(ABC):
    @abstractmethod
    def save_lead(self, lead_data: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def save_message(self, lead_id: str, message_data: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_lead(self, phone: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def get_properties(
        self,
        query: str,
        limit: int = 3,
        use_mock_table: bool = False,
        embedding: list[float] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def update_lead(self, phone: str, data: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def update_lead_status(self, phone: str, status: str) -> None:
        pass

    @abstractmethod
    def get_cached_response(self, embedding: list[float], threshold: float = 0.9) -> str | None:
        pass

    @abstractmethod
    def save_to_cache(self, query: str, embedding: list[float], response: str) -> None:
        pass

    @abstractmethod
    def get_market_stats(self, zone: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def update_message_status(self, sid: str, status: str) -> None:
        pass

    @abstractmethod
    def save_payment_schedule(self, schedule: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_due_payments(self, date_limit: datetime) -> list[dict[str, Any]]:
        """Returns payments due before or on date_limit that haven't been completed."""
        pass

    @abstractmethod
    def get_active_agents(self) -> list[dict[str, Any]]:
        """Returns list of active agents with their zones."""
        pass

    @abstractmethod
    def assign_lead_to_agent(self, lead_id: str, agent_id: str) -> None:
        """Assigns a lead to an agent."""
        pass


class AIPort(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> list[float]:
        pass


class CalendarPort(ABC):
    @abstractmethod
    def create_event(
        self, summary: str, start_time: datetime, end_time: datetime, attendees: list[str]
    ) -> str:
        """Creates a calendar event and returns the event link."""
        pass

    @abstractmethod
    def get_availability(self, staff_id: str, date: str) -> list[str]:
        """Returns a list of available time slots for a specific staff and date."""
        pass


class DocumentPort(ABC):
    @abstractmethod
    def generate_pdf(self, template_name: str, data: dict[str, Any]) -> str:
        """Generates a PDF from a template and returns the local file path."""
        pass


class MessagingPort(ABC):
    @abstractmethod
    def send_message(self, to: str, body: str, media_url: str | None = None) -> str:
        """Sends a message, optionally with a media attachment."""
        pass

    @abstractmethod
    def send_interactive_message(self, to: str, message: Any) -> str:
        """Sends interactive message (Buttons, List, etc.) via InteractiveMessage model."""
        pass


class MarketDataPort(ABC):
    @abstractmethod
    def get_avg_price(self, zone: str, city: str = "") -> int | None:
        pass

    @abstractmethod
    def get_market_insights(self, zone: str, city: str = "") -> dict[str, Any]:
        """Returns structured insights like avg_price, trend, and liquidity."""
        pass


class ScraperPort(ABC):
    @abstractmethod
    def scrape_url(self, url: str) -> dict[str, Any] | None:
        pass


class VoicePort(ABC):
    @abstractmethod
    def get_greeting_twiml(self, webhook_url: str) -> str:
        """Returns TwiML to greet and record user input."""
        pass

    @abstractmethod
    def handle_transcription(self, transcription_text: str, from_phone: str) -> None:
        """Processes the transcribed text as an inbound lead."""
        pass


class EmailPort(ABC):
    @abstractmethod
    def fetch_unread_emails(self, criteria: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Returns list of {subject, body, sender, date, id}"""
        pass

    @abstractmethod
    def mark_as_processed(self, email_id: str) -> None:
        """Marks email as read or moves to processed folder."""
        pass


class ResearchPort(ABC):
    """Real-time web research using Perplexity Labs API."""

    @abstractmethod
    def search(self, query: str, context: str | None = None) -> str:
        """General purpose real-time web research."""
        pass

    @abstractmethod
    def research_legal_compliance(self, topic: str) -> str:
        """Specific research for regulatory updates (e.g., Gazzetta Ufficiale, EU AI Act)."""
        pass

    @abstractmethod
    def find_market_comparables(
        self,
        city: str,
        zone: str,
        property_type: str = "appartamento",
        surface_sqm: int = 100,
        radius_km: float = 2.0,
    ) -> str:
        """Find active live listings to supplement valuation models."""
        pass


class ValidationPort(ABC):
    @abstractmethod
    def log_validation(
        self,
        predicted_value: int,
        actual_value: int,
        metadata: dict[str, Any],
        uncertainty_score: float | None = None,
        lead_id: str | None = None,
        model_version: str = "xgboost_v1",
    ) -> None:
        """Logs a validation event."""
        pass

    @abstractmethod
    def detect_drift(self, zone: str, threshold: float = 0.15) -> bool:
        """Checks for model drift in a zone."""
        pass


class NotificationPort(ABC):
    @abstractmethod
    def notify_agency(self, request: Any) -> bool:
        """
        Notifies the agency of a handoff request.
        Request type is Any to avoid circular imports, but typically HandoffRequest.
        """
        pass


class CachePort(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass
