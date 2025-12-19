from datetime import datetime, timezone, timedelta
import os
import logging
from thefuzz import fuzz
from config import config
from supabase import create_client
from mistralai import Mistral
from twilio.rest import Client
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize everything via config
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
mistral = Mistral(api_key=config.MISTRAL_API_KEY)

# Initialize Twilio client
twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

def send_whatsapp_safe(to_number, body_text):
    """
    Sends a WhatsApp message via Twilio or logs it if MOCK_MODE is enabled.
    """
    mock_mode = os.getenv("MOCK_MODE", "False").lower() in ["true", "1", "yes"]
    
    if mock_mode:
        log_entry = f"\n[MOCK WHATSAPP] To: {to_number} | Body: {body_text}\n"
        logger.info(f"\033[93m{log_entry}\033[0m")
        with open("mock_messages.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - {log_entry}")
        return "queued-mock"

    try:
        msg = twilio_client.messages.create(
            body=body_text,
            from_=config.TWILIO_PHONE_NUMBER,
            to=f"whatsapp:{to_number}"
        )
        return msg.sid
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {to_number}: {e}", exc_info=True)
        return None


def get_property_details(property_name):
    """Returns the first matching property (legacy function)"""
    response = (
        supabase.table("properties")
        .select("*")
        .ilike("title", f"%{property_name}%")
        .execute()
    )

    if response.data:
        return response.data[0]  # Return the first match found
    return None


def get_matching_properties(property_query, limit=3, min_sqm=None, min_rooms=None):
    """
    Returns multiple matching properties with Data 2.0 numeric filtering support.
    """
    query = supabase.table("properties").select("*")
    
    # Text Search (Base)
    query = query.ilike("description", f"%{property_query}%")
    
    # Data 2.0: Numeric Filters
    if min_sqm:
        query = query.gte("sqm", min_sqm)
    if min_rooms:
        query = query.gte("rooms", min_rooms)
        
    response = query.limit(limit).execute()
    return response.data if response.data else []


def get_alternative_properties(budget=None, limit=2):
    """
    Finds properties within a price range or simply the latest listings 
    to keep the conversation going when a specific search fails.
    """
    query = supabase.table("properties").select("*")
    
    if budget:
        # Search for properties +/- 20% of budget
        min_p = budget * 0.8
        max_p = budget * 1.2
        query = query.gte("price", min_p).lte("price", max_p)
    
    response = query.order("price", desc=False).limit(limit).execute()
    return response.data if response.data else []


def format_property_options(properties):
    """Formats multiple properties into a readable list"""
    if not properties:
        return "Non ho trovato immobili corrispondenti."
    
    if len(properties) == 1:
        # Single match - detailed format
        p = properties[0]
        return (
            f"TITOLO: {p.get('title', 'N/A')}\n"
            f"PREZZO: €{p.get('price', 0):,}\n"
            f"DESCRIZIONE: {p.get('description', '')}"
        )
    
    # Multiple matches - compact list format
    result = f"Ho trovato {len(properties)} opzioni per te:\n\n"
    for i, p in enumerate(properties, 1):
        price_str = f"€{p.get('price', 0):,}" if p.get('price') else "Prezzo su richiesta"
        result += f"{i}. {p.get('title', 'N/A')} - {price_str}\n"
    result += "\nQuale ti interessa di più? Posso darti più dettagli!"
    return result



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


