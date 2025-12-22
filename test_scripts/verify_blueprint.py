import os
import sys
from datetime import UTC, datetime

# Add root to path
sys.path.append(os.getcwd())

from config.container import container
from domain.enums import LeadStatus

def cleanup_lead(phone):
    db = container.db
    try:
        # Hard delete if possible or at least ensure it doesn't affect the test
        # SupabaseAdapter doesn't have delete_lead, so we'll just clear out the record
        # but better yet, let's use the client directly for a true purge
        db.client.table("leads").delete().eq("customer_phone", phone).execute()
        print(f"🧹 Purged lead: {phone}")
    except Exception as e:
        print(f"⚠️ Cleanup failed for {phone}: {e}")

def verify_blueprint_scenarios():
    print("🚀 Verifying Blueprint Scenarios...")
    
    lp = container.lead_processor
    db = container.db
    
    # 1. Test Web Appraisal (Phase 1.1)
    print("\n--- Scenario 1: Web Appraisal (Phase 1.1) ---")
    phone_appraisal = "+39111222333"
    cleanup_lead(phone_appraisal)
    
    query1 = "Vorrei una valutazione gratuita per il mio immobile in Via Roma 5, Milano. #appraisal"
    print(f"Input: {query1}")
    lp.process_lead(phone_appraisal, "Mario Appraisal", query1)
    
    lead1 = db.get_lead(phone_appraisal)
    if not lead1:
        print("❌ Lead not found in DB after processing!")
        return
        
    print(f"Full Lead Data: {lead1}")
    status = lead1.get('status')
    source = lead1.get('metadata', {}).get('source') if lead1.get('metadata') else None
    print(f"Lead Status: {status}")
    print(f"Metadata Source: {source}")
    
    assert status == LeadStatus.HOT, f"Expected HOT, got {status}"
    assert source == "WEB_APPRAISAL", f"Expected WEB_APPRAISAL, got {source} (Lead info: {lead1.get('metadata')})"
    
    # 2. Test Portal Lead (Phase 1.2)
    print("\n--- Scenario 2: Portal Lead (Phase 1.2) ---")
    phone_portal = "+39444555666"
    cleanup_lead(phone_portal)
    
    query2 = "Agency: Immobiliare.it. Messaggio: Sono interessato all'immobile: Trilocale Brera."
    print(f"Input: {query2}")
    lp.process_lead(phone_portal, "Luigi Portal", query2)
    
    lead2 = db.get_lead(phone_portal)
    source2 = lead2.get('metadata', {}).get('source')
    prop_id = lead2.get('metadata', {}).get('context_data', {}).get('property_id')
    print(f"Lead Source: {source2}")
    print(f"Context Prop: {prop_id}")
    
    assert source2 == "PORTAL"
    assert "brera" in prop_id.lower()
    
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
    assert "calendly.com" in response.lower()

    print("\n✅ Verification Complete! All blueprint phases are correctly wired.")

if __name__ == "__main__":
    try:
        verify_blueprint_scenarios()
    except Exception as e:
        print(f"\n❌ Verification Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
