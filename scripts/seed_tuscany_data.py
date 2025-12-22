import logging
import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Supabase Setup
url: str = os.getenv("SUPABASE_URL")
key: str = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
)
supabase: Client = create_client(url, key)

# Tuscany Market Data (Avg Price/mq - 2024/2025 Estimates)
TUSCANY_MARKET_DATA = [
    {"zone": "Firenze Centro", "price_per_mq": 5200, "city": "Firenze"},
    {"zone": "Firenze Oltrarno", "price_per_mq": 4800, "city": "Firenze"},
    {"zone": "Siena Centro", "price_per_mq": 3200, "city": "Siena"},
    {"zone": "Pisa Centro", "price_per_mq": 2800, "city": "Pisa"},
    {"zone": "Lucca Mura", "price_per_mq": 3600, "city": "Lucca"},
    {"zone": "Arezzo Centro", "price_per_mq": 1600, "city": "Arezzo"},
    {"zone": "Livorno Mare", "price_per_mq": 2400, "city": "Livorno"},
    {"zone": "Forte dei Marmi", "price_per_mq": 12000, "city": "Forte dei Marmi"},
    {"zone": "Pistoia", "price_per_mq": 1800, "city": "Pistoia"},
    {"zone": "Grosseto", "price_per_mq": 2100, "city": "Grosseto"},
    {"zone": "Prato", "price_per_mq": 2300, "city": "Prato"},
    {"zone": "Viareggio", "price_per_mq": 3400, "city": "Viareggio"},
    {"zone": "Scandicci", "price_per_mq": 3100, "city": "Firenze"},
]


def seed_tuscany():
    logger.info("📍 Starting Tuscany Market Data Seeding...")

    for item in TUSCANY_MARKET_DATA:
        try:
            # Check if exists
            existing = supabase.table("market_data").select("*").eq("zone", item["zone"]).execute()

            if not existing.data:
                supabase.table("market_data").insert(item).execute()
                logger.info(f"✅ Inserted: {item['zone']} - €{item['price_per_mq']}/mq")
            else:
                supabase.table("market_data").update(item).eq("zone", item["zone"]).execute()
                logger.info(f"🔄 Updated: {item['zone']} - €{item['price_per_mq']}/mq")
        except Exception as e:
            logger.error(f"❌ Error seeding {item['zone']}: {e}")


if __name__ == "__main__":
    seed_tuscany()
    logger.info("✨ Seeding complete!")
