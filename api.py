from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Ensure lead_manager can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from lead_manager import handle_real_estate_lead
except ImportError:
    # Mocking for when lead_manager is not yet ready or missing dependencies
    def handle_real_estate_lead(phone, name, details):
        return f"Mock Success: Lead {name} processed."


app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadRequest(BaseModel):
    name: str
    agency: str
    phone: str
    properties: str | None = None


@app.post("/api/leads")
async def create_lead(lead: LeadRequest):
    print(f"🔔 New Lead Received: {lead.name} from {lead.agency}")

    try:
        # Trigger the AI Logic (The Heart)
        # We pass the agency name/properties as context
        context = f"Agenzia: {lead.agency}. Gestione: {lead.properties}"
        result = handle_real_estate_lead(lead.phone, lead.name, context)

        return {
            "status": "success",
            "message": "Lead processed successfully",
            "ai_response": result,
        }
    except Exception as e:
        print(f"❌ Error processing lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    """
    The Ears: Receives incoming WhatsApp messages from Twilio.
    """
    try:
        # Twilio sends data as Form Data, not JSON
        form_data = await request.form()
        incoming_msg = form_data.get("Body", "")
        from_number = form_data.get("From", "").replace("whatsapp:", "")

        print(f"📩 New Message from {from_number}: {incoming_msg}")

        # Trigger the "Conversation Loop" in lead_manager
        from lead_manager import handle_incoming_message

        response_text = handle_incoming_message(from_number, incoming_msg)

        return {"status": "replied", "message": response_text}

    except Exception as e:
        print(f"❌ Error webhook: {e}")
        return {"status": "error", "detail": str(e)}


class TakeoverRequest(BaseModel):
    phone: str


@app.post("/api/leads/takeover")
async def monitor_control_phase(req: TakeoverRequest):
    """
    The Control: Allows the human agent to stop the AI.
    """
    from lead_manager import toggle_human_mode

    success = toggle_human_mode(req.phone)
    if success:
        return {
            "status": "success",
            "message": f"AI Muted for {req.phone}. Human Control Active.",
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to toggle human mode")


@app.get("/health")
async def health_check():
    return {"status": "online", "service": "Agenzia AI Backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
