from datetime import datetime, timezone, timedelta
import os
import logging
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

    # Sanitize phone number (remove spaces, etc. for E.164)
    clean_number = re.sub(r'[^\d+]', '', str(to_number))
    from_number = config.TWILIO_PHONE_NUMBER.strip() # Ensure no trailing spaces
    
    logger.info(f"📤 Attempting to send WhatsApp message to {clean_number} from {from_number}")

    try:
        msg = twilio_client.messages.create(
            body=body_text,
            from_=from_number,
            to=f"whatsapp:{clean_number}"
        )
        logger.info(f"✅ Twilio Message Sent! SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp to {to_number}: {e}", exc_info=True)
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



def get_preferred_language(phone: str) -> str:
    """Detects preferred language based on country code."""
    if phone.startswith("+39") or phone.startswith("0039"):
        return "Italian"
    elif phone.startswith("+34") or phone.startswith("0034"):
        return "Spanish"
    return "English"

def send_ai_whatsapp(customer_phone, customer_name, interest):
    # 1. AI Generates the message
    pref_lang = get_preferred_language(customer_phone)
    prompt = f"Write a short, professional WhatsApp message for {customer_name} regarding their interest in: {interest}. Respond in {pref_lang}."
    ai_response = mistral.chat.complete(
        model="mistral-small-latest", messages=[{"role": "user", "content": prompt}]
    )
    reply_text = ai_response.choices[0].message.content

    # 2. Twilio sends the message
    message = twilio_client.messages.create(
        body=reply_text,
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


def save_lead_to_dashboard(customer_name, customer_phone, last_msg, ai_notes, lead_score=0, status=None, postcode=None):
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
            "postcode": postcode,
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


def handle_real_estate_lead(customer_phone, customer_name, property_query, postcode=None):
    # 0. Check for Appraisal Request First (Lead Magnet Flow)
    if "RICHIESTA VALUTAZIONE" in property_query:
        # Better extraction: find what's after "VALUTAZIONE: "
        parts = property_query.split("RICHIESTA VALUTAZIONE: ")
        address = parts[-1].strip() if len(parts) > 1 else property_query
        
        pref_lang = get_preferred_language(customer_phone)
        report = get_valuation_report(address, postcode=postcode, language=pref_lang)
        
        # Save and send immediately
        save_lead_to_dashboard(customer_name, customer_phone, property_query, report, lead_score=85, postcode=postcode) 
        
        send_whatsapp_safe(customer_phone, report)
            
        return report

    # 1. Search database for ALL matching properties (up to 3)
    matching_properties = get_matching_properties(property_query, limit=3)
    
    # 2. Format property information
    if matching_properties:
        details = format_property_options(matching_properties)
        context_note = f"Found {len(matching_properties)} properties"
    else:
        details = "No specific properties found in database. Offer a custom search and consultation."
        context_note = "No match"

    # 3. Build AI prompt
    pref_lang = get_preferred_language(customer_phone)
    prompt = f"""
    Identity: You are "Anzevino AI", an elite real estate virtual assistant.
    Goal: Respond professionally and persuasively but keep it succinct (WhatsApp style).
    Language Protocol: 
    - The customer is using a phone number from a region where {pref_lang} is preferred.
    - ALWAYS respond in the SAME LANGUAGE as the user (Italian, English, or Spanish). 
    - Default to {pref_lang} if the user's inquiry is ambiguous.

    CUSTOMER: {customer_name}
    INQUIRY: {property_query}
    
    OFFICIAL DATABASE DATA:
    {details}
    
    TASK:
    1. {"Present the matching options enthusiastically" if matching_properties else "Offer general consultancy"}.
    2. Create urgency (e.g., "These properties are in high demand").
    3. Close with a clear Call to Action (CTA): e.g., "Would you like to see photos?" or "When are you free for a viewing?".
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
    save_lead_to_dashboard(customer_name, customer_phone, message_text, ai_notes, postcode=postcode)

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

# Professional Market Data Fallbacks (Milan Average Prices 2025)
# Used when the Supabase table is empty.
MILANO_ZONE_PRICES = {
    "CENTRO": 10500,
    "BRERA": 11000,
    "NAVIGLI": 6500,
    "PRATI": 7500, # Assuming some Rome data mixed in or similar tier
    "PORTA NUOVA": 9500,
    "ISOLA": 7000,
    "GARIBALDI": 8500,
    "NIGUARDA": 4200,
    "VATICANO": 7000,
    "BOVISA": 3800,
    "LAMBRATE": 4500,
    "SAN SIRO": 5500,
    "FIRENZE": 4500,
    "SIENA": 3200,
    "PISA": 2800,
    "LUCCA": 3500,
    "AREZZO": 1500,
    "LIVORNO": 2100,
    "GROSSETO": 2500,
    "PRATO": 2200,
    "PISTOIA": 2100,
    "MASSA": 2400,
    "CARRARA": 1800,
    "FORTE DEI MARMI": 10500,
    "VIAREGGIO": 3400,
    "MONTE ARGENTARIO": 5500,
    "FIGLINE E INCISA VALDARNO": 2400,
    "FIGLINE": 2400,
    "INCISA VALDARNO": 2300,
    "TOSCANA": 2600,
    "MILANO": 5200 # General average
}

REPORT_TEMPLATES = {
    "Italian": {
        "header": "🏠 *VALUTAZIONE ISTANTANEA AI*",
        "address": "📍 *Indirizzo:*",
        "zone": "📊 *Zona rilevata:*",
        "avg_price": "💰 *Prezzo Medio Zona:*",
        "range": "📈 *Range Estimativo:*",
        "footer": "Questa stima è generata dalla nostra IA analizzando i prezzi medi delle compravendite recenti nel quartiere.\n\n👉 *Cosa fare ora?* Se desidera una perizia tecnica certificata e gratuita (molto più precisa), risponda 'SI' a questo messaggio o prenoti qui: https://vino5493.setmore.com"
    },
    "English": {
        "header": "🏠 *INSTANT AI VALUATION*",
        "address": "📍 *Address:*",
        "zone": "📊 *Detected Zone:*",
        "avg_price": "💰 *Avg Zone Price:*",
        "range": "📈 *Estimated Range:*",
        "footer": "This estimate is generated by our AI analyzing recent market sales in the neighborhood.\n\n👉 *What to do now?* If you'd like a certified technical appraisal (much more precise), reply 'YES' or book here: https://vino5493.setmore.com"
    },
    "Spanish": {
        "header": "🏠 *VALORACIÓN INSTANTÁNEA AI*",
        "address": "📍 *Dirección:*",
        "zone": "📊 *Zona detectada:*",
        "avg_price": "💰 *Precio Medio Zona:*",
        "range": "📈 *Rango Estimativo:*",
        "footer": "Esta estimación es generada por nuestra IA analizando los precios medios de ventas recientes en el barrio.\n\n👉 *¿Qué hacer ahora?* Si desea una valoración técnica certificada y gratuita (mucho más precisa), responda 'SÍ' o reserve aquí: https://vino5493.setmore.com"
    }
}

def get_market_context(zone: str):
    """
    Fetches market analytics (avg price/mq) for a specific zone.
    PRIORITY:
    1. Local Database (market_data table)
    2. Live API (RapidAPI Idealista)
    3. Hardcoded Fallbacks (MILANO_ZONE_PRICES)
    """
    from market_service import get_live_market_price
    
    zone_upper = zone.upper()
    db_market_text = ""
    
    try:
        # 1. Try DB first (Fastest & Free)
        result = supabase.table("market_data").select("price_per_mq").ilike("zone", f"%{zone}%").execute()
        prices = [row['price_per_mq'] for row in result.data if row['price_per_mq'] > 0]
        
        if prices:
            avg_price = sum(prices) / len(prices)
            db_market_text = f"\n[DATI DI MERCATO ZONA {zone_upper}]: Il prezzo medio di mercato in questa zona è di circa €{int(avg_price)}/mq basato sui nostri dati interni."
            return db_market_text
    except Exception as e:
        logger.warning(f"Market Data Lookup failed: {e}")

    # 2. Try Live API (Real-time data from Marketplace)
    live_price = get_live_market_price(zone)
    if live_price:
        return f"\n[DATI LIVE {zone_upper}]: Prezzo medio attuale di mercato rilevato: €{live_price}/mq. Nota: I prezzi possono variare in base alle finiture."

    # 3. Smart Fallback if DB and API are unavailable
    if zone_upper in MILANO_ZONE_PRICES:
        avg_price = MILANO_ZONE_PRICES[zone_upper]
        return f"\n[STIMA DI MERCATO {zone_upper}]: Basandoci sugli ultimi trend del 2025, il prezzo medio in zona è di circa €{avg_price}/mq."
    
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

def get_valuation_report(address: str, postcode: str = None, language: str = "Italian"):
    """
    Calculates a price range based on market data for a given address.
    """
    # 1. Extract zone from address or postcode
    # Priority order: Multi-word locations first to avoid partial matches
    zones = ["Forte dei Marmi", "Figline e Incisa Valdarno", "Figline", "Incisa Valdarno", "Monte Argentario", "Viareggio", "Firenze", "Siena", "Pisa", "Lucca", "Arezzo", "Grosseto", "Livorno", "Pistoia", "Prato", "Massa", "Carrara", "Toscana", "Porta Nuova", "San Siro", "Prati", "Centro", "Navigli", "Niguarda", "Vaticano", "Brera", "Isola", "Garibaldi", "Bovisa", "Lambrate"]
    
    # 1a. Postcode Mapping for High-Priority Tuscany Areas
    postcode_zones = {
        "50063": "Figline e Incisa Valdarno",
        "501": "Firenze",      # Prefix match
        "53100": "Siena",
        "561": "Pisa",         # Prefix match
        "55100": "Lucca",
        "52100": "Arezzo",
        "58100": "Grosseto",
        "571": "Livorno",      # Prefix match
        "51100": "Pistoia",
        "59100": "Prato",
        "54100": "Massa",
        "54033": "Carrara",
        "55042": "Forte dei Marmi",
        "58019": "Monte Argentario",
        "55049": "Viareggio"
    }

    detected_zone = "Milano" # default fallback
    
    address_clean = address.lower()
    
    # 0. Check for ZIP code in the address string if not provided separately
    if not postcode:
        zip_match = re.search(r'\b\d{5}\b', address)
        if zip_match:
            postcode = zip_match.group(0)
            logger.info(f"📍 Extracted ZIP {postcode} from address string")

    # 1. Extract zone from address or postcode
    found_in_addr = False
    for z in zones:
        if z.lower() in address_clean:
            detected_zone = z
            found_in_addr = True
            break
    
    # If not found in address, check postcode
    if not found_in_addr and postcode:
        # Exact match first
        if postcode in postcode_zones:
            detected_zone = postcode_zones[postcode]
        else:
            # Prefix match (e.g. 50123 -> Firenze)
            for pc_prefix, pc_zone in postcode_zones.items():
                if postcode.startswith(pc_prefix):
                    detected_zone = pc_zone
                    break
            
    # 3. Extract average price from the text
    logger.info(f"🔎 Final Zone Detection: '{detected_zone}' for Address: '{address}'")
    
    market_text = get_market_context(detected_zone)
    
    # If no data found for detected zone, try "Milano" as absolute last resort
    if not market_text and detected_zone != "Milano":
        logger.warning(f"⚠️ No market data for {detected_zone}, falling back to Milano")
        detected_zone = "Milano"
        market_text = get_market_context(detected_zone)

    price_match = re.search(r'€(\d+)', market_text)
    if not price_match:
        msg = f"✅ Richiesta Ricevuta! Il nostro sistema sta elaborando i dati per {address}"
        if postcode: msg += f" ({postcode})"
        msg += ". La ricontatteremo a breve con il report completo."
        return msg
    
    avg_price = int(price_match.group(1))
    
    # 4. Calculate range (+/- 8% for professional flexibility)
    min_range = int(avg_price * 0.92)
    max_range = int(avg_price * 1.08)
    
    # 5. Get Language Template
    tpl = REPORT_TEMPLATES.get(language, REPORT_TEMPLATES["Italian"])
    
    report = f"{tpl['header']}\n\n"
    report += f"{tpl['address']} {address}"
    if postcode: report += f" (CAP: {postcode})"
    report += f"\n{tpl['zone']} {detected_zone.upper()}\n"
    report += f"{tpl['avg_price']} €{avg_price}/mq\n"
    report += f"{tpl['range']} €{min_range} - €{max_range} al mq\n\n"
    report += tpl['footer']
    
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

import difflib

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
    Checks if any keyword matches the text using fuzzy matching (difflib).
    """
    if not text:
        return False
        
    text_lower = text.lower()
    words = text_lower.split()
    
    # Expand keywords with synonyms
    expanded_keywords = set(keywords)
    for kw in keywords:
        if kw in KEYWORD_SYNONYMS:
            expanded_keywords.update(KEYWORD_SYNONYMS[kw])
    
    for keyword in expanded_keywords:
        keyword_lower = keyword.lower()
        
        # 1. Exact substring match check (fast)
        if keyword_lower in text_lower:
            return True
            
        # 2. Fuzzy match word-by-word
        for word in words:
            # Skip short words to avoid noise, or if they are too different in length
            if len(word) < 3 or abs(len(word) - len(keyword_lower)) > 3: # Added length difference check
                continue
                
            # Calculate similarity ratio (0.0 to 1.0) -> convert to 0-100
            score = difflib.SequenceMatcher(None, word, keyword_lower).ratio() * 100
            
            # Fuzzy match for typos
            if score >= threshold:
                logger.debug(f"Fuzzy match: '{word}' ~ '{keyword_lower}' (score: {score:.1f})")
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
            # Better extraction: find what's after "VALUTAZIONE: "
            parts = message_text.split("RICHIESTA VALUTAZIONE: ")
            address = parts[-1].strip() if len(parts) > 1 else message_text
            
            pref_lang = get_preferred_language(customer_phone)
            report = get_valuation_report(address, language=pref_lang)
            
            # Save to Dashboard immediately
            save_lead_to_dashboard(
                "AI Appraisal Lead", 
                customer_phone, 
                message_text, 
                report, 
                status="HOT",
                lead_score=85
            )
            
            # Send WhatsApp
            send_whatsapp_safe(customer_phone, report)
            return report
                
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
                database_context = "No direct property matches found. Offer a custom search or neighborhood consultation."
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
        
        # Get Setmore link from env
        booking_link = os.getenv("SETMORE_LINK", "")
        booking_instruction = ""
        if wants_appointment and booking_link:
            booking_instruction = f"\n\n[SISTEMA]: Il cliente vuole prenotare. Link: {booking_link}"
        
        # Adjust tone for negative sentiment
        tone_instruction = ""
        if sentiment_negative:
            tone_instruction = "\n\n[SISTEMA]: Cliente frustrato. Sii empatico, scusati e cerca di risolvere subito."
        
        # 7. Generate Reply (Sales Pro Prompt)
        pref_lang = get_preferred_language(customer_phone)
        prompt = f"""
        Identity: You are "Anzevino AI", an elite multilingual real estate assistant.
        Language Protocol: 
        - The customer's phone prefix suggests a preference for {pref_lang}.
        - You MUST respond in the SAME language as the user (Italian, English, or Spanish). 
        - If the user's message is short or ambiguous, use {pref_lang}.
        Goal: SELL properties or BOOK VIEWINGS.
        
        REAL-TIME DATABASE DATA (USE THIS):
        {database_context}
        
        CONVERSATION HISTORY:
        {history}
        
        LAST USER MESSAGE: "{message_text}"
        
        SALES LOGIC:
        1. If properties are in the database, present them with enthusiasm. If not, offer a personalized search.
        2. Be proactive: Don't wait for them to ask, offer to send photos or book a viewing directly.
        3. Tone: Professional, friendly, "smart" (WhatsApp style).
        4. Call to Action (CTA): ALWAYS close with an open question.
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
        notify_owner_urgent(customer_phone, f"🔴 SYSTEM ERROR: AI failed with lead. Human intervention required!\nError: {str(global_err)[:100]}")
        # AUTO-MUTING AI FOR THIS LEAD TO PREVENT LOOPS
        toggle_human_mode(customer_phone)
        return "Al momento ho un piccolo problema tecnico. Un mio collega umano la ricontatterà a breve! / I'm having a technical issue. A human agent will contact you shortly! 🙏"
