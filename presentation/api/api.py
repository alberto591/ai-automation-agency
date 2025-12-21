import re
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config.container import container
from config.settings import settings
from domain.errors import BaseAppError
from infrastructure.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Agenzia AI API")

# Middleware / Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_webhook_key(x_webhook_key: str = Header(None)) -> None:
    if settings.WEBHOOK_API_KEY and x_webhook_key != settings.WEBHOOK_API_KEY:
        logger.warning("UNAUTHORIZED_WEBHOOK_ATTEMPT", context={"key": x_webhook_key})
        raise HTTPException(status_code=401, detail="Unauthorized") from None


# DTOs
class LeadRequest(BaseModel):
    name: str = Field(..., min_length=1)
    agency: str
    phone: str
    postcode: str | None = None
    properties: str | None = None


class PhoneRequest(BaseModel):
    phone: str


class ManualMessageRequest(BaseModel):
    phone: str
    message: str


@app.post("/api/leads")
async def create_lead(lead: LeadRequest) -> dict[str, Any]:
    logger.info("RECEIVED_LEAD_REQUEST", context={"name": lead.name, "phone": lead.phone})

    # Simple validation
    if not re.match(r"^\+[1-9]\d{6,14}$", lead.phone.replace(" ", "")):
        raise HTTPException(status_code=400, detail="Invalid phone format")

    try:
        result = container.lead_processor.process_lead(
            phone=lead.phone,
            name=lead.name,
            query=f"Agency: {lead.agency}. Notes: {lead.properties}",
            postcode=lead.postcode,
        )
        return {"status": "success", "ai_response": result}
    except BaseAppError as e:
        logger.error("API_LEAD_PROCESSING_FAILED", context={"error": e.message, "cause": e.cause})
        raise HTTPException(status_code=500, detail=e.message) from e
    except Exception:
        logger.error("INTERNAL_SERVER_ERROR", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") from None


@app.post("/api/leads/takeover")
async def takeover_lead(req: PhoneRequest) -> dict[str, str]:
    try:
        container.lead_processor.takeover(req.phone)
        return {"status": "success", "message": "AI Muted. Human in control."}
    except Exception as e:
        logger.error("TAKEOVER_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to mute AI") from None


@app.post("/api/leads/resume")
async def resume_lead(req: PhoneRequest) -> dict[str, str]:
    try:
        container.lead_processor.resume(req.phone)
        return {"status": "success", "message": "AI Resumed."}
    except Exception as e:
        logger.error("RESUME_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to resume AI") from None


@app.post("/api/leads/message")
async def send_manual_message(req: ManualMessageRequest) -> dict[str, str]:
    try:
        container.lead_processor.send_manual_message(req.phone, req.message)
        return {"status": "success", "message": "Message sent."}
    except Exception as e:
        logger.error("MANUAL_MESSAGE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to send message") from None


@app.get("/api/user/profile")
async def get_user_profile() -> dict[str, Any]:
    return {
        "name": (settings.AGENCY_OWNER_PHONE.split("@")[0] if settings.AGENCY_OWNER_PHONE else "Agency Owner"),
        "email": settings.AGENCY_OWNER_EMAIL or "info@anzevino.ai",
        "phone": settings.AGENCY_OWNER_PHONE or "+39 123 456 7890",
        "agency_name": "Anzevino AI",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "online", "service": "Agenzia AI - Hexagonal"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
