from abc import ABC, abstractmethod
from typing import Any


class DatabasePort(ABC):
    @abstractmethod
    def save_lead(self, lead_data: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def get_lead(self, phone: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def get_properties(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def update_lead_status(self, phone: str, status: str) -> None:
        pass


class AIPort(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass


class MessagingPort(ABC):
    @abstractmethod
    def send_message(self, to: str, body: str) -> str:
        pass


class MarketDataPort(ABC):
    @abstractmethod
    def get_avg_price(self, zone: str, city: str = "") -> int | None:
        pass


class ScraperPort(ABC):
    @abstractmethod
    def scrape_url(self, url: str) -> dict[str, Any] | None:
        pass
