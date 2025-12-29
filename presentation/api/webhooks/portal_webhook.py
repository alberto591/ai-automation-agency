from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field

from config.container import container
from config.settings import settings
from domain.services.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/portal", tags=["Webhooks"])


class PortalLead(BaseModel):
    """
    Standardized payload for leads coming from portals (via Make/Zapier).
    """

    portal_name: str = Field(..., description="Source portal (e.g., 'idealista', 'immobiliare')")
    lead_name: str
    lead_phone: str
    lead_email: EmailStr | None = None
    message: str | None = None
    property_ref: str | None = None
    property_url: str | None = None
    listing_price: int | None = None


@router.post("")
async def receive_portal_lead(
    lead: PortalLead,
    background_tasks: BackgroundTasks,
    x_webhook_key: str | None = Header(None, alias="X-Webhook-Key"),
) -> dict[str, str]:
    """
    Endpoint to receive leads from real estate portals.
    Expected to be called by middleware (Make.com, Zapier, n8n).
    """
    # 1. Security Check
    if settings.WEBHOOK_API_KEY and x_webhook_key != settings.WEBHOOK_API_KEY:
        logger.warning("UNAUTHORIZED_PORTAL_WEBHOOK", context={"key": x_webhook_key})
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(
        "PORTAL_LEAD_RECEIVED",
        context={
            "source": lead.portal_name,
            "name": lead.lead_name,
            "phone": lead.lead_phone,
            "property": lead.property_ref,
        },
    )

    # 2. Process Lead in Background
    # We construct a context query combining the message and property info
    query_context = f"Source: {lead.portal_name}. "
    if lead.property_ref:
        query_context += f"Ref: {lead.property_ref}. "
    if lead.listing_price:
        query_context += f"Price: €{lead.listing_price}. "
    if lead.message:
        query_context += f"Message: {lead.message}"

    # Use the container to process the lead
    # process_lead handles:
    # - DB creation/update
    # - AI Conversation start (if phone valid)
    # - Google Sheets Sync (via finalize_node)

    background_tasks.add_task(
        container.lead_processor.process_lead,
        phone=lead.lead_phone,
        name=lead.lead_name,
        query=query_context,
        postcode=None,
    )

    return {"status": "received", "message": "Lead queued for processing"}
