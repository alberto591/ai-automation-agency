import os
import sys
import time

import requests

BASE_URL = "http://localhost:8000"
PHONE = "+39888999000"
NAME = "Giulia (Cliente VIP)"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header(text):
    print("\n" + "=" * 60)
    print(f"  ✨ {text}")
    print("=" * 60 + "\n")


def pause_for_effect():
    input("\n👉 [Press Enter to Continue] ")


def print_ai(text):
    print(f"\n🤖 \033[94mAI AGENT:\033[0m {text}")


def print_user(text):
    print(f"\n👤 \033[92mCLIENTE:\033[0m {text}")


def print_system(text):
    print(f"\n⚙️  \033[90mSYSTEM:\033[0m {text}")


# ---------------------------------------------------------
# THE SHOW
# ---------------------------------------------------------

clear()
header("AGENZIA AI: LIVE DEMO")
print("Scenario: A Lead arrives from Immobiliare.it for the 'Villa in Toscana'.")
print("The Goal: Show how the AI handles the lead, negotiates, and allows takeover.")
pause_for_effect()

# STEP 1: CAPTURE
header("STEP 1: THE CAPTURE")
print("Simulating an incoming email from 'Immobiliare.it'...")
time.sleep(1)

payload = {
    "name": NAME,
    "phone": PHONE,
    "agency": "Immobiliare.it",
    "properties": "Richiesta per: Villa con Piscina in Toscana",
}

try:
    resp = requests.post(f"{BASE_URL}/api/leads", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print_system("Lead Captured & Processed in 0.4s")
        print_ai(data.get("ai_response", ""))
    else:
        print("❌ Error connecting to server. Is it running?")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

pause_for_effect()

# STEP 2: THE INTERACTION
header("STEP 2: THE NEGOTIATION")
print("The Client replies via WhatsApp. Let's send a simulated message.")
print_user("Wow che bella! Ma il prezzo è trattabile? Offro 1.0M.")

pause_for_effect()
print_system("Sending message to AI...")

try:
    resp = requests.post(
        f"{BASE_URL}/webhooks/twilio",
        data={
            "Body": "Wow che bella! Ma il prezzo è trattabile? Offro 1.0M.",
            "From": f"whatsapp:{PHONE}",
        },
    )
    data = resp.json()
    print_ai(data.get("message", ""))
except Exception as e:
    print(f"❌ Error: {e}")

pause_for_effect()

# STEP 3: THE TAKEOVER
header("STEP 3: THE CONTROL (HUMAN TAKEOVER)")
print("You, the Agency Owner, see the lowball offer.")
print("You decide to intervene.")
pause_for_effect()

print_system("Activating 'Stop AI' Protocol...")
try:
    resp = requests.post(f"{BASE_URL}/api/leads/takeover", json={"phone": PHONE})
    print(f"✅ DASHBOARD: {resp.json().get('message')}")
except Exception as e:
    print(f"❌ Error: {e}")

pause_for_effect()

# STEP 4: VERIFICATION
header("STEP 4: VERIFY SILENCE")
print("The Client sends another message. The AI should be DEAD SILENT.")
print_user("Pronto? C'è nessuno?")

pause_for_effect()
try:
    resp = requests.post(
        f"{BASE_URL}/webhooks/twilio",
        data={"Body": "Pronto? C'è nessuno?", "From": f"whatsapp:{PHONE}"},
    )
    data = resp.json()
    if data.get("message") == "AI is muted. Human agent is in control.":
        print_system("AI Status: MUTED 🔇")
        print("\n🎉 DEMO SUCCESSFUL! The Client is yours to call.")
    else:
        print_ai(data.get("message", ""))
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 30)
print("  END OF DEMO")
print("=" * 30 + "\n")
