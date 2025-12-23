import argparse

import requests

# Configuration
BASE_URL = "http://localhost:8000"
PHONE = "+34625852546"  # User's verified phone


def simulate_reply(message_text):
    print(f"\n📨 SIMULAZIONE MESSAGGIO IN ARRIVO DA: {PHONE}")
    print(f"💬 Testo: '{message_text}'")
    print("-" * 50)

    try:
        # Simulate Twilio Webhook Data
        payload = {"Body": message_text, "From": f"whatsapp:{PHONE}", "ProfileName": "Marco (User)"}

        # Hit the local webhook
        resp = requests.post(f"{BASE_URL}/webhooks/twilio", data=payload)

        if resp.status_code == 200:
            print("✅ Webhook ricevuto con successo dal Server.")
            print("⏳ L'AI sta elaborando... Controlla il tuo WhatsApp tra 5 secondi!")
        else:
            print(f"❌ Errore Server: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        print("Assicurati che il server sia attivo (uvicorn api:app ...)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate inbound WhatsApp message")
    parser.add_argument(
        "message",
        type=str,
        nargs="?",
        default="Grazie, quando posso visitare?",
        help="Message to send",
    )
    args = parser.parse_args()

    simulate_reply(args.message)
