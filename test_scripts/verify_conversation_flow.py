import sys
import os
import json

# Add root to path
sys.path.append(os.getcwd())

from config.container import container

def test_multi_turn_conversation():
    print("🔄 STARTING MULTI-TURN CONVERSATION TEST")
    print("="*50)
    
    phone = "+393330001112"
    name = "Conversational Test"
    
    turns = [
        "Ciao, cerco un appartamento a Firenze.",
        "Il mio budget è di circa 500.000 euro.",
        "Preferirei la zona di Porta Nuova o centro.",
        "Mi sembra perfetto, vorrei andare a vederlo domani."
    ]
    
    for i, user_input in enumerate(turns):
        print(f"\n👉 [TURN {i+1}] USER: {user_input}")
        
        # Process Lead (this handles the full LangGraph pipeline)
        response = container.lead_processor.process_lead(phone, name, user_input)
        
        print(f"🤖 AI: {response}")
        
        # Intermediate State Check
        lead = container.db.get_lead(phone)
        metadata = lead.get("metadata", {})
        journey = lead.get("journey_state")
        
        print(f"📊 STATE: Stage={journey} | Budget={lead.get('budget_max')} | Intent={metadata.get('last_intent')}")

    print("\n" + "="*50)
    print("✅ TEST COMPLETED")
    
    # Final Verification
    final_lead = container.db.get_lead(phone)
    if final_lead.get("journey_state") == "appointment_requested":
        print("🎉 SUCCESS: Lead reached appointment stage through conversation!")
    else:
        print("⚠️ WARNING: Final stage was " + str(final_lead.get("journey_state")))

if __name__ == "__main__":
    test_multi_turn_conversation()
