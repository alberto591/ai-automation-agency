import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supabase import create_client

from config.settings import settings
from infrastructure.market_scraper import MarketDataManager
from infrastructure.market_service import MarketDataService

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ZONES = [
    ("Milano, Centro", "Milano"),
    ("Milano, Navigli", "Milano"),
    ("Milano, Isola", "Milano"),
    ("Firenze, Centro", "Firenze"),
    ("Chianti", "Toscana"),
]


def map_to_strict_schema(api_item: dict, zone: str, city: str) -> dict:
    original_desc = api_item.get("description", "") or ""
    # Inject location into description since zone/city columns are missing
    enhanced_desc = f"📍 ZONA: {zone}, CITTÀ: {city}.\n\n{original_desc}"

    return {
        "title": api_item.get("suggestedTexts", {}).get("title", f"Appartamento a {zone}"),
        "description": enhanced_desc,
        "price": float(api_item.get("price", 0)),
        "sqm": int(api_item.get("size", 0)),
        "rooms": int(api_item.get("rooms", 0)),
        "bathrooms": int(api_item.get("bathrooms", 0)),
        "floor": int(
            api_item.get("floor", "0")
            .replace("st", "")
            .replace("nd", "")
            .replace("rd", "")
            .replace("th", "")
            if api_item.get("floor") and api_item.get("floor").isdigit()
            else 0
        ),
        "energy_class": "N/A",
        "has_elevator": api_item.get("hasLift", False),
        "status": "available",
        "image_url": api_item.get("thumbnail") or "",
    }


def run_gathering(duration_minutes: int = 30):
    service = MarketDataService()

    # Use Service Role Key to bypass RLS
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    if not key:
        logger.error("❌ SUPABASE_KEY missing")
        return

    db_client = create_client(settings.SUPABASE_URL, key)
    manager = MarketDataManager(db_client=db_client)
    db = manager.db

    if not service.api_key:
        logger.error("❌ RAPIDAPI_KEY is missing.")
        return

    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    logger.info(f"🚀 Starting Data Gathering for {duration_minutes} minutes (Strict Schema)...")

    total_saved = 0
    iteration = 1

    while datetime.now() < end_time:
        for zone, city in ZONES:
            if datetime.now() >= end_time:
                break

            logger.info(f"📡 Scraping {zone}...")
            listings = service.search_properties(zone, city)

            for item in listings:
                try:
                    data = map_to_strict_schema(item, zone, city)
                    image_url = data.get("image_url")

                    if not image_url:
                        continue

                    # Manual Check for Duplicates
                    existing = (
                        db.table("properties")
                        .select("id")
                        .eq("image_url", image_url)
                        .limit(1)
                        .execute()
                    )
                    if existing.data:
                        # logger.info(f"   Skip duplicate: {data['title']}")
                        continue

                    # Insert
                    db.table("properties").insert(data).execute()
                    total_saved += 1
                    print(f"   ✅ Saved: {data['title']}")

                except Exception as e:
                    logger.error(f"   Save Failed: {e}")

            time.sleep(2)  # Politeness

        iteration += 1
        time.sleep(10)

    logger.info(f"✅ Gathering Complete. Total properties saved: {total_saved}")


def signal_handler(sig, frame):
    logger.info("🛑 Process interrupted by user.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    run_gathering(30)
