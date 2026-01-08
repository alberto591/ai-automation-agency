from fastapi import Header, HTTPException

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)


async def verify_webhook_key(x_webhook_key: str = Header(None)) -> None:
    if settings.WEBHOOK_API_KEY and x_webhook_key != settings.WEBHOOK_API_KEY:
        logger.warning("UNAUTHORIZED_WEBHOOK_ATTEMPT", context={"key": x_webhook_key})
        raise HTTPException(status_code=401, detail="Invalid Webhook Key")
