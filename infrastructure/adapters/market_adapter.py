from domain.ports import MarketDataPort
from infrastructure.logging import get_logger
from infrastructure.market_service import MarketDataService

logger = get_logger(__name__)


class IdealistaMarketAdapter(MarketDataPort):
    def __init__(self) -> None:
        self._service = MarketDataService()

    def get_avg_price(self, zone: str, city: str = "") -> int | None:
        try:
            return self._service.get_avg_price(zone, city)
        except Exception as e:
            logger.error("MARKET_PRICE_FETCH_FAILED", context={"zone": zone, "error": str(e)})
            return None  # Or raise ExternalServiceError
