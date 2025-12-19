#!/usr/bin/env python3
"""
Follow-Up Automation Script

This script identifies leads that need follow-up and sends automated messages.
Run via cron job or scheduler:
  - Daily: 0 9 * * * /path/to/venv/bin/python scripts/follow_up.py

Follow-up schedule:
  - Day 1: "Ciao [Name], hai avuto modo di pensarci?"
  - Day 3: "La proprietà è ancora disponibile. Vuoi vedere le foto?"
  - Day 7: "Ultimo promemoria prima che passiamo ad altri interessati."
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client
from twilio.rest import Client

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Initialize clients
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# Follow-up message templates
FOLLOW_UP_TEMPLATES = {
    1: "Ciao! 👋 Ieri abbiamo parlato di un immobile. Hai avuto modo di pensarci? Sono qui per qualsiasi domanda!",
    3: "Buongiorno! Volevo ricordarti che la proprietà di cui abbiamo parlato è ancora disponibile. Vuoi vedere più foto o organizzare una visita? 🏠",
    7: "Ciao! È l'ultimo promemoria: abbiamo altri interessati alla proprietà. Se vuoi vederla, fammi sapere oggi! ⏰",
}


def get_leads_needing_followup():
    """
    Returns leads that:
    1. Last interaction was 1, 3, or 7 days ago
    2. Status is NOT 'TAKEOVER' or 'CLOSED'
    3. Haven't received a follow-up for this tier yet
    """
    now = datetime.now(timezone.utc)
    leads_to_contact = []
    
    try:
        # Get all unique phone numbers with their last interaction
        response = supabase.table("lead_conversations")\
            .select("customer_phone,customer_name,created_at,status")\
            .order("created_at", desc=True)\
            .execute()
        
        # Group by phone, get latest record per phone
        latest_by_phone = {}
        for record in response.data:
            phone = record["customer_phone"]
            if phone not in latest_by_phone:
                latest_by_phone[phone] = record
        
        # Check which ones need follow-up
        for phone, record in latest_by_phone.items():
            # Skip if in takeover or system messages
            if record.get("status") in ["TAKEOVER", "RESUMED", "CLOSED"]:
                continue
            if record.get("customer_name") == "System":
                continue
            
            # Calculate days since last interaction
            created_str = record.get("created_at", "")
            if not created_str:
                continue
                
            try:
                created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                days_since = (now - created_at).days
                
                # Check if eligible for follow-up
                if days_since in FOLLOW_UP_TEMPLATES:
                    leads_to_contact.append({
                        "phone": phone,
                        "name": record.get("customer_name", "Cliente"),
                        "days_since": days_since,
                        "template": FOLLOW_UP_TEMPLATES[days_since]
                    })
            except Exception:
                continue
                
    except Exception as e:
        print(f"❌ Error fetching leads: {e}")
    
    return leads_to_contact


def send_follow_up(lead):
    """Sends a follow-up message to the lead."""
    try:
        twilio_client.messages.create(
            body=lead["template"],
            from_=TWILIO_PHONE,
            to=f"whatsapp:{lead['phone']}"
        )
        print(f"✅ Follow-up sent to {lead['phone']} (Day {lead['days_since']})")
        
        # Log the follow-up in database
        supabase.table("lead_conversations").insert({
            "customer_name": "System",
            "customer_phone": lead["phone"],
            "last_message": f"[AUTO] Follow-up Day {lead['days_since']}",
            "ai_summary": lead["template"],
            "status": "FOLLOW_UP"
        }).execute()
        
        return True
    except Exception as e:
        print(f"❌ Failed to send follow-up to {lead['phone']}: {e}")
        return False


def run_follow_up_job():
    """Main function to run the follow-up automation."""
    print(f"🔄 Running follow-up job at {datetime.now()}")
    
    leads = get_leads_needing_followup()
    print(f"📋 Found {len(leads)} leads needing follow-up")
    
    success_count = 0
    for lead in leads:
        if send_follow_up(lead):
            success_count += 1
    
    print(f"✅ Sent {success_count}/{len(leads)} follow-ups")
    return success_count


if __name__ == "__main__":
    run_follow_up_job()
