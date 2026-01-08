import dotenv

from config.container import container

dotenv.load_dotenv()


def verify_aggregated_report():
    print("\n--- Verifying Real Lead Aggregation ---")

    # 1. Take a lead and a property
    # Let's find any existing lead and property
    lead_res = container.db.client.table("leads").select("customer_phone").limit(1).execute()
    prop_res = container.db.client.table("properties").select("id").limit(1).execute()

    if not lead_res.data or not prop_res.data:
        print("❌ Not enough data in DB to verify. Need at least 1 lead and 1 property.")
        return

    phone = lead_res.data[0]["customer_phone"]
    prop_id = prop_res.data[0]["id"]

    print(f"Simulating interest for lead {phone} on property {prop_id}...")

    # 2. Trigger property brochure send
    # This should update metadata
    container.journey.send_property_brochure(phone, {"id": prop_id, "title": "Test Property"})

    # 3. Check metadata
    updated_lead = container.db.get_lead(phone)
    meta = updated_lead.get("metadata") or {}
    interests = meta.get("interested_property_ids", [])

    if prop_id in interests:
        print(f"✅ Metadata updated successfully. Interests: {interests}")
    else:
        print(f"❌ Metadata NOT updated. Found: {interests}")

    # 4. (Optional) Check report data via internal query logic
    # We want to see if the count for this prop_id is correct
    leads_res = container.db.client.table("leads").select("id, metadata").execute()
    count = 0
    for lead in leads_res.data:
        interest = (lead.get("metadata") or {}).get("interested_property_ids", [])
        if prop_id in interest:
            count += 1

    print(f"✅ Query check: Found {count} interested leads for property {prop_id}.")


if __name__ == "__main__":
    verify_aggregated_report()
