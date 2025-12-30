import json
import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from config.container import container


def verify_real_appraisal():
    print("🚀 Verifying Real Appraisal Integration...")

    # Simulate a lead from the appraisal tool
    phone = "+393339998887"
    name = "Test Appraisal User"
    query = "RICHIESTA VALUTAZIONE: via Ghibellina, Firenze"
    postcode = "50122"

    print(f"📡 Sending request: {query} (POSTCODE: {postcode})")

    # Process
    response = container.lead_processor.process_lead(phone, name, query, postcode)

    print("\n🤖 AI RESPONSE:")
    print("-" * 30)
    print(response)
    print("-" * 30)

    # In Tuscany (Firenze), Expert Data should return ~4546/mq
    # AI should provide a range around that.

    if "4.546" in response or "4546" in response or ("4." in response and "500" in response):
        print("\n✅ SUCCESS: AI mentions real market data for Firenze!")
    else:
        print(
            "\n⚠️ WARNING: Market data not explicitly found in response text. Check if AI summarized it."
        )

    # Check lead metadata in DB
    lead = container.db.get_lead(phone)
    metadata = lead.get("metadata", {})
    print("\n📦 LEAD METADATA:")
    print(json.dumps(metadata, indent=2))

    if metadata.get("source") == "FIFI_APPRAISAL":
        print("✅ SUCCESS: Source correctly tagged as FIFI_APPRAISAL")
    else:
        print("❌ ERROR: Source tag missing or incorrect")


if __name__ == "__main__":
    verify_real_appraisal()
