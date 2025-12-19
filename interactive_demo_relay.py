import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
PHONE = "+34625852546"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_ai(text):
    print(f"\n🤖 \033[94mAI (Sent to WhatsApp):\033[0m {text}")

def print_system(text):
    print(f"\n⚙️  \033[90m{text}\033[0m")

def start_interactive_session():
    clear()
    print("\033[95m" + "="*60)
    print("  📱 INTERACTIVE PARTNER DEMO (HYBRID MODE)")
    print("="*60 + "\033[0m")
    print(f"Target Phone: {PHONE}")
    print("Instructions:")
    print("1. You will receive REAL WhatsApp messages on your phone.")
    print("2. Reply on your phone (optional), BUT...")
    print("3. \033[93mTYPE YOUR REPLY HERE\033[0m to send it to the AI.")
    print("(This bridges the connection since we don't have ngrok)\n")
    
    input("👉 Press Enter to start the conversation...")

    # 1. Trigger Initial Lead
    print_system("Creating new lead from Portal...")
    payload = {
        "name": "Marco User",
        "phone": PHONE,
        "agency": "Immobiliare.it",
        "properties": "Richiesta per: Trilocale Via Roma",
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/leads", json=payload)
        data = resp.json()
        print_ai(data.get("ai_response", "Error"))
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 2. Conversation Loop
    while True:
        print("\n" + "-"*40)
        user_reply = input("👤 \033[92mYour Reply (Type here what you want to say):\033[0m ")
        
        if user_reply.lower() in ["exit", "quit", "stop"]:
            print("👋 Session ended.")
            break
            
        print_system("Sending to AI 'Brain'...")
        
        try:
            # Simulate Inbound Webhook
            webhook_payload = {
                "Body": user_reply,
                "From": f"whatsapp:{PHONE}",
                "ProfileName": "Marco User"
            }
            requests.post(f"{BASE_URL}/webhooks/twilio", data=webhook_payload)
            
            print("✅ Sent! Check your WhatsApp for the reply...")
            
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    start_interactive_session()
