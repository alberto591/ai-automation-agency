import os
import logging
from dotenv import load_dotenv
from supabase import create_client
from mistralai import Mistral
from twilio.rest import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
# Initialize everything
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Initialize Twilio client (credentials loaded from env)
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))


def get_property_details(property_name):
    # This query searches your Supabase 'properties' table
    response = (
        supabase.table("properties")
        .select("*")
        .ilike("title", f"%{property_name}%")
        .execute()
    )

    if response.data:
        return response.data[0]  # Return the first match found
    return None


def send_ai_whatsapp(customer_phone, customer_name, interest):
    # 1. AI Generates the message
    prompt = f"Scrivi un messaggio WhatsApp breve in italiano per {customer_name} riguardo a: {interest}."
    ai_response = mistral.chat.complete(
        model="mistral-small-latest", messages=[{"role": "user", "content": prompt}]
    )
    italian_text = ai_response.choices[0].message.content

    # 2. Twilio sends the message
    message = twilio_client.messages.create(
        body=italian_text,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=f"whatsapp:{customer_phone}",
    )
    return message.sid


# ---------------------------------------------------------
# LEAD SCORING SYSTEM
# ---------------------------------------------------------

SCORING_SIGNALS = {
    # High Intent Signals (+20-30 points)
    "visita": 30,
    "visitare": 30,
    "vedere": 25,
    "appuntamento": 30,
    "urgente": 25,
    "subito": 20,
    "oggi": 20,
    "domani": 15,
    
    # Budget Signals (+15-20 points)
    "budget": 20,
    "contanti": 20,
    "mutuo": 15,
    "finanziamento": 15,
    
    # Specific Interest (+10-15 points)
    "camera": 10,
    "bagno": 10,
    "terrazza": 15,
    "giardino": 15,
    "garage": 10,
    "piscina": 15,
    
    # Negotiation (neutral - AI handles but owner notified)
    "trattabile": 5,
    "sconto": 5,
}

def calculate_lead_score(message_text: str) -> int:
    """
    Calculates a lead score (0-100) based on intent signals in the message.
    Higher score = more likely to convert.
    """
    score = 0
    message_lower = message_text.lower()
    
    for signal, points in SCORING_SIGNALS.items():
        if signal in message_lower:
            score += points
    
    # Cap at 100
    return min(score, 100)


def save_lead_to_dashboard(customer_name, customer_phone, last_msg, ai_notes, lead_score=0):
    # This sends the data directly to your Supabase table
    data = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "last_message": last_msg,
        "ai_summary": ai_notes,
        "status": "New",
        # Note: lead_score column needs to be added to Supabase table
        # For now, we include it in ai_summary if > 50
    }
    
    # Add score indicator to summary if hot lead
    if lead_score >= 50:
        data["ai_summary"] = f"🔥 HOT LEAD (Score: {lead_score}) - {ai_notes}"
    elif lead_score >= 30:
        data["ai_summary"] = f"⭐ Warm Lead (Score: {lead_score}) - {ai_notes}"

    # Execute the insert
    try:
        supabase.table("lead_conversations").insert(data).execute()
        logger.info(f"Lead {customer_name} saved to Dashboard (Score: {lead_score})")
    except Exception as e:
        logger.error(f"Error saving lead: {e}")


