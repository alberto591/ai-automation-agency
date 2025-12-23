from typing import Any

from domain.ports import MarketDataPort
from infrastructure.logging import get_logger
from infrastructure.market_service import MarketDataService

logger = get_logger(__name__)


class IdealistaMarketAdapter(MarketDataPort):
    def __init__(self) -> None:
        self._service = MarketDataService()

    def get_avg_price(self, zone: str, city: str = "") -> int | None:
        return self._service.get_avg_price(zone, city)

    def get_market_insights(self, zone: str, city: str = "") -> dict[str, Any]:
        try:
            return self._service.get_market_insights(zone, city)
        except Exception as e:
            logger.error("MARKET_INSIGHTS_FETCH_FAILED", context={"zone": zone, "error": str(e)})
            return {"avg_price_sqm": None, "trend": "STABLE", "area": zone}
