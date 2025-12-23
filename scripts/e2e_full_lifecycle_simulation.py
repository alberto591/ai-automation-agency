import os
import sys
import time

# Add the project root to sys.path
sys.path.append(os.getcwd())

from application.services.journey_manager import JourneyManager
from application.services.lead_processor import LeadProcessor
from domain.services.logging import get_logger
from infrastructure.adapters.document_adapter import DocumentAdapter
from infrastructure.adapters.google_calendar_adapter import GoogleCalendarAdapter
from infrastructure.adapters.market_adapter import IdealistaMarketAdapter
from infrastructure.adapters.mistral_adapter import MistralAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.adapters.twilio_adapter import TwilioAdapter
from infrastructure.market_scraper import ImmobiliareScraper

logger = get_logger("E2E_Simulation")


def run_simulation():
    print("\n🚀 STARTING E2E FULL LIFECYCLE SIMULATION")
    print("=========================================\n")

    # 1. Initialize Adapters & Services
    db = SupabaseAdapter()
    ai = MistralAdapter()
    msg = TwilioAdapter()  # Note: In simulation, this might log instead of send if not configured
    market = IdealistaMarketAdapter()
    scraper = ImmobiliareScraper()
    calendar = GoogleCalendarAdapter()
    doc_gen = DocumentAdapter()

    from application.services.lead_processor import LeadScorer

    scorer = LeadScorer()
    journey = JourneyManager(db, calendar, doc_gen, msg)
    processor = LeadProcessor(db, ai, msg, scorer, journey, scraper, market, calendar)

    # Simulation lead info
    phone = "+447700900123"  # UK Number to trigger English persona
    name = "E2E Test Lead"
    property_id = "test-prop-123"  # Simulated property lead

    print("📍 STEP 1: PORTAL INGESTION (Phase 1 & 2)")
    print(f"Simulating lead from portal for UK number: {phone}")

    initial_msg = "Hello, I saw your listing for the villa in Siena. Is it still available?"
    response = processor.process_incoming_message(
        phone,
        initial_msg,
        source="PORTAL",
        context={"property_id": property_id, "property_name": "Villa Siena"},
    )

    print(f"AI Response:\n{response}\n")
    time.sleep(2)

    print("📍 STEP 2: INFORMATION & BROCHURE REQUEST (Phase 3)")
    print("User asks for more details and photos.")

    info_msg = "Yes, it looks beautiful. Can I have more details and some photos or a brochure?"
    response = processor.process_incoming_message(phone, info_msg)

    print(f"AI Response:\n{response}\n")
    print("(Check logs for 'SENDING_PROPERTY_BROCHURE' event)\n")
    time.sleep(2)

    print("📍 STEP 3: NEGOTIATION & MARKET ANALYSIS (Phase 5)")
    print("User asks about the price and market trends.")

    neg_msg = "Is the price negotiable? How is the market in Siena right now?"
    response = processor.process_incoming_message(phone, neg_msg)

    print(f"AI Response:\n{response}\n")
    time.sleep(2)

    print("📍 STEP 4: CONVERSION & APPOINTMENT (Phase 4)")
    print("User wants to visit the property.")

    visit_msg = "I'd like to visit it next week. How can we arrange that?"
    response = processor.process_incoming_message(phone, visit_msg)

    print(f"AI Response:\n{response}\n")

    print("=========================================")
    print("✅ E2E SIMULATION COMPLETE")
    print("Review logs to verify all backend triggers (PDF, Market Data) were called.")


if __name__ == "__main__":
    try:
        run_simulation()
    except Exception as e:
        logger.error("SIMULATION_FAILED", context={"error": str(e)})
        sys.exit(1)
