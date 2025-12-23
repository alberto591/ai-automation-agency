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
        insights = self.get_market_insights(zone, city)
        return insights.get("avg_price_sqm")

    def search_properties(self, zone: str, city: str = "") -> list[dict[str, Any]]:
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY_MISSING")
            return []

        location_id = self._resolve_location(zone)
        # Use locationName if ID not found, handled in _fetch_listings
        return self._fetch_listings(zone, city, location_id)

    def get_market_insights(self, zone: str, city: str = "") -> dict[str, Any]:
        zone_upper = zone.upper()
        expert_price = None

        # 1. Check Expert Fallbacks
        for t_zone, t_price in self.TUSCANY_EXPERT_DATA.items():
            if t_zone in zone_upper:
                expert_price = t_price
                break

        # 2. Try Live Lookup
        live_price = None
        if self.api_key:
            location_id = self._resolve_location(zone)
            live_price = self._fetch_live_price(zone, city, location_id)

        # 3. Consolidate Insights
        final_price = live_price or expert_price

        # Trend Inference: If live > expert + 5% -> Rising, if live < expert - 5% -> Falling
        trend = "STABLE"
        if live_price and expert_price:
            diff = (live_price - expert_price) / expert_price
            if diff > 0.05:
                trend = "RISING"
            elif diff < -0.05:
                trend = "FALLING"

        return {
            "avg_price_sqm": final_price,
            "trend": trend,
            "area": zone,
            "liquidity": "MEDIUM",  # Placeholder for now
            "is_live": live_price is not None,
        }

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

    def _fetch_listings(
        self, zone: str, city: str, location_id: str | None
    ) -> list[dict[str, Any]]:
        url = f"https://{self.host}/properties/list"
        params = {
            "operation": "sale",
            "propertyType": "homes",
            "country": "it",
            # Request specific fields if API supports it, otherwise parsing JSON
            "maxItems": "40",  # Increase for production data
            "sort": "date",  # Get newest first
        }
        if location_id:
            params["locationId"] = location_id
        else:
            params["locationName"] = f"{zone}, {city}".strip(", ")

        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error(f"API_FAIL {resp.status_code}: {resp.text}")
                return []

            return list(resp.json().get("elementList", []))
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            return []

    def _fetch_live_price(self, zone: str, city: str, location_id: str | None) -> int | None:
        elements = self._fetch_listings(zone, city, location_id)
        prices_mq = []
        for p in elements:
            if p.get("isAuction"):
                continue
            price, size = p.get("price"), p.get("size")
            if price and size and size > 0:
                val = price / size
                if 800 < val < 20000:
                    prices_mq.append(val)

        if not prices_mq:
            return None
        avg = sum(prices_mq) / len(prices_mq)
        logger.info(f"🌐 Live API Data for {zone}: €{int(avg)}/mq")
        return int(avg)


# Helper for backward compatibility
def get_live_market_price(zone: str, city: str = "") -> int | None:
    service = MarketDataService()
    return service.get_avg_price(zone, city)
