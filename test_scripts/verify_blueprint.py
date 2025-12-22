import os
import sys
from datetime import UTC, datetime

# Add root to path
sys.path.append(os.getcwd())

from config.container import container
from domain.enums import LeadStatus

def cleanup_all(phone):
    db = container.db
    try:
        # Purge Lead
        db.client.table("leads").delete().eq("customer_phone", phone).execute()
        # Purge Cache (all of it for clean test)
        db.client.table("semantic_cache").delete().neq("query_text", "___").execute()
        print(f"🧹 Purged lead {phone} and cleared semantic cache.")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

def verify_blueprint_scenarios():
    print("🚀 Verifying Blueprint Scenarios (with Clean Cache)...")
    
    lp = container.lead_processor
    db = container.db
    
    # 1. Test Web Appraisal (Phase 1.1)
    print("\n--- Scenario 1: Web Appraisal (Phase 1.1) ---")
    phone_appraisal = "+39111222333"
    cleanup_all(phone_appraisal)
    
    query1 = "Vorrei una valutazione gratuita per il mio immobile in Via Roma 5, Milano. #appraisal"
    print(f"Input: {query1}")
    lp.process_lead(phone_appraisal, "Mario Appraisal", query1)
    
    lead1 = db.get_lead(phone_appraisal)
    status = lead1.get('status')
    source = lead1.get('metadata', {}).get('source') if lead1.get('metadata') else None
    print(f"Lead Status: {status}")
    print(f"Metadata Source: {source}")
    
    assert status == LeadStatus.HOT
    assert source == "WEB_APPRAISAL"
    
    # 2. Test Portal Lead (Phase 1.2)
    print("\n--- Scenario 2: Portal Lead (Phase 1.2) ---")
    phone_portal = "+39444555666"
    cleanup_all(phone_portal)
    
    query2 = "Agency: Immobiliare.it. Messaggio: Sono interessato all'immobile: Trilocale Brera."
    print(f"Input: {query2}")
    lp.process_lead(phone_portal, "Luigi Portal", query2)
    
    lead2 = db.get_lead(phone_portal)
    source2 = lead2.get('metadata', {}).get('source') if lead2.get('metadata') else None
    prop_id = lead2.get('metadata', {}).get('context_data', {}).get('property_id') if lead2.get('metadata') else None
    print(f"Lead Source: {source2}")
    print(f"Context Prop: {prop_id}")
    
    assert source2 == "PORTAL"
    assert "brera" in str(prop_id).lower()
    
    # 3. Test Appointment Steering (Phase 4.1)
    print("\n--- Scenario 3: Appointment Steering (Phase 4.1) ---")
    query3 = "Mi piacerebbe visitarla domani mattina, è possibile?"
    print(f"Input: {query3}")
    response = lp.process_lead(phone_portal, "Luigi Portal", query3)
    
    lead3 = db.get_lead(phone_portal)
    jstate = lead3.get('journey_state')
    print(f"Lead Journey State: {jstate}")
    print(f"AI Response Preview: {response[:150]}...")
    
    assert jstate == LeadStatus.APPOINTMENT_REQUESTED
    assert "setmore.com" in response.lower()

    print("\n✅ Verification Complete! All blueprint phases are correctly wired.")

if __name__ == "__main__":
    try:
        verify_blueprint_scenarios()
    except Exception as e:
        print(f"\n❌ Verification Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
