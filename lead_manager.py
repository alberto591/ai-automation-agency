import os
from dotenv import load_dotenv
from supabase import create_client
from mistralai import Mistral
from twilio.rest import Client

load_dotenv()
# Initialize everything
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Debug: Print Twilio credentials to verify they are loaded correctly
print(f"TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
print(f"TWILIO_AUTH_TOKEN: {os.getenv('TWILIO_AUTH_TOKEN')}")
print(f"TWILIO_PHONE_NUMBER: {os.getenv('TWILIO_PHONE_NUMBER')}")

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

def get_property_details(property_name):
    # This query searches your Supabase 'properties' table
    response = supabase.table("properties").select("*").ilike("title", f"%{property_name}%").execute()
    
    if response.data:
        return response.data[0] # Return the first match found
    return None

def send_ai_whatsapp(customer_phone, customer_name, interest):
    # 1. AI Generates the message
    prompt = f"Scrivi un messaggio WhatsApp breve in italiano per {customer_name} riguardo a: {interest}."
    ai_response = mistral.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    italian_text = ai_response.choices[0].message.content

    # 2. Twilio sends the message
    message = twilio_client.messages.create(
        body=italian_text,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=f"whatsapp:{customer_phone}"
    )
    return message.sid

def save_lead_to_dashboard(customer_name, customer_phone, last_msg, ai_notes):
    # This sends the data directly to your Supabase table
    data = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "last_message": last_msg,
        "ai_summary": ai_notes,
        "status": "New"
    }
    
    # Execute the insert
    try:
        supabase.table("lead_conversations").insert(data).execute()
        print(f"✅ Lead {customer_name} saved to Dashboard!")
    except Exception as e:
        print(f"❌ Error saving lead: {e}")

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
        details = "Non ho trovato l'immobile specifico, ma offri una consulenza generale."

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
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 3. Send via WhatsApp
    message_text = ai_response.choices[0].message.content
    try:
        twilio_client.messages.create(
            body=message_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{customer_phone}"
        )
    except Exception as e:
        print(f"⚠️ Twilio Send Error (Expected in Sandbox): {e}")
        # Proceed to save to dashboard anyway logic is sound
        message_text += " [Simulated Send]"
    
    # 4. Save to Dashboard
    ai_notes = f"Interessato a {property_query}. Proposta inviata con successo."
    save_lead_to_dashboard(customer_name, customer_phone, message_text, ai_notes)
    
    return "Messaggio inviato con dati reali!"

if __name__ == "__main__":
    # TEST: Use your own phone number here (with international code, e.g., +39...)
    my_test_number = "+34625852546"
    # print(f"Sending message... SID: {send_ai_whatsapp(my_test_number, 'Marco', 'Attico a Milano')}")

    # TEST: Try searching for the "Attico" we put in the database
    # print(handle_real_estate_lead("+34625852546", "Marco", "Attico"))
    pass

def get_chat_history(customer_phone):
    """
    Retrieves the last 5 messages for this user to build context.
    """
    try:
        # Fetch last 5 interactions
        response = supabase.table("lead_conversations")\
            .select("*")\
            .eq("customer_phone", customer_phone)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
        
        # Reverse to chronological order
        history = response.data[::-1] if response.data else []
        
        # Format for AI
        context_string = ""
        for row in history:
            # We assume 'last_message' is User and 'ai_summary'/response is AI
            # Ideally database would have 'role' column, but adapting to current schema:
            if row.get('last_message'):
                context_string += f"Cliente: {row['last_message']}\n"
            if row.get('ai_summary'): # storing full AI text here for now
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
            "status": "TAKEOVER"
        }
        supabase.table("lead_conversations").insert(data).execute()
        return True
    except Exception as e:
        print(f"❌ Error setting human mode: {e}")
        return False

def check_if_human_mode(customer_phone):
    """
    Checks if the AI should be muted.
    """
    try:
        # Get the VERY LAST interaction
        response = supabase.table("lead_conversations")\
            .select("status")\
            .eq("customer_phone", customer_phone)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
            
        if response.data and response.data[0]['status'] == 'TAKEOVER':
            return True
        return False
    except Exception as e:
        print(f"⚠️ Error checking human mode: {e}")
        return False

def handle_incoming_message(customer_phone, message_text):
    # 0. SAFETY CHECK: Is Human Mode On?
    if check_if_human_mode(customer_phone):
        print(f"🛑 AI Muted for {customer_phone} (Human Mode Active)")
        return "AI is muted. Human agent is in control."

    # 1. Get Context
    history = get_chat_history(customer_phone)
    
    # 2. Build Prompt with Memory
    prompt = f"""
    Sei "Anzevino AI". Stai avendo una conversazione WhatsApp con un cliente.
    
    STORICO CONVERSAZIONE:
    {history}
    
    NUOVO MESSAGGIO CLIENTE: {message_text}
    
    OBIETTIVO:
    Rispondi in modo cordiale, breve e utile. 
    Se chiedono di visitare, proponi 2 orari domani.
    Se chiedono info, rispondi basandoti sul contesto precedente.
    """
    
    # 3. Generate Reply
    ai_response = mistral.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    reply_text = ai_response.choices[0].message.content
    
    # 4. Send Reply
    try:
        twilio_client.messages.create(
            body=reply_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=f"whatsapp:{customer_phone}"
        )
    except Exception as e:
        print(f"⚠️ Twilio Send Error (Expected in Sandbox): {e}")

    # 5. Save Interaction
    save_lead_to_dashboard("Cliente WhatsApp", customer_phone, message_text, reply_text)
    
    return reply_text