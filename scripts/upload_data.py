import argparse
import csv
import os

from dotenv import load_dotenv
from supabase import Client, create_client

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
# The Agency Portfolio (Sample Data 2.0)
# ---------------------------------------------------------
DEFAULT_PORTFOLIO = [
    {
        "title": "Attico a Milano Centro",
        "description": "Splendido attico con vista Duomo, terrazza panoramica, doppi servizi. Ristrutturato recentemente.",
        "price": 850000,
        "sqm": 150,
        "rooms": 3,
        "bathrooms": 2,
        "energy_class": "A+",
        "floor": 5,
        "has_elevator": True,
        "status": "available",
    },
    {
        "title": "Trilocale Via Roma",
        "description": "Appartamento luminoso in zona servita, balcone, box auto incluso. Ottimo investimento.",
        "price": 320000,
        "sqm": 90,
        "rooms": 3,
        "bathrooms": 1,
        "energy_class": "C",
        "floor": 2,
        "has_elevator": True,
        "status": "available",
    },
    {
        "title": "Bilocale Moderno Porta Nuova",
        "description": "Moderno appartamento in grattacielo, palestra condominiale, vista skyline. Arredato di design.",
        "price": 450000,
        "sqm": 60,
        "rooms": 2,
        "bathrooms": 1,
        "energy_class": "A",
        "floor": 12,
        "has_elevator": True,
        "status": "available",
    },
]


def load_from_csv(file_path):
    """Loads properties from a CSV file with Data 2.0 support."""
    properties = []
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found {file_path}")
        return []

    try:
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic validation
                if "title" in row and "description" in row:
                    try:
                        # Required conversion
                        row["price"] = int(row["price"]) if row.get("price") else 0

                        # Data 2.0 optional fields (auto-conversion)
                        if row.get("sqm"):
                            row["sqm"] = int(row["sqm"])
                        if row.get("rooms"):
                            row["rooms"] = int(row["rooms"])
                        if row.get("bathrooms"):
                            row["bathrooms"] = int(row["bathrooms"])
                        if row.get("floor"):
                            row["floor"] = int(row["floor"])
                        if row.get("has_elevator"):
                            row["has_elevator"] = row["has_elevator"].lower() in [
                                "true",
                                "1",
                                "si",
                                "yes",
                            ]

                        properties.append(row)
                    except ValueError as ve:
                        print(f"   ⚠️ Skipping {row['title']}: Data conversion error: {ve}")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

    return properties


def upload_portfolio(portfolio_data):
    print(f"🏠 [Agency Database] Updating Portfolio with {len(portfolio_data)} items...")

    for property_data in portfolio_data:
        try:
            print(f"   - Uploading: {property_data['title']}...")
            supabase.table("properties").insert(property_data).execute()
        except Exception as e:
            print(f"   ⚠️ Could not upload {property_data['title']}: {e}")

    print("✅ [Success] Sync completed!")
    print("   The RAG Brain now knows about these houses.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload property portfolio to Supabase.")
    parser.add_argument("--csv", type=str, help="Path to a CSV file containing properties.")
    args = parser.parse_args()

    if args.csv:
        data = load_from_csv(args.csv)
    else:
        print("💡 No CSV provided, using default sample data.")
        data = DEFAULT_PORTFOLIO

    if data:
        upload_portfolio(data)
    else:
        print("❌ No data to upload.")
