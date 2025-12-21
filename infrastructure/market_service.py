import logging
from typing import Any

import requests

from config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    # Expert Fallbacks for Tuscany (November 2025 Market Trends)
    TUSCANY_EXPERT_DATA = {
        "FIRENZE": 4546,
        "SIENA": 3100,
        "PISA": 2500,
        "LUCCA": 3544,
        "AREZZO": 1524,
        "LIVORNO": 2100,
        "GROSSETO": 2500,
        "PRATO": 2200,
        "PISTOIA": 2100,
        "MASSA": 2400,
        "CARRARA": 1800,
        "FORTE DEI MARMI": 10500,
        "VIAREGGIO": 3400,
        "MONTE ARGENTARIO": 5500,
        "FIGLINE E INCISA VALDARNO": 2400,
        "FIGLINE": 2400,
        "INCISA VALDARNO": 2300,
        "TOSCANA": 2594,
    }

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.RAPIDAPI_KEY
        self.host = "idealista2.p.rapidapi.com"
        self.headers = (
            {"X-RapidAPI-Key": self.api_key, "X-RapidAPI-Host": self.host} if self.api_key else {}
        )

    def get_avg_price(self, zone: str, city: str = "") -> int | None:
        zone_upper = zone.upper()

        # 1. Check Expert Fallbacks
        for t_zone, t_price in self.TUSCANY_EXPERT_DATA.items():
            if t_zone in zone_upper:
                logger.info(f"📍 Expert Data used for {zone}: €{t_price}/mq")
                return t_price

        if not self.api_key:
            logger.warning("⚠️ RAPIDAPI_KEY not found. Skipping live lookup.")
            return None

        # 2. Live API Lookup
        location_id = self._resolve_location(zone)
        return self._fetch_live_price(zone, city, location_id)

    def _resolve_location(self, zone: str) -> str | None:
        try:
            url = f"https://{self.host}/auto-complete"
            params = {"prefix": zone, "country": "it"}
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            if resp.status_code == 200:  # noqa: PLR2004
                locations: list[dict[str, Any]] = resp.json().get("locations", [])
                if locations:
                    return str(locations[0].get("locationId"))
        except Exception as e:
            logger.warning(f"⚠️ Autocomplete failed for {zone}: {e}")
        return None

    def _fetch_live_price(self, zone: str, city: str, location_id: str | None) -> int | None:
        url = f"https://{self.host}/properties/list"
        params = {"operation": "sale", "propertyType": "homes", "country": "it", "maxItems": "20"}
        if location_id:
            params["locationId"] = location_id
        else:
            params["locationName"] = f"{zone}, {city}".strip(", ")

        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            if resp.status_code != 200:  # noqa: PLR2004
                return None

            elements: list[dict[str, Any]] = resp.json().get("elementList", [])
            prices_mq = []
            for p in elements:
                if p.get("isAuction"):
                    continue
                price, size = p.get("price"), p.get("size")
                if price and size and size > 0:
                    val = price / size
                    if 800 < val < 20000:  # noqa: PLR2004
                        prices_mq.append(val)

            if not prices_mq:
                return None
            avg = sum(prices_mq) / len(prices_mq)
            logger.info(f"🌐 Live API Data for {zone}: €{int(avg)}/mq")
            return int(avg)
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            return None


# Helper for backward compatibility
def get_live_market_price(zone: str, city: str = "") -> int | None:
    service = MarketDataService()
    return service.get_avg_price(zone, city)
