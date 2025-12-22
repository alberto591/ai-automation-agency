import requests
import json
import time
import sys
import os

# Ensure we can access config
sys.path.append(os.getcwd())

API_URL = os.getenv("API_URL", "http://localhost:8000")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY", "prod_dev_secret_key_2025")

SCENARIOS = {
    "1": {
        "name": "Luxury Seeker (Marco) - PORTAL",
        "phone": "+393335550001",
        "payload": {
            "name": "Marco Luxury",
            "agency": "Immobiliare.it",
            "phone": "+393335550001",
            "properties": "Attico vista Duomo, 2.5mln"
        }
    },
    "2": {
        "name": "Free Appraisal (Elena) - WEB_APPRAISAL (HOT)",
        "phone": "+393335550002",
        "payload": {
            "name": "Elena Appraisal",
            "agency": "Website Widget",
            "phone": "+393335550002",
            "properties": "Valutazione via Roma 5, Milano #appraisal"
        }
    },
    "3": {
        "name": "Visit Request (Luca) - APPOINTMENT STEERING",
        "phone": "+393335550003",
        "payload": {
            "name": "Luca Investor",
            "agency": "Idealista",
            "phone": "+393335550003",
            "properties": "Interessato al Rustico. Vorrei visitarlo domani."
        }
    }
}

def run_demo(scenario_id):
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        print("❌ Scenario non trovato.")
        return

    print(f"\n--- 🌟 Starting Live Demo: {scenario['name']} ---")
    print(f"📡 Target API: {API_URL}")
    
    # Send to /api/leads (Standard entry point)
    print(f"🚀 Sending lead data for {scenario['phone']}...")
    try:
        response = requests.post(
            f"{API_URL}/api/leads", 
            json=scenario['payload'], 
            headers={"X-Webhook-Key": WEBHOOK_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Lead captured and processed.")
            print(f"🤖 AI Response: {data.get('ai_response', '')[:200]}...")
            print("\n💡 ACTION: Now open the Dashboard to see the new lead and its AI Insights!")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    print("======================================")
    print("   ANZEVINO AI - CLIENT DEMO TOOL")
    print("======================================")
    for k, v in SCENARIOS.items():
        print(f"{k}. {v['name']}")
    
    choice = input("\nSelect Scenario (1-3): ")
    run_demo(choice)
