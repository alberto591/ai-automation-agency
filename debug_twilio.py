import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_PHONE_NUMBER")
to_number = "+34625852546"

client = Client(account_sid, auth_token)

print(f"📡 TESTING DIRECT TWILIO CONNECTION")
print(f"FROM: {from_number}")
print(f"TO:   {to_number}")

try:
    message = client.messages.create(
        body="🤖 Debug Test: Ciao! Se leggi questo, la connessione è OK.",
        from_=from_number,
        to=f"whatsapp:{to_number}"
    )
    print(f"✅ Message sent! SID: {message.sid}")
    print(f"Status: {message.status}")
except Exception as e:
    print(f"❌ Error: {e}")
