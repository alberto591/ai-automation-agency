from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class DatabasePort(ABC):
    @abstractmethod
    def save_lead(self, lead_data: dict[str, Any]) -> Any:
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
