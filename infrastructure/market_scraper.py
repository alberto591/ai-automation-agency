import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

import requests
from bs4 import BeautifulSoup
from supabase import Client, create_client

from config import settings

logger = logging.getLogger(__name__)


class Scraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> dict[str, Any] | None:
        pass


class ImmobiliareScraper(Scraper):
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def scrape(self, url: str) -> dict[str, Any] | None:
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=10)
            if resp.status_code != 200:  # noqa: PLR2004
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            data = {
                "portal_url": url,
                "title": self._find_text(soup, "h1", "nd-title") or "Appartamento",
                "price": self._extract_numeric(
                    soup, ["div", "li"], "nd-list__item nd-list__item--main nd-list__item--price"
                ),
                "sqm": self._extract_attribute(soup, "li", "aria_label", "superficie"),
                "rooms": int(self._extract_attribute(soup, "li", "aria_label", "locali") or 0),
                "bathrooms": int(self._extract_attribute(soup, "li", "aria_label", "bagni") or 0),
                "floor": self._parse_floor(
                    self._extract_attribute_text(soup, "li", "aria_label", "piano")
                ),
                "energy_class": self._find_text(
                    soup, "span", "nd-list__item nd-list__item--main nd-list__item--energy"
                )
                or "N/A",
                "zone": self._find_text(soup, "span", "nd-title__sub-title") or "Milano",
                "city": "Milano",
            }
            p_val = data.get("price")
            s_val = data.get("sqm")
            price = float(p_val) if isinstance(p_val, (int, float, str)) else 0.0
            sqm = float(s_val) if isinstance(s_val, (int, float, str)) else 0.0
            data["price_per_mq"] = round(price / sqm, 2) if sqm > 0 else 0.0
            return data
        except Exception as e:
            logger.error(f"Scraper Error: {e}")
            return None

    def _find_text(self, soup: BeautifulSoup, tag: str, cls: str) -> str | None:
        el = soup.find(tag, class_=cls)
        return str(el.get_text().strip()) if el else None

    def _extract_numeric(self, soup: BeautifulSoup, tags: list[str], cls: str) -> float:
        for tag in tags:
            el = soup.find(tag, class_=cls)
            if el:
                return float(re.sub(r"[^\d]", "", str(el.get_text())))
        return 0.0

    def _extract_attribute(self, soup: BeautifulSoup, tag: str, attr: str, value: str) -> float:
        el = soup.find(tag, attrs={attr: value})
        if el:
            return float(re.sub(r"[^\d]", "", str(el.get_text())))
        return 0.0

    def _extract_attribute_text(self, soup: BeautifulSoup, tag: str, attr: str, value: str) -> str:
        el = soup.find(tag, attrs={attr: value})
        return str(el.get_text().strip()) if el else ""

    def _parse_floor(self, text: str) -> int:
        if not text:
            return 0
        if "T" in text or "terra" in text.lower():
            return 0
        match = re.search(r"\d+", text)
        return int(match.group()) if match else 0


class MarketDataManager:
    def __init__(self, db_client: Client | None = None):
        self.db = db_client or create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def save_to_db(self, data: dict[str, Any]) -> Any:
        try:
            return self.db.table("market_data").upsert(data, on_conflict="portal_url").execute()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            return None


# Backward compatibility
def scrape_immobiliare(url: str) -> dict[str, Any] | None:
    return ImmobiliareScraper().scrape(url)


def save_to_market_data(data: dict[str, Any]) -> Any:
    return MarketDataManager().save_to_db(data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        res = scrape_immobiliare(url)
        if res:
            print(json.dumps(res, indent=2))
            save_to_market_data(res)
    else:
        print("Usage: python3 market_scraper.py <URL>")