def save_lead_to_dashboard(customer_name, customer_phone, last_msg, ai_notes, lead_score=0, status=None):
    """
    Saves or updates a lead record in the dashboard.
    Maintains a 'messages' JSONB array for the full chat history.
    """
    try:
        # 1. Fetch existing lead to get current history
        existing = (
            supabase.table("lead_conversations")
            .select("messages")
            .eq("customer_phone", customer_phone)
            .execute()
        )

        messages = []
        if existing.data and existing.data[0].get("messages"):
            messages = existing.data[0]["messages"]
        
        # 2. Append the new message interaction
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": last_msg,
            "ai": ai_notes,
            "score": lead_score
        }
        messages.append(new_entry)

        # 3. Prepare data for upsert
        data = {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "last_message": last_msg,
            "ai_summary": ai_notes,
            "status": "Active",
            "messages": messages, # JSONB column
            "updated_at": datetime.now().isoformat()
        }
        
        if status:
            data["status"] = status
        elif lead_score >= 50:
            data["status"] = "HOT"
        elif lead_score >= 30:
            data["status"] = "Warm"

        # --- DATA 2.0: Lead Profiling ---
        # 1. Budget Extraction (Matches k, mln, M, and large numbers)
        # Regex explanation: 
        # Group 1 & 2: Decimals + M/mln (e.g., 2.5mln)
        # Group 3: Thousands + k (e.g., 500k)
        # Group 4: Large raw numbers (e.g., 500000)
        budget_matches = re.findall(r'(\d+(?:\.\d+)?)[\s]?(m(?:ln|ilioni)?)|(\d+)[\s]?k|(\d{5,})', last_msg.lower())
        if budget_matches:
            found_budgets = []
            for m_val, m_unit, k_val, raw_val in budget_matches:
                if m_val:
                    val = int(float(m_val) * 1000000)
                elif k_val:
                    val = int(k_val) * 1000
                else:
                    val = int(raw_val)
                found_budgets.append(val)
            data["budget_max"] = max(found_budgets)
        
        # 2. Zone Extraction
        zones = ["Navigli", "Brera", "Prati", "Centro", "Isola", "Niguarda"]
        detected_zones = [z for z in zones if z.lower() in last_msg.lower()]
        if detected_zones:
            data["preferred_zones"] = detected_zones

        # 4. Upsert (requires customer_phone to be unique/pk or have an upsert constraint)
        try:
            supabase.table("lead_conversations").upsert(data, on_conflict="customer_phone").execute()
            logger.info(f"Lead {customer_name} consolidated in Dashboard (History: {len(messages)} msgs)")
        except Exception as db_err:
            if "column" in str(db_err).lower() and "messages" in str(db_err).lower():
                logger.error("❌ DATABASE INCOMPATIBLE: 'messages' column missing in Supabase.")
                logger.error("👉 Please run the SQL migration provided in the Documentation.")
                # Fallback: Save as a regular row without the JSONB history if needed
                data.pop("messages", None)
                data.pop("updated_at", None)
                supabase.table("lead_conversations").insert(data).execute()
            else:
                raise db_err

    except Exception as e:
        logger.error(f"Error saving lead: {e}")


