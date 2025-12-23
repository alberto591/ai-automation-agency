import sys
import time

import requests

BASE_URL = "http://localhost:8000"
PHONE = "+39555000111"
NAME = "Dr. Ross Geller"


def print_step(title):
    print(f"\n🎬 {title}")
    print("-" * 50)


def print_ai_reply(response_data):
    if isinstance(response_data, dict):
        msg = response_data.get("message", str(response_data))
    else:
        msg = str(response_data)

    # Clean up formatting for display
    print(f'🤖 AI AGENT: "{msg}"')


def wait(seconds=2):
    time.sleep(seconds)


print("🎭 SCENARIO START: 'THE LOWBALL OFFER' 🎭")
print(f"Items: 1.25M Euro Villa. Client: {NAME}. Agency: Agenzia AI.")

# -------------------------------------------------------------
# ACT 1: THE LEAD ARRIVES
# -------------------------------------------------------------
print_step("ACT 1: The 'Ding' from Idealista")
wait()

payload = {
    "name": NAME,
    "phone": PHONE,
    "agency": "Idealista Luxury",
    "properties": "Vorrei informazioni sulla Villa con Piscina in Toscana. (Rif: VILLA-99)",
}

try:
    resp = requests.post(f"{BASE_URL}/api/leads", json=payload)
    if resp.status_code == 200:
        print("✅ CRM: Lead Created.")
        print_ai_reply(resp.json()["ai_response"])  # This returns the raw text usually
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)

wait(3)

# -------------------------------------------------------------
# ACT 2: THE AGGRESSIVE OFFER
# -------------------------------------------------------------
print_step("ACT 2: The Aggressive Offer")
offer_msg = "Senta, non perdiamo tempo. Ho 1.1 Milioni Cash pronti sul conto. Offerta valida 24h. Prendere o lasciare."
print(f'👤 {NAME}: "{offer_msg}"')
wait()

try:
    resp = requests.post(
        f"{BASE_URL}/webhooks/twilio",
        data={"Body": offer_msg, "From": f"whatsapp:{PHONE}"},
    )
    if resp.status_code == 200:
        data = resp.json()
        print_ai_reply(data)
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Error: {e}")

wait(4)

# -------------------------------------------------------------
# ACT 3: THE TAKEOVER
# -------------------------------------------------------------
print_step("ACT 3: The Owner Panics & Takes Over")
print("📢 AGENCY OWNER: 'Whoa, 1.1M in cash? I need to handle this guy personally. Stop the bot!'")
wait(1)

try:
    resp = requests.post(f"{BASE_URL}/api/leads/takeover", json={"phone": PHONE})
    if resp.status_code == 200:
        print(f"👮‍♂️ DASHBOARD: {resp.json().get('message')}")
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# -------------------------------------------------------------
# ACT 4: THE SILENCE
# -------------------------------------------------------------
print_step("ACT 4: The Follow-Up (Silence Check)")
followup = "Allora? Cosa avete deciso? Ho un altro appuntamento..."
print(f'👤 {NAME}: "{followup}"')
print("(The AI should NOT reply to this. It should stay silent.)")
wait()

try:
    resp = requests.post(
        f"{BASE_URL}/webhooks/twilio",
        data={"Body": followup, "From": f"whatsapp:{PHONE}"},
    )
    data = resp.json()
    if data.get("message") == "AI is muted. Human agent is in control.":
        print("😶 SYSTEM: [AI Muted] (Log: Human agent has control)")
        print(
            "✅ SUCCESS: The Agency Owner is now free to call Ross personally and close the deal."
        )
    else:
        print(f"❌ FAIL! AI Replied: {data}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎭 END OF SCENARIO")
