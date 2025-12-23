#!/usr/bin/env python3
"""
Demo Data Generator

Populates the database with realistic test conversations for client demos.
Run this before showing the Google Sheets dashboard to make it look active.

Usage:
    python populate_demo_data.py
"""

import os
import sys
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
)

# Realistic Italian lead data
DEMO_CONVERSATIONS = [
    {
        "customer_name": "Laura Bianchi",
        "customer_phone": "+393331234567",
        "last_message": "Vorrei vedere la villa con piscina urgentemente",
        "ai_summary": "🔥 HOT LEAD (Score: 75) - Interessata a villa con piscina. Richiesta visita urgente.",
        "status": "New",
        "days_ago": 0,
    },
    {
        "customer_name": "Marco Ferrara",
        "customer_phone": "+393337654321",
        "last_message": "Il prezzo è trattabile?",
        "ai_summary": "⭐ Warm Lead (Score: 35) - Chiede negoziazione prezzo attico centro.",
        "status": "New",
        "days_ago": 1,
    },
    {
        "customer_name": "Giulia Rossi",
        "customer_phone": "+393339876543",
        "last_message": "Voglio parlare con un agente umano",
        "ai_summary": "Richiesta passaggio ad agente umano.",
        "status": "TAKEOVER",
        "days_ago": 1,
    },
    {
        "customer_name": "Roberto Colombo",
        "customer_phone": "+393335551234",
        "last_message": "Quanto costa il bilocale?",
        "ai_summary": "Richiesta informazioni bilocale zona universitaria. Score: 20",
        "status": "New",
        "days_ago": 2,
    },
    {
        "customer_name": "Alessia Romano",
        "customer_phone": "+393334447890",
        "last_message": "Ho budget €300k, cerco trilocale con terrazza",
        "ai_summary": "🔥 HOT LEAD (Score: 85) - Budget definito, richiesta specifica. Proposta 3 opzioni.",
        "status": "New",
        "days_ago": 2,
    },
    {
        "customer_name": "Francesco Ricci",
        "customer_phone": "+393336669999",
        "last_message": "Grazie per le info, ci penso",
        "ai_summary": "Richiesta follow-up tra 3 giorni. Score: 25",
        "status": "FOLLOW_UP",
        "days_ago": 3,
    },
]


def clear_existing_data():
    try:
        # Delete messages first due to FK
        supabase.table("messages").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        # Delete leads
        supabase.table("leads").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Existing data cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False


def populate_demo_conversations():
    """Adds realistic conversations for demo purposes"""

    print("📝 Populating demo conversations...")

    for conv in DEMO_CONVERSATIONS:
        # Calculate timestamp based on days_ago
        timestamp = (datetime.now(UTC) - timedelta(days=conv["days_ago"])).isoformat()

        lead_data = {
            "customer_name": conv["customer_name"],
            "customer_phone": conv["customer_phone"],
            "ai_summary": conv["ai_summary"],
            "status": conv["status"],
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        try:
            res = supabase.table("leads").insert(lead_data).execute()
            if res.data:
                lead_id = res.data[0]["id"]
                # Add the last message to messages table
                msg_data = {
                    "lead_id": lead_id,
                    "role": "user",
                    "content": conv["last_message"],
                    "created_at": timestamp,
                }
                supabase.table("messages").insert(msg_data).execute()
                print(f"  ✅ Added: {conv['customer_name']} ({conv['status']})")
        except Exception as e:
            print(f"  ❌ Failed to add {conv['customer_name']}: {e}")

    print("\n✅ Demo data populated!")
    print("\n📊 Summary:")
    print(f"   Total conversations: {len(DEMO_CONVERSATIONS)}")
    print(f"   Hot leads (🔥): {len([c for c in DEMO_CONVERSATIONS if '🔥' in c['ai_summary']])}")
    print(f"   Takeovers: {len([c for c in DEMO_CONVERSATIONS if c['status'] == 'TAKEOVER'])}")
    print("\n💡 Tip: Open your Google Sheet to see these conversations!")


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 50)
    print("🎭 DEMO DATA GENERATOR")
    print("=" * 50 + "\n")

    if "--clear" in sys.argv:
        # Dangerous option: clear then populate
        if clear_existing_data():
            print()
            populate_demo_conversations()
    else:
        # Safe option: just add demo data (keeps existing data)
        print("Mode: ADD ONLY (existing data will be kept)")
        print("Use --clear flag to delete existing data first\n")
        populate_demo_conversations()
