import re
from datetime import datetime, timedelta, UTC
from application.services.lead_processor import LeadProcessor, LeadScorer
from application.services.journey_manager import JourneyManager
from domain.enums import LeadStatus
from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)

def test_sales_journey():
    print("🚀 Starting Sales Journey Verification...")
    
    # 0. Cleanup Old Data
    phone = "+393331234567"
    print(f"\n--- Step 0: Cleanup old data for {phone} ---")
    container.db.client.table("leads").delete().eq("customer_phone", phone).execute()
    
    # 1. Simulate Incoming Inquiry with Visit Intent
    text = "Buongiorno, ho visto il trilocale in Via Roma e vorrei venire a vederlo domani."
    
    print(f"\n--- Step 1: User says: '{text}' ---")
    container.lead_processor.process_incoming_message(phone, text)
    
    lead = container.db.get_lead(phone)
    print(f"Lead State: {lead.get('journey_state')}")
    assert lead.get("journey_state") == LeadStatus.APPOINTMENT_REQUESTED
    
    # 2. Simulate Manual Scheduling (from Dashboard/API)
    print(f"\n--- Step 2: Scheduling visit ---")
    start_time = datetime.now(UTC) + timedelta(days=1)
    container.journey.transition_to(phone, LeadStatus.SCHEDULED, context={"start_time": start_time})
    
    lead = container.db.get_lead(phone)
    print(f"Lead State: {lead.get('journey_state')}")
    assert lead.get("journey_state") == LeadStatus.SCHEDULED
    
    # 3. Simulate Contract Generation
    print(f"\n--- Step 3: Generating Proposta d'Acquisto ---")
    container.journey.transition_to(phone, LeadStatus.CONTRACT_PENDING, context={"offered_price": 250000})
    
    lead = container.db.get_lead(phone)
    print(f"Lead State: {lead.get('journey_state')}")
    assert lead.get("journey_state") == LeadStatus.CONTRACT_PENDING
    
    print("\n✅ Sales Journey Verification Successful!")

if __name__ == "__main__":
    # Ensure environment is set up (MISTRAL_API_KEY etc)
    try:
        test_sales_journey()
    except Exception as e:
        print(f"❌ Verification Failed: {str(e)}")
