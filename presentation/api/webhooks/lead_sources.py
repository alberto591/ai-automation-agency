import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Query, Request

from config.container import container
from config.settings import settings
from infrastructure.logging import get_logger
from presentation.api.security import verify_webhook_key

logger = get_logger(__name__)

router = APIRouter()


@router.get("/webhooks/facebook")
async def verify_facebook_webhook(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
) -> int:
    """
    Verifies the Facebook Webhook handshake.
    """
    verify_token = settings.FACEBOOK_VERIFY_TOKEN or "my_secure_token"

    if mode == "subscribe" and token == verify_token:
        logger.info("FACEBOOK_WEBHOOK_VERIFIED")
        return int(challenge)

    logger.warning("FACEBOOK_VERIFICATION_FAILED", context={"mode": mode, "token": token})
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhooks/facebook")
async def facebook_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
) -> str:
    """
    Receives Lead Ads notifications.
    """
    body_bytes = await request.body()

    # Verify Signature if secret is set
    if settings.FACEBOOK_APP_SECRET and x_hub_signature_256:
        expected = hmac.new(
            settings.FACEBOOK_APP_SECRET.encode(), msg=body_bytes, digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(f"sha256={expected}", x_hub_signature_256):
            logger.warning("FACEBOOK_SIGNATURE_INVALID")
            raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    container.lead_ingestion.process_facebook_webhook(payload)

    return "OK"


@router.post("/webhooks/generic")
async def generic_webhook(
    request: Request,
    x_webhook_key: str | None = Header(None),
) -> dict[str, str]:
    """
    Receives generic JSON lead payloads (e.g. Zapier, Typeform).
    Requires X-Webhook-Key header.
    """
    if not x_webhook_key:
        logger.warning("GENERIC_WEBHOOK_KEY_MISSING")
        raise HTTPException(status_code=401, detail="Missing X-Webhook-Key")
    await verify_webhook_key(x_webhook_key)

    payload = await request.json()
    source = payload.get("source", "generic")

    lead_id = container.lead_ingestion.process_generic_payload(payload, source=source)

    return {"status": "success", "lead_id": lead_id}