def handle_real_estate_lead(customer_phone, customer_name, property_query):
    # 0. Check for Appraisal Request First (Lead Magnet Flow)
    if "RICHIESTA VALUTAZIONE" in property_query:
        address = property_query.replace("RICHIESTA VALUTAZIONE: ", "").strip()
        report = get_valuation_report(address)
        
        # Save and send immediately
        save_lead_to_dashboard(customer_name, customer_phone, property_query, report, lead_score=80) 
        
        try:
            twilio_client.messages.create(
                body=report,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=f"whatsapp:{customer_phone}"
            )
        except Exception as e:
            logger.error(f"Failed to send valuation WhatsApp: {e}")
            
        return report

    # 1. Search database for ALL matching properties (up to 3)
    matching_properties = get_matching_properties(property_query, limit=3)
    
    # 2. Format property information
    if matching_properties:
        details = format_property_options(matching_properties)
        context_note = f"Found {len(matching_properties)} properties"
    else:
        details = "Non ho trovato l'immobile specifico, ma offri una consulenza generale."
        context_note = "No match"

    # 3. Build AI prompt
    prompt = f"""
    Sei "Anzevino AI", l'assistente virtuale d'élite dell'agenzia immobiliare.
    Parla in modo professionale, persuasivo ma succinto (stile WhatsApp). Non usare mai "Saluti" o firme lunghe.
    
    CLIENTE: {customer_name}
    RICHIESTA: {property_query}
    
    DATI UFFICIALI DAL DATABASE:
    {details}
    
    OBIETTIVO:
    1. {"Presenta le opzioni trovate in modo entusiasta" if matching_properties else "Offri consulenza generale"}.
    2. Crea urgenza (es. "Sono molto richiesti").
    3. Chiudi con una Call to Action chiara: "Vuoi vedere le foto?" o "Quando puoi passare per una visita?".
    """

    ai_response = mistral.chat.complete(
        model="mistral-small-latest", messages=[{"role": "user", "content": prompt}]
    )

    # 4. Send via WhatsApp
    message_text = ai_response.choices[0].message.content
    try:
        twilio_client.messages.create(
            body=message_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{customer_phone}",
        )
    except Exception as e:
        logger.warning(f"Twilio Send Error: {e}")
        message_text += " [Simulated Send]"

    # 5. Save to Dashboard
    ai_notes = f"Interessato a {property_query}. {context_note}. Proposta inviata."
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
    Activates Human Takeover by updating the status.
    """
    try:
        data = {
            "last_message": "[SYSTEM] Human Takeover Activated",
            "ai_summary": "AI Stopped by Agent",
            "status": "human_mode",
            "updated_at": datetime.now().isoformat()
        }
        supabase.table("lead_conversations").update(data).eq("customer_phone", customer_phone).execute()
        logger.info(f"Human takeover activated for {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Error toggling human mode: {e}")
        return False

def get_market_context(zone: str):
    """
    Fetches market analytics (avg price/mq) for a specific zone from market_data table.
    """
    try:
        # Get all entries for the zone
        result = supabase.table("market_data").select("price_per_mq").ilike("zone", f"%{zone}%").execute()
        prices = [row['price_per_mq'] for row in result.data if row['price_per_mq'] > 0]
        
        if not prices:
            return ""
        
        avg_price = sum(prices) / len(prices)
        return f"\n[DATI DI MERCATO ZONA {zone.upper()}]: Il prezzo medio di mercato in questa zona è di circa €{int(avg_price)}/mq basato su {len(prices)} rilevazioni recenti."
    except Exception as e:
        logger.warning(f"Market Data Lookup failed: {e}")
        return ""

def resume_ai_mode(customer_phone):
    """
    Resumes AI control by resetting the status.
    """
    try:
        data = {
            "last_message": "[SYSTEM] AI Control Resumed",
            "ai_summary": "Human released control back to AI",
            "status": "active",
            "updated_at": datetime.now().isoformat()
        }
        supabase.table("lead_conversations").update(data).eq("customer_phone", customer_phone).execute()
        logger.info(f"AI control resumed for {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Error resuming AI mode: {e}")
        return False

def get_valuation_report(address: str):
    """
    Calculates a price range based on market data for a given address.
    """
    # 1. Extract zone from address (simple heuristic)
    zones = ["Prati", "Centro", "Porta Nuova", "Navigli", "Niguarda", "Vaticano", "Brera", "Isola"]
    detected_zone = "Milano" # default
    for z in zones:
        if z.lower() in address.lower():
            detected_zone = z
            break
            
    # 2. Get market data
    market_text = get_market_context(detected_zone)
    if not market_text:
        return f"Mi dispiace, non ho ancora abbastanza dati di mercato per una valutazione precisa in zona {detected_zone}. Un consulente umano la contatterà a breve."

    # 3. Extract average price from the text (or re-query)
    import re
    price_match = re.search(r'€(\d+)', market_text)
    if not price_match:
        return "Errore nel calcolo della valutazione. Riprova più tardi."
    
    avg_price = int(price_match.group(1))
    
    # 4. Calculate range (+/- 7% for safety)
    min_range = int(avg_price * 0.93)
    max_range = int(avg_price * 1.07)
    
    report = f"✅ VALUTAZIONE AI COMPLETATA per: {address}\n"
    report += f"📍 Zona: {detected_zone.upper()}\n"
    report += f"📊 Prezzo Medio Zona: €{avg_price}/mq\n"
    report += f"📈 Range Estimativo: €{min_range}/mq - €{max_range}/mq\n\n"
    report += "Questa è una stima basata sui big data di zona. Se desidera una perizia tecnica certificata gratuita, possiamo fissare un appuntamento domani?"
    
    return report


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
        
        # If status is active, AI is active
        if last_record["status"] == "active":
            return False
            
        # If status is human_mode, check expiry
        if last_record["status"] == "human_mode":
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
    try:
        # 1. Check if we are already in Human Mode
        if check_if_human_mode(customer_phone):
            return "AI is muted. Human agent is in control."

        message_lower = message_text.lower()
        
        # 1.5 SPECIAL: Lead Magnet / Appraisal Request
        if "RICHIESTA VALUTAZIONE" in message_text:
            address = message_text.replace("RICHIESTA VALUTAZIONE: ", "").strip()
            report = get_valuation_report(address)
            
            # Save to Dashboard immediately
            save_lead_to_dashboard(
                customer_phone, 
                "AI Appraisal Lead", 
                message_text, 
                report, 
                status="HOT"
            )
            
            # Send WhatsApp
            send_whatsapp_safe(customer_phone, report)
                
            return report
        
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
            #Alert owner (non-blocking, AI still responds)
            notify_owner_urgent(customer_phone, f"[ATTENZIONE] Cliente sta negoziando: {message_text}")

        # 3.5 SENTIMENT ANALYSIS - Detect frustration before it escalates
        NEGATIVE_SIGNALS = ["deluso", "arrabbiato", "scherzo", "perché non", "assurdo", "ridicolo", 
                           "mai risposto", "non funziona", "delusione", "pessimo", "inaccettabile"]
        
        sentiment_negative = any(signal in message_lower for signal in NEGATIVE_SIGNALS)
        if sentiment_negative:
            logger.warning(f"Negative sentiment detected from {customer_phone}: {message_text}")
            # Preemptive alert to owner
            notify_owner_urgent(customer_phone, f"⚠️ CLIENTE FRUSTRATO: {message_text}")
            # AI will use softer tone (handled in prompt below)

        # 4. Extract property search query (if any) and search database
        # We use a simple keyword check first, or we can use the AI to identify search intent
        property_keywords = ["camera", "bagno", "trilocale", "bilocale", "villa", "appartamento", "mansarda", "centro", "periferia", "giardino", "terrazza", "garage", "piscina"]
        is_asking_property = any(kw in message_lower for kw in property_keywords) or len(message_text.split()) < 4
        
        database_context = "Nessun immobile specifico richiesto in questo messaggio."
        if is_asking_property:
            # Data 2.0: Extract numeric requirements
            min_sqm = None
            sqm_match = re.search(r'(\d+)[\s]?mq', message_lower)
            if sqm_match:
                min_sqm = int(sqm_match.group(1))

            min_rooms = None
            rooms_match = re.search(r'(\d+)[\s]?locale|(\d+)[\s]?camere', message_lower)
            if rooms_match:
                min_rooms = int(rooms_match.group(1) or rooms_match.group(2))
            elif "trilocale" in message_lower:
                min_rooms = 3
            elif "bilocale" in message_lower:
                min_rooms = 2
            elif "monolocale" in message_lower:
                min_rooms = 1
            elif "quadrilocale" in message_lower:
                min_rooms = 4

            # 4a. Try precise match first (with filters)
            matching_properties = get_matching_properties(message_text, limit=3, min_sqm=min_sqm, min_rooms=min_rooms)
            if matching_properties:
                database_context = format_property_options(matching_properties)
            else:
                # 4b. No match? Try to extract budget and find alternatives
                budget_match = re.search(r'(\d+)[\s]?k|(\d{4,})', message_lower)
                budget = None
                if budget_match:
                    # Extract either '500k' -> 500000 or '300000' -> 300000
                    b_str = budget_match.group(1) or budget_match.group(2)
                    budget = int(b_str) * (1000 if 'k' in budget_match.group(0) else 1)
                
                alternatives = get_alternative_properties(budget=budget, limit=2)
                if alternatives:
                    database_context = "[SCELTE ALTERNATIVE TROVATE]:\n" + format_property_options(alternatives)
                    database_context += "\n\n(Nota x AI: Non abbiamo trovato l'immobile esatto, ma questi sono vicini per zona o budget. Proponili come alternative valide.)"
                else:
                    database_context = "Nessun match trovato nemmeno nelle alternative. Proponi una ricerca personalizzata."

        # 4c. Enrich with Market Context if a zone is identified
        market_stats = ""
        # Identify zone from message or matched properties
        detected_zone = None
        if is_asking_property:
            # Try to find a zone keyword in message
            zones = ["Prati", "Centro", "Porta Nuova", "Navigli", "Niguarda", "Prati", "Vaticano"]
            for z in zones:
                if z.lower() in message_lower:
                    detected_zone = z
                    break
        
        if detected_zone:
            market_stats = get_market_context(detected_zone)
            if market_stats:
                database_context += f"\n\n{market_stats}"

        # 5. Retrieve Context (History)
        history = get_chat_history(customer_phone)

        # 6. Check if appointment-related keywords
        APPOINTMENT_KEYWORDS = ["visita", "visitare", "appuntamento", "vedere", "incontrare", "passare"]
        wants_appointment = any(kw in message_lower for kw in APPOINTMENT_KEYWORDS)
        
        # Get Calendly link from env
        calendly_link = os.getenv("CALENDLY_LINK", "")
        booking_instruction = ""
        if wants_appointment and calendly_link:
            booking_instruction = f"\n\n[SISTEMA]: Il cliente vuole prenotare. Link: {calendly_link}"
        
        # Adjust tone for negative sentiment
        tone_instruction = ""
        if sentiment_negative:
            tone_instruction = "\n\n[SISTEMA]: Cliente frustrato. Sii empatico, scusati e cerca di risolvere subito."
        
        # 7. Generate Reply (Sales Pro Prompt)
        prompt = f"""
        Sei "Anzevino AI", il miglior assistente immobiliare d'Italia.
        Il tuo obiettivo è VENDERE o FISSARE VISITE.
        
        DATI REALI DAL DATABASE (USA QUESTI):
        {database_context}
        
        STORICO CHAT:
        {history}
        
        ULTIMO MESSAGGIO UTENTE: "{message_text}"
        
        LOGICA DI VENDITA:
        1. Se ci sono immobili nel database, presentali con entusiasmo. Se non ci sono, offri di fare una ricerca personalizzata.
        2. Sii proattivo: Non aspettare che chiedano, offri tu di mandare foto o fissare una visita.
        3. Tono: Professionale, cordiale, "smart" (stile WhatsApp).
        4. Call to Action (CTA): Chiudi SEMPRE con una domanda aperta (es. "Vuoi vedere la planimetria?" o "Quando saresti libero per una visita?").
        {booking_instruction}{tone_instruction}
        """
        
        ai_response = mistral.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = ai_response.choices[0].message.content

        # 8. Send Reply (with error handling)
        # 8. Send Reply (SAFE MODE)
        send_whatsapp_safe(customer_phone, reply_text)

        # 9. Calculate Lead Score
        lead_score = calculate_lead_score(message_text)
        
        # 10. Alert owner if HOT LEAD (score >= 50)
        if lead_score >= 50:
            notify_owner_urgent(customer_phone, f"🔥 HOT LEAD (Score: {lead_score}): {message_text}")

        # 11. Save & Report
        save_lead_to_dashboard("Cliente WhatsApp", customer_phone, message_text, reply_text, lead_score)
        
        return reply_text

    except Exception as global_err:
        logger.error(f"🚨 CRITICAL SYSTEM ERROR for {customer_phone}: {global_err}")
        # TRIGGER MANAGER ALERT
        notify_owner_urgent(customer_phone, f"🔴 ERRORE SISTEMA: L'IA ha fallito con il lead. Intervenire manualmente!\nErrore: {str(global_err)[:100]}")
        # AUTO-MUTING AI FOR THIS LEAD TO PREVENT LOOPS
        toggle_human_mode(customer_phone)
        return "Al momento ho un piccolo problema tecnico. Un mio collega umano la ricontatterà tra pochissimi minuti! 🙏"