def handle_real_estate_lead(customer_phone, customer_name, property_query):
    # 1. Search the database first
    property_info = get_property_details(property_query)

    if property_info:
        # Construct a Rich Data Context
        details = (
            f"TITOLO: {property_info.get('title', 'N/A')}\n"
            f"PREZZO: €{property_info.get('price', 0):,}\n"
            f"DESCRIZIONE: {property_info.get('description', '')}\n"
            f"CARATTERISTICHE: {property_info.get('features', '')}\n"
            f"ZONA: {property_info.get('location', '')}"
        )
    else:
        details = (
            "Non ho trovato l'immobile specifico, ma offri una consulenza generale."
        )

    # 2. Tell the AI the facts
    prompt = f"""
    Sei "Anzevino AI", l'assistente virtuale d'élite dell'agenzia immobiliare.
    Parla in modo professionale, persuasivo ma succinto (stile WhatsApp). Non usare mai "Saluti" o firme lunghe.
    
    CLIENTE: {customer_name}
    RICHIESTA: {property_query}
    
    DATI UFFICIALI DAL DATABASE:
    {details}
    
    OBIETTIVO:
    1. Conferma che l'immobile è perfetto per loro citando 1-2 dettagli specifici (es. la terrazza o la zona).
    2. Crea urgenza (es. "È molto richiesto").
    3. Chiudi con una Call to Action chiara: "Vuoi vedere le foto?" o "Quando puoi passare per una visita?".
    """

    ai_response = mistral.chat.complete(
        model="mistral-small-latest", messages=[{"role": "user", "content": prompt}]
    )

    # 3. Send via WhatsApp
    message_text = ai_response.choices[0].message.content
    try:
        twilio_client.messages.create(
            body=message_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{customer_phone}",
        )
    except Exception as e:
        logger.warning(f"Twilio Send Error: {e}")
        # Proceed to save to dashboard anyway logic is sound
        message_text += " [Simulated Send]"

    # 4. Save to Dashboard
    ai_notes = f"Interessato a {property_query}. Proposta inviata con successo."
    save_lead_to_dashboard(customer_name, customer_phone, message_text, ai_notes)

    return "Messaggio inviato con dati reali!"


if __name__ == "__main__":
    # Tests are now in tests/ directory - run: pytest tests/
    pass


def get_chat_history(customer_phone):
    """
    Retrieves the last 5 messages for this user to build context.
    """
    try:
        # Fetch last 5 interactions (only fields we need)
        response = (
            supabase.table("lead_conversations")
            .select("last_message,ai_summary,created_at")
            .eq("customer_phone", customer_phone)
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )

        # Reverse to chronological order
        history = response.data[::-1] if response.data else []

        # Format for AI
        context_string = ""
        for row in history:
            # We assume 'last_message' is User and 'ai_summary'/response is AI
            # Ideally database would have 'role' column, but adapting to current schema:
            if row.get("last_message"):
                context_string += f"Cliente: {row['last_message']}\n"
            if row.get("ai_summary"):  # storing full AI text here for now
                context_string += f"Anzevino AI: {row['ai_summary']}\n"

        return context_string
    except Exception as e:
        print(f"⚠️ Error fetching history: {e}")
        return ""


def toggle_human_mode(customer_phone):
    """
    Activates Human Takeover by logging a special status event.
    """
    try:
        data = {
            "customer_name": "System",
            "customer_phone": customer_phone,
            "last_message": "[SYSTEM] Human Takeover Activated",
            "ai_summary": "AI Stopped by Agent",
            "status": "TAKEOVER",
        }
        supabase.table("lead_conversations").insert(data).execute()
        logger.info(f"Human takeover activated for {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Error setting human mode: {e}")
        return False


def resume_ai_mode(customer_phone):
    """
    Resumes AI control by logging a RESUMED status event.
    """
    try:
        data = {
            "customer_name": "System",
            "customer_phone": customer_phone,
            "last_message": "[SYSTEM] AI Control Resumed",
            "ai_summary": "Human released control back to AI",
            "status": "RESUMED",
        }
        supabase.table("lead_conversations").insert(data).execute()
        logger.info(f"AI control resumed for {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Error resuming AI mode: {e}")
        return False


# Auto-expire takeover after this many hours
TAKEOVER_EXPIRY_HOURS = int(os.getenv("TAKEOVER_EXPIRY_HOURS", "24"))


