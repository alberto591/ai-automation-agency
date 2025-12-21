from typing import Any

from domain.ports import ScraperPort
from infrastructure.logging import get_logger
from infrastructure.market_scraper import ImmobiliareScraper

logger = get_logger(__name__)


class ImmobiliareScraperAdapter(ScraperPort):
    def __init__(self) -> None:
        self._service = ImmobiliareScraper()

    def scrape_url(self, url: str) -> dict[str, Any] | None:
        try:
            return self._service.scrape(url)
        except Exception as e:
            logger.error("SCRAPE_FAILED", context={"url": url, "error": str(e)})
            return None
