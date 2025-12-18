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
        details = f"Immobile: {property_info['title']}, Prezzo: €{property_info['price']}, Città: {property_info['city']}"
    else:
        details = "Non ho trovato l'immobile specifico, ma offri una consulenza generale."

    # 2. Tell the AI the facts
    prompt = f"""
    Sei un agente immobiliare. Il cliente {customer_name} chiede di: {property_query}.
    DATI REALI DAL DATABASE: {details}
    Scrivi un messaggio WhatsApp professionale in italiano confermando i dettagli se trovati.
    """
    
    ai_response = mistral.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 3. Send via WhatsApp
    message_text = ai_response.choices[0].message.content
    twilio_client.messages.create(
        body=message_text,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=f"whatsapp:{customer_phone}"
    )
    
    # 4. Save to Dashboard
    ai_notes = f"Interessato a {property_query}. Proposta inviata con successo."
    save_lead_to_dashboard(customer_name, customer_phone, message_text, ai_notes)
    
    return "Messaggio inviato con dati reali!"

# TEST: Use your own phone number here (with international code, e.g., +39...)
my_test_number = "+34625852546"
print(f"Sending message... SID: {send_ai_whatsapp(my_test_number, 'Marco', 'Attico a Milano')}")

# TEST: Try searching for the "Attico" we put in the database
print(handle_real_estate_lead("+34625852546", "Marco", "Attico"))