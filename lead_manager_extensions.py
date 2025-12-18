
# ... (imports remain the same)

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

def handle_incoming_message(customer_phone, message_text):
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
    twilio_client.messages.create(
        body=reply_text,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=f"whatsapp:{customer_phone}"
    )
    
    # 5. Save Interaction
    save_lead_to_dashboard("Cliente WhatsApp", customer_phone, message_text, reply_text)
    
    return reply_text
