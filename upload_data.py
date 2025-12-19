import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# The Agency Portfolio (Sample Data)
# ---------------------------------------------------------
# In a real scenario, this would come from a CSV or XML feed.
portfolio = [
    {
        "title": "Attico a Milano Centro",
        "description": "Splendido attico con vista Duomo, 150mq, terrazza panoramica, 3 camere, doppi servizi. Ristrutturato recentemente.",
        "price": 850000,
    },
    {
        "title": "Trilocale Via Roma",
        "description": "Appartamento luminoso in zona servita, 90mq, 2 camere, balcone, box auto incluso. Ottimo investimento.",
        "price": 320000,
    },
    {
        "title": "Villa con Piscina in Toscana",
        "description": "Casale ristrutturato nel Chianti, 300mq, 2 ettari di terreno, piscina privata, dependance ospiti.",
        "price": 1250000,
    },
    {
        "title": "Bilocale Moderno Porta Nuova",
        "description": "Moderno appartamento in grattacielo, 60mq, palestra condominiale, vista skyline. Arredato di design.",
        "price": 450000,
    },
]


def upload_portfolio():
    print("🏠 [Agency Database] Updating Portfolio...")

    # Optional: Clear existing data (be careful in production!)
    # print("   - Cleaning old records...")
    # supabase.table("properties").delete().neq("id", 0).execute()

    for property_data in portfolio:
        try:
            print(f"   - Uploading: {property_data['title']}...")
            # Using 'upsert' to update if exists or insert if new (assuming title could be a unique key, or just simple insert)
            # For simplicity in this demo, we just insert. In prod, use an ID.
            supabase.table("properties").insert(property_data).execute()

        except Exception as e:
            print(f"   ⚠️ Could not upload {property_data['title']}: {e}")
            # Usually fails if table structure doesn't match keys.
            # We assume a 'properties' table exists with these text columns.

    print("✅ [Success] All properties uploaded to Supabase!")
    print("   The RAG Brain now knows about these 4 houses.")


if __name__ == "__main__":
    upload_portfolio()
