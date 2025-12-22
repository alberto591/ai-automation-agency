import asyncio
import os
import sys
import json

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)

async def migrate_data():
    print("🚀 Starting Data Migration (v1 -> v2)...")
    db = SupabaseAdapter()
    
    # 1. Fetch old data
    try:
        old_leads = db.client.table("lead_conversations").select("*").execute().data
        print(f"📦 Found {len(old_leads)} legacy leads to migrate.")
    except Exception as e:
        print(f"❌ Failed to fetch legacy data: {e}")
        return

    migrated_count = 0
    messages_count = 0

    for old_lead in old_leads:
        try:
            # 2. Insert into NEW leads table
            # Map fields safely
            lead_data = {
                "customer_phone": old_lead.get("customer_phone"),
                "customer_name": old_lead.get("customer_name"),
                "status": old_lead.get("status", "new").lower(),
                "is_ai_active": old_lead.get("is_ai_active", True),
                "budget_max": old_lead.get("budget_max"),
                "postcode": old_lead.get("postcode"),
                "preferred_zones": old_lead.get("preferred_zones"),
                "lead_type": old_lead.get("lead_type", "buyer"),
                "score": old_lead.get("score", 0),
                "created_at": old_lead.get("created_at"),
                "updated_at": old_lead.get("updated_at")
            }
            
            # Upsert into leads (using phone as key reference logic)
            # Fetch ID after insert to link messages
            res = db.client.table("leads").upsert(lead_data, on_conflict="customer_phone").execute()
            new_lead_id = res.data[0]["id"]
            
            # 3. Migrate Messages
            raw_messages = old_lead.get("messages")
            if raw_messages:
                # Handle both stringified JSON and direct list
                if isinstance(raw_messages, str):
                    try:
                        msg_list = json.loads(raw_messages)
                    except:
                        msg_list = []
                else:
                    msg_list = raw_messages
                
                for msg in msg_list:
                    msg_data = {
                        "lead_id": new_lead_id,
                        "role": msg.get("role", "system"),
                        "content": msg.get("content", ""),
                        "created_at": old_lead.get("updated_at") # Best guess timestamp
                    }
                    db.client.table("messages").insert(msg_data).execute()
                    messages_count += 1

            migrated_count += 1
            print(f"  ✅ Migrated: {old_lead.get('customer_name')} ({len(msg_list if raw_messages else [])} msgs)")

        except Exception as e:
            print(f"  ❌ Failed to migrate {old_lead.get('customer_phone')}: {e}")

    print(f"\n✨ Migration Complete!")
    print(f"   Leads: {migrated_count}")
    print(f"   Messages: {messages_count}")

if __name__ == "__main__":
    asyncio.run(migrate_data())
