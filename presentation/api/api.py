from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config.container import container
from config.settings import settings
from domain.enums import LeadStatus
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


@app.post("/api/webhooks/twilio")
async def twilio_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
) -> str:
    """
    Receives webhooks from Twilio for incoming WhatsApp messages.
    """
    logger.info("WEBHOOK_RECEIVED", context={"from": From, "body": Body})
    
    # Process in background to ensure 200 OK is returned to Twilio immediately
    background_tasks.add_task(
        container.lead_processor.process_incoming_message,
        phone=From,
        text=Body
    )
    
    return "OK"


@app.post("/api/leads/message")
async def send_manual_message(req: ManualMessageRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    try:
        # 1. Send message immediately (fast)
        container.lead_processor.send_manual_message(req.phone, req.message, skip_history=True)
        
        # 2. Schedule history update in background (slower DB op)
        background_tasks.add_task(
            container.lead_processor.add_message_history, 
            req.phone, 
            "assistant", 
            req.message, 
            metadata={"by": "human_agent"}
        )
        
        return {"status": "success", "message": "Message queued."}
    except Exception as e:
        logger.error("MANUAL_MESSAGE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to send message") from None


class LeadUpdate(BaseModel):
    phone: str
    name: str | None = None
    budget: int | None = None
    zones: list[str] | None = None
    status: str | None = None
    journey_state: str | None = None
    scheduled_at: str | None = None # Receive as ISO string


@app.patch("/api/leads")
async def update_lead(req: LeadUpdate) -> dict[str, str]:
    try:
        # Use lead_processor to update domain record
        container.lead_processor.update_lead_details(
            phone=req.phone,
            name=req.name,
            budget=req.budget,
            zones=req.zones,
            status=req.status,
            journey_state=req.journey_state,
            scheduled_at=req.scheduled_at
        )
        return {"status": "success", "message": "Lead updated."}
    except Exception as e:
        logger.error("LEAD_UPDATE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to update lead") from None


class ScheduleRequest(BaseModel):
    phone: str
    start_time: str # ISO string


@app.post("/api/leads/schedule")
async def schedule_viewing(req: ScheduleRequest) -> dict[str, str]:
    try:
        dt = datetime.fromisoformat(req.start_time.replace("Z", "+00:00"))
        container.journey.transition_to(
            req.phone, 
            LeadStatus.SCHEDULED, 
            context={"start_time": dt}
        )
        return {"status": "success", "message": "Viewing scheduled."}
    except Exception as e:
        logger.error("SCHEDULE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to schedule viewing") from None


class ContractRequest(BaseModel):
    phone: str
    offered_price: int


@app.post("/api/leads/generate-contract")
async def generate_contract(req: ContractRequest) -> dict[str, str]:
    try:
        container.journey.transition_to(
            req.phone, 
            LeadStatus.CONTRACT_PENDING, 
            context={"offered_price": req.offered_price}
        )
        return {"status": "success", "message": "Contract generation triggered."}
    except Exception as e:
        logger.error("CONTRACT_GEN_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to generate contract") from None


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
