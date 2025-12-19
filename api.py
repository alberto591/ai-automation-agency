from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
import time

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
RATE_LIMIT_REQUESTS = 100  # Max requests
RATE_LIMIT_WINDOW = 60  # Per 60 seconds

# SECONDARY LIMITER: Phone-based (Protects AI/Twilio budget)
phone_limit_store = defaultdict(list)
MAX_MSG_PER_HOUR = 20 

def check_phone_rate_limit(phone: str):
    """
    Checks if a specific phone number has exceeded the message limit.
    Prevents a single user from draining the AI/Twilio budget.
    """
    now = time.time()
    # Clean old requests (older than 1 hour)
    phone_limit_store[phone] = [t for t in phone_limit_store[phone] if now - t < 3600]
    
    if len(phone_limit_store[phone]) >= MAX_MSG_PER_HOUR:
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded for {phone}. Please wait before sending more messages."
        )
    
    # Log the request
    phone_limit_store[phone].append(now)


from fastapi.responses import JSONResponse

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basic IP-based rate limiting to prevent infrastructure abuse"""
    client_ip = request.client.host
    now = datetime.now()
    
    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Try again later."}
        )
    
    # Log request
    rate_limit_store[client_ip].append(now)
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"🚨 Middleware caught unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_webhook_key(x_webhook_key: str = Header(None)):
    """Security Layer: Verifies the X-Webhook-Key header."""
    # Special case: Twilio might not send headers easily in some configurations, 
    # but for portals it's mandatory.
    EXPECTED_KEY = os.getenv("WEBHOOK_API_KEY")
    if not EXPECTED_KEY:
        # If no key is set, we are in open-dev mode (not recommended for prod)
        return
        
    if x_webhook_key != EXPECTED_KEY:
        print(f"⚠️ Unauthorized Webhook Attempt: {x_webhook_key}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Webhook API Key")


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

    # SECRECY: Phone-based rate limiting
    check_phone_rate_limit(lead.phone)

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


# ---------------------------------------------------------
# PORTAL INTEGRATIONS (Immobiliare.it, Casa.it, Idealista)
# ---------------------------------------------------------

from typing import Optional

class PortalLead(BaseModel):
    """Universal format for portal leads"""
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    property_title: Optional[str] = None
    property_url: Optional[str] = None
    message: Optional[str] = None
    source: str = "unknown"  # immobiliare, casa, idealista


@app.post("/webhooks/portal")
async def portal_webhook(lead: PortalLead, _=Depends(verify_webhook_key)):
    """
    Universal webhook for real estate portals.
    Accepts leads from Immobiliare.it, Casa.it, Idealista, etc.
    """
    print(f"📡 Portal Lead from {lead.source}: {lead.name} - {lead.phone}")
    
    # Validate phone
    if lead.phone and not validate_phone(lead.phone):
        # Try to fix common format issues
        if not lead.phone.startswith("+"):
            lead.phone = "+39" + lead.phone.lstrip("0")
    
    try:
        # Build property context
        property_query = lead.property_title or lead.message or "Generic inquiry"
        customer_name = lead.name or "Cliente Portale"
        
        # Process the lead
        result = handle_real_estate_lead(lead.phone, customer_name, property_query)
        
        return {
            "status": "success",
            "source": lead.source,
            "message": f"Lead {customer_name} processed via AI",
        }
    except Exception as e:
        print(f"❌ Portal webhook error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/webhooks/immobiliare")
async def immobiliare_webhook(request: Request, _=Depends(verify_webhook_key)):
    """
    Specific webhook for Immobiliare.it lead format.
    """
    try:
        data = await request.json()
        
        # Immobiliare.it typical payload structure
        lead = PortalLead(
            name=data.get("contact_name") or data.get("name"),
            phone=data.get("contact_phone") or data.get("phone"),
            email=data.get("contact_email") or data.get("email"),
            property_title=data.get("property_title") or data.get("listing_title"),
            property_url=data.get("property_url") or data.get("listing_url"),
            message=data.get("message") or data.get("inquiry_text"),
            source="immobiliare.it"
        )
        
        return await portal_webhook(lead)
        
    except Exception as e:
        print(f"❌ Immobiliare webhook error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/webhooks/email-parser")
async def email_parser_webhook(request: Request, _=Depends(verify_webhook_key)):
    """
    Receives parsed email data from Make.com/Zapier.
    Use this when portal sends email notifications.
    """
    try:
        data = await request.json()
        
        # Make.com/Zapier sends parsed email data
        lead = PortalLead(
            name=data.get("parsed_name") or data.get("sender_name"),
            phone=data.get("parsed_phone") or data.get("phone"),
            email=data.get("parsed_email") or data.get("sender_email"),
            property_title=data.get("property") or data.get("subject"),
            message=data.get("body") or data.get("email_body"),
            source=data.get("source") or "email"
        )
        
        return await portal_webhook(lead)
        
    except Exception as e:
        print(f"❌ Email parser webhook error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/webhooks/twilio")
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks, x_webhook_key: str = Header(None)):
    """
    The Ears: Receives incoming WhatsApp messages from Twilio.
    """
    # NOTE: Twilio security is usually done via signature validation. 
    # For now, we allow X-Webhook-Key or we can skip for Twilio if needed.
    # We'll make it optional for Twilio to avoid breaking delivery if header isn't set.
    EXPECTED_KEY = os.getenv("WEBHOOK_API_KEY")
    if EXPECTED_KEY and x_webhook_key and x_webhook_key != EXPECTED_KEY:
         raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Twilio sends data as Form Data, not JSON
        form_data = await request.form()
        incoming_msg = form_data.get("Body", "")
        from_number = form_data.get("From", "").replace("whatsapp:", "")

        print(f"📩 New Message from {from_number}: {incoming_msg}")

        # SECRECY: Phone-based rate limiting
        check_phone_rate_limit(from_number)

        # Trigger the "Conversation Loop" in lead_manager
        from lead_manager import handle_incoming_message, notify_agent_via_email

        response_text = handle_incoming_message(from_number, incoming_msg)
        
        # Send email notification in background (non-blocking)
        background_tasks.add_task(notify_agent_via_email, "WhatsApp Client", incoming_msg, response_text)

        return {"status": "replied", "message": response_text}

    except Exception as e:
        print(f"❌ Error webhook: {e}")
        return {"status": "error", "detail": str(e)}


class MessageRequest(BaseModel):
    phone: str
    message: str

@app.post("/api/leads/message")
async def send_outbound_message(req: MessageRequest):
    """
    Agency Dashboard sends a manual message to the client.
    """
    from lead_manager import send_whatsapp_safe, supabase
    
    # 1. Send via Twilio (or Mock)
    sid = send_whatsapp_safe(req.phone, req.message)
    
    if sidebar_error := (sid == None): # Check for failure mechanism in send_whatsapp_safe if implemented
         # For now send_whatsapp_safe returns SID or "queued-mock" or None on error
         pass

    if not sid:
        raise HTTPException(status_code=500, detail="Failed to send message via Twilio")

    # 2. Log to Database (User role)
    # We fetch the current history first to append, or we can use a specific 'append' function if we had one.
    # For simplicity, we'll do a quick fetch-and-update or RPC if available. 
    # Actually, let's just grab, append, and update.
    
    try:
        # Fetch current
        row = supabase.table("lead_conversations").select("messages").eq("customer_phone", req.phone).single().execute()
        current_msgs = row.data.get("messages", []) if row.data else []
        
        # Append User message (Role: assistant? No, if the HUMAN sends it, it's strictly 'assistant' from the client's perspective, 
        # but for the internal logs, we might want to distinguish 'ai' vs 'human'. 
        # Standard schema usually uses 'assistant' for anything sent TO the user.
        # Let's verify schema. Usually: user=lead, assistant=agency(ai/human).
        
        new_msg = {
            "role": "assistant", 
            "content": req.message, 
            "metadata": {"by": "human_agent"} # Mark as human
        }
        current_msgs.append(new_msg)
        
        # Update
        supabase.table("lead_conversations").update({
            "messages": current_msgs,
            "status": "human_mode",
            "updated_at": datetime.now().isoformat()
        }).eq("customer_phone", req.phone).execute()

        return {"status": "sent", "sid": sid}
        
    except Exception as e:
        print(f"❌ Database Log Error: {e}")
        raise HTTPException(status_code=500, detail=f"Message sent but failed to log: {e}")

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
