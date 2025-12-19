from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# Ensure lead_manager can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from lead_manager import handle_real_estate_lead
except ImportError:
    # Mocking for when lead_manager is not yet ready or missing dependencies
    def handle_real_estate_lead(phone, name, details):
        return f"Mock Success: Lead {name} processed."


app = FastAPI()

# Simple in-memory rate limiter (for production, use Redis)
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # Max requests
RATE_LIMIT_WINDOW = 60  # Per 60 seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basic rate limiting to prevent abuse"""
    client_ip = request.client.host
    now = datetime.now()
    
    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    
    # Log request
    rate_limit_store[client_ip].append(now)
    
    response = await call_next(request)
    return response

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import re

def validate_phone(phone: str) -> bool:
    """Validates international phone number format (+[country code][number])"""
    # Accepts: +39123456789, +1-555-123-4567, +44 20 7946 0958
    # Rejects: abc123, 123, +1
    pattern = r'^\+[1-9]\d{6,14}$'
    # Remove common separators before validation
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, clean_phone))


class LeadRequest(BaseModel):
    name: str
    agency: str
    phone: str
    properties: str | None = None


@app.post("/api/leads")
async def create_lead(lead: LeadRequest):
    print(f"🔔 New Lead Received: {lead.name} from {lead.agency}")
    
    # Validate phone number
    if not validate_phone(lead.phone):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid phone number format: {lead.phone}. Use international format: +[country code][number]"
        )

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
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks):
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
        from lead_manager import handle_incoming_message, notify_agent_via_email

        response_text = handle_incoming_message(from_number, incoming_msg)
        
        # Send email notification in background (non-blocking)
        background_tasks.add_task(notify_agent_via_email, "WhatsApp Client", incoming_msg, response_text)

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
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to toggle human mode for {req.phone}. Check server logs."
        )


@app.get("/health")
async def health_check():
    return {"status": "online", "service": "Agenzia AI Backend"}


@app.post("/api/leads/resume")
async def resume_ai_control(req: TakeoverRequest):
    """
    Resumes AI control for a specific client.
    """
    from lead_manager import resume_ai_mode

    success = resume_ai_mode(req.phone)
    if success:
        return {
            "status": "success",
            "message": f"AI Resumed for {req.phone}. Bot is back online.",
        }
    else:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to resume AI for {req.phone}. Check server logs."
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
