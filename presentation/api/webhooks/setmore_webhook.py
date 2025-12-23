from fastapi import APIRouter, Header, HTTPException, Request

from domain.enums import LeadStatus
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhooks/setmore")
async def setmore_webhook(
    request: Request, x_setmore_signature: str = Header(None)
) -> dict[str, str]:
    """
    Receives booking confirmations from Setmore.
    Standardizes the lead status to APPOINTMENT_CONFIRMED.
    """
    # TODO: Verify signature for security if provided by Setmore

    try:
        data = await request.json()
        logger.info("SETMORE_WEBHOOK_RECEIVED", context={"data": data})

        # Extract customer info (Setmore payload varies by version)
        customer = data.get("customer", {})
        phone = customer.get("phone") or data.get("customer_phone")

        if not phone:
            logger.warning("SETMORE_WEBHOOK_MISSING_PHONE")
            return {"status": "ignored", "reason": "missing_phone"}

        db = SupabaseAdapter()
        db.update_lead_status(phone, LeadStatus.SCHEDULED)

        logger.info("LEAD_STATUS_UPDATED_BY_SETMORE", context={"phone": phone})
        return {"status": "success"}

    except Exception as e:
        logger.error("SETMORE_WEBHOOK_FAILED", context={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal Server Error") from None
