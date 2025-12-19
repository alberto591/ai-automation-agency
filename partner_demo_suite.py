import requests
import time
import os

BASE_URL = "http://localhost:8000"
PHONE = "+39111222333"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("\033[95m" + "="*70)
    print("  🏆 AGENZIA AI: PARTNER DEMO SUITE 🏆")
    print("="*70 + "\033[0m")

def scenario(title, description):
    print(f"\n🔥 SCENARIO: \033[93m{title}\033[0m")
    print(f"   {description}\n")
    input("👉 [Premi INVIO per iniziare]")

def print_msg(role, text):
    color = "\033[94m" if role == "AI" else "\033[92m"
    name = "🤖 ANZEVINO AI" if role == "AI" else "👤 CLIENTE"
    print(f"\n{color}{name}:\033[0m {text}")

# --- START ---
clear()
banner()
print("Questa suite simula 3 casi d'uso reali per mostrare la potenza del sistema.")

# SCENARIO 1: IL VENDITORE (Appraisal)
scenario("IL VENDITORE (Acquisizione)", "Un potenziale venditore richiede una valutazione dal sito.")
print("Simulazione: Richiesta valutazione per Via Roma 1, Milano...")
time.sleep(1)

payload_1 = {
    "name": "Marco Venditore",
    "phone": PHONE,
    "agency": "Landing Page",
    "properties": "VALUTAZIONE: Via Roma 1, Milano",
}
resp = requests.post(f"{BASE_URL}/api/leads", json=payload_1).json()
print_msg("AI", resp.get("ai_response", "Errore Server"))

# SCENARIO 2: IL COMPRATORE PRECISO (RAG)
scenario("IL COMPRATORE (Precision RAG)", "Un cliente cerca un immobile con requisiti specifici (Min 100mq, 3 locali).")
print_msg("CLIENTE", "Cerco un trilocale di almeno 100mq a Milano.")
time.sleep(1)

resp = requests.post(
    f"{BASE_URL}/webhooks/twilio",
    data={"Body": "Cerco un trilocale di almeno 100mq a Milano.", "From": f"whatsapp:{PHONE}"}
).json()
print_msg("AI", resp.get("message", "Errore Server"))

# SCENARIO 3: ALTERNATIVE & TAKE OVER
scenario("LA CHIUSURA (Alternative & Takeover)", "L'immobile richiesto non è disponibile, l'AI propone alternative e poi interviene l'umano.")
print_msg("CLIENTE", "Avete attici a Brera? Budget 1.5M.")
time.sleep(1)

resp = requests.post(
    f"{BASE_URL}/webhooks/twilio",
    data={"Body": "Avete attici a Brera? Budget 1.5M.", "From": f"whatsapp:{PHONE}"}
).json()
print_msg("AI", resp.get("message", "Errore Server"))

print("\n\033[91m[SISTEMA]: Alert proprietario inviato! Il cliente è fuori budget o cerca qualcosa di raro.\033[0m")
print("\n🎉 DEMO COMPLETATA!")
print("Controlla la Dashboard per vedere i dati estratti (Budget: 1.5M, Zona: Brera).")
print("="*70 + "\n")
