import requests
import json
import time
import sys
import os

# Ensure we can access config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import config
    WEBHOOK_KEY = config.WEBHOOK_API_KEY
except ImportError:
    WEBHOOK_KEY = "prod_dev_secret_key_2025"

API_URL = "http://localhost:8000"

SCENARIOS = {
    "1": {
        "name": "Luxury Seeker (Marco)",
        "phone": "+393335550001",
        "portal_msg": "Interessato ad attico vista duomo, budget 2M.",
        "whatsapp_msg": "Ciao, ho visto l'annuncio. Avete altri attici simili in Brera? Budget fino a 2.5mln."
    },
    "2": {
        "name": "First-Time Buyer (Sofia)",
        "phone": "+393335550002",
        "portal_msg": "Cerco bilocale zona Navigli, max 350k.",
        "whatsapp_msg": "Salve, vorrei sapere se il bilocale in via Tortona è ancora disponibile. Ho un budget di 350-400k."
    },
    "3": {
        "name": "Investor (Luca)",
        "phone": "+393335550003",
        "portal_msg": "Cerco immobili da mettere a reddito, zona università.",
        "whatsapp_msg": "Buongiorno, cerco piccoli tagli per investimento (monolocali/bilocali) tra 200k e 300k. Valuto Prati o Centro."
    }
}

def run_demo(scenario_id):
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        print("❌ Scenario non trovato.")
        return

    print(f"\n--- 🌟 Starting Live Demo: {scenario['name']} ---")
    
    # Step 1: Portal Lead Ingestion
    print(f"📡 1. Simulating Portal Lead ({scenario['phone']})...")
    portal_payload = {
        "name": scenario['name'],
        "phone": scenario['phone'],
        "source": "immobiliare",
        "message": scenario['portal_msg']
    }
    res1 = requests.post(f"{API_URL}/webhooks/portal", json=portal_payload, headers={"X-Webhook-Key": WEBHOOK_KEY})
    if res1.status_code == 200:
        print("✅ Lead created in CRM.")
    else:
        print(f"❌ Error: {res1.text}")
        return

    time.sleep(2)

    # Step 2: WhatsApp Message
    print(f"📩 2. Simulating Incoming WhatsApp: '{scenario['whatsapp_msg']}'")
    twilio_payload = {
        "Body": scenario['whatsapp_msg'],
        "From": f"whatsapp:{scenario['phone']}"
    }
    res2 = requests.post(f"{API_URL}/webhooks/twilio", data=twilio_payload, headers={"X-Webhook-Key": WEBHOOK_KEY})
    if res2.status_code == 200:
        print("🤖 AI Replied instantly.")
        print(f"   AI Message: {res2.json().get('message', '')[:100]}...")
    else:
        print(f"❌ Error: {res2.text}")

    print("\n--- ✅ Demo Step Complete! Now check the Dashboard. ---")

if __name__ == "__main__":
    print("Select a demo scenario:")
    for k, v in SCENARIOS.items():
        print(f"{k}. {v['name']}")
    
    choice = input("\nEnter number (1-3): ")
    run_demo(choice)