def check_if_human_mode(customer_phone):
    """
    Checks if the AI should be muted.
    Auto-expires after TAKEOVER_EXPIRY_HOURS (default 24h).
    """
    from datetime import datetime, timedelta, timezone
    
    try:
        # Get the VERY LAST interaction with status and timestamp
        response = (
            supabase.table("lead_conversations")
            .select("status,created_at")
            .eq("customer_phone", customer_phone)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return False
            
        last_record = response.data[0]
        
        # If status is RESUMED, AI is active
        if last_record["status"] == "RESUMED":
            return False
            
        # If status is TAKEOVER, check expiry
        if last_record["status"] == "TAKEOVER":
            # Parse timestamp (Supabase returns ISO format)
            created_str = last_record.get("created_at", "")
            if created_str:
                # Handle various timestamp formats
                try:
                    created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    expiry_time = created_at + timedelta(hours=TAKEOVER_EXPIRY_HOURS)
                    
                    if datetime.now(timezone.utc) > expiry_time:
                        logger.info(f"Takeover expired for {customer_phone}, auto-resuming AI")
                        return False  # Expired, AI can respond
                except Exception:
                    pass  # If parsing fails, assume not expired
                    
            return True  # Still in takeover mode
            
        return False
        
    except Exception as e:
        logger.error(f"Error checking human mode: {e}")
        return False


# ---------------------------------------------------------
# STRATEGY: INVISIBLE LOGIC & ALERTS (Tiered Keywords)
# ---------------------------------------------------------

from thefuzz import fuzz

# Tier 1: IMMEDIATE TAKEOVER - Client explicitly wants human
TIER1_TAKEOVER_KEYWORDS = ["umano", "staff", "human", "agent", "manager", "parlare con", "persona reale"]

# Tier 2: ALERT ONLY - Sensitive topic, but AI can still respond
TIER2_ALERT_KEYWORDS = ["trattabile", "negoziare", "sconto", "ribasso", "offerta"]

# Synonyms map (common alternative phrasings)
KEYWORD_SYNONYMS = {
    "umano": ["umani", "persona", "persone", "qualcuno"],
    "trattabile": ["trattabili", "negoziabile"],
    "sconto": ["sconti", "riduzione", "ribassare"],
    "visita": ["visite", "vedere", "guardare"],
    "appuntamento": ["appuntamenti", "incontro", "meeting"],
}

def fuzzy_keyword_match(text: str, keywords: list, threshold: int = 80) -> bool:
    """
    Checks if any keyword matches the text using fuzzy matching.
    Handles typos like "umnao" -> "umano", "tratabile" -> "trattabile"
    """
    text_lower = text.lower()
    
    # Expand keywords with synonyms
    expanded_keywords = set(keywords)
    for kw in keywords:
        if kw in KEYWORD_SYNONYMS:
            expanded_keywords.update(KEYWORD_SYNONYMS[kw])
    
    # Check each word in the text
    words = text_lower.split()
    for word in words:
        for keyword in expanded_keywords:
            # Exact match first (fast path)
            if keyword in text_lower:
                return True
            # Fuzzy match for typos
            if len(word) >= 4 and fuzz.ratio(word, keyword) >= threshold:
                logger.debug(f"Fuzzy match: '{word}' ~ '{keyword}' (score: {fuzz.ratio(word, keyword)})")
                return True
    
    return False

# Tier 3: INFORMATIONAL - AI handles these normally (no special action)
# Examples: "prezzo", "costo", "quanto" - These are normal questions

AGENCY_OWNER_PHONE = os.getenv("AGENCY_OWNER_PHONE", "+39000000000")  # Set this in .env

def notify_owner_urgent(customer_phone, message_text):
    """Sends an urgent WhatsApp to the Boss."""
    try:
        twilio_client.messages.create(
            body=f"⚠️ URGENT: Lead {customer_phone} asking for human!\nMsg: '{message_text}'\nAI Paused.",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{AGENCY_OWNER_PHONE}"
        )
        print("🚨 Urgent Alert sent to Owner.")
    except Exception as e:
        print(f"❌ Failed to alert owner: {e}")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def notify_agent_via_email(customer_name, message, reply):
    """
    Sends an email CC of the conversation to the agency.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    recipient_email = os.getenv("AGENCY_OWNER_EMAIL")

    if not all([sender_email, sender_password, recipient_email]):
        print("⚠️ Email skipped: Missing SMTP credentials in .env")
        return

    try:
        # Create Message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"🔔 Agenzia AI: Reply to {customer_name}"

        body = f"""
        <h2>New AI Interaction</h2>
        <p><strong>Customer:</strong> {customer_name}</p>
        <hr>
        <p><strong>User:</strong> "{message}"</p>
        <p><strong>AI:</strong> "{reply}"</p>
        <hr>
        <p><em>(Reply to this email to ignore, or WhatsApp the client directly to intervene)</em></p>
        """
        msg.attach(MIMEText(body, 'html'))

        # Send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email sent to {recipient_email}")

    except Exception as e:
        print(f"❌ Email Failed: {e}")

def handle_incoming_message(customer_phone, message_text):
    # 1. Check if we are already in Human Mode
    if check_if_human_mode(customer_phone):
        return "AI is muted. Human agent is in control."

    message_lower = message_text.lower()
    
    # 2. TIER 1: IMMEDIATE TAKEOVER - Client explicitly wants human (with fuzzy matching)
    if fuzzy_keyword_match(message_text, TIER1_TAKEOVER_KEYWORDS):
        logger.warning(f"TIER1 Keyword (takeover): {customer_phone} said '{message_text}'")
        toggle_human_mode(customer_phone)
        notify_owner_urgent(customer_phone, message_text)
        return "Ho avvisato il mio responsabile. Le risponderà personalmente a breve. 👨‍💼"

    # 3. TIER 2: ALERT ONLY - Sensitive topic, notify owner but AI continues (with fuzzy matching)
    tier2_triggered = fuzzy_keyword_match(message_text, TIER2_ALERT_KEYWORDS)
    if tier2_triggered:
        logger.info(f"TIER2 Keyword (alert): {customer_phone} discussing sensitive topic")
        # Alert owner (non-blocking, AI still responds)
        notify_owner_urgent(customer_phone, f"[ATTENZIONE] Cliente sta negoziando: {message_text}")

    # 4. Retrieve Context
    history = get_chat_history(customer_phone)

    # 5. Check if appointment-related keywords
    APPOINTMENT_KEYWORDS = ["visita", "visitare", "appuntamento", "vedere", "incontrare", "passare"]
    wants_appointment = any(kw in message_lower for kw in APPOINTMENT_KEYWORDS)
    
    # Get Calendly link from env (set by agency owner)
    calendly_link = os.getenv("CALENDLY_LINK", "")
    booking_instruction = ""
    if wants_appointment and calendly_link:
        booking_instruction = f"\n\nIMPORTANTE: Il cliente vuole prenotare. Includi questo link: {calendly_link}"
    
    # 5. Generate Reply
    prompt = f"""
    Sei un assistente immobiliare esperto.
    Storico chat: {history}
    Ultimo messaggio utente: "{message_text}"
    
    Obiettivo: Rispondi in modo professionale e breve (max 50 parole).
    Se chiedono appuntamenti, proponi il link di prenotazione.{booking_instruction}
    """
    
    ai_response = mistral.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    reply_text = ai_response.choices[0].message.content

    # 5. Send Reply (with error handling)
    try:
        twilio_client.messages.create(
            body=reply_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{customer_phone}"
        )
    except Exception as e:
        print(f"⚠️ Twilio Send Error: {e}")
        # Continue processing even if send fails (message still logged)

    # 6. Calculate Lead Score
    lead_score = calculate_lead_score(message_text)
    
    # 7. Alert owner if HOT LEAD (score >= 50)
    if lead_score >= 50:
        notify_owner_urgent(customer_phone, f"🔥 HOT LEAD (Score: {lead_score}): {message_text}")

    # 8. Save & Report
    save_lead_to_dashboard("Cliente WhatsApp", customer_phone, message_text, reply_text, lead_score)
    
    return reply_text
