import json

import requests

API_BASE = "http://localhost:8000"


def test_appraisal_and_feedback():
    print("🚀 Starting End-to-End Testing...")

    # 1. Test Appraisal (Florence Centro)
    print("\n1️⃣ Testing Appraisal: Firenze Centro (150sqm)...")
    appraisal_payload = {
        "city": "Florence",
        "zone": "Centro",
        "surface_sqm": 150,
        "condition": "luxury",
        "phone": "+393406789123",
    }

    try:
        response = requests.post(f"{API_BASE}/api/appraisals/estimate", json=appraisal_payload)
        response.raise_for_status()
        data = response.json()

        appraisal_id = data.get("id")
        estimated_value = data.get("estimated_value")
        comparables = data.get("comparables", [])

        print("  ✅ Appraisal Successful!")
        print(f"  💰 Estimated Value: €{estimated_value:,.2f}")
        print(f"  📍 Appraisal ID: {appraisal_id}")
        print(f"  🔍 Found {len(comparables)} comparables.")

        # Check for our seeded property
        found_premium = any("Attico Prestigioso" in c["title"] for c in comparables)
        if found_premium:
            print("  ✨ SUCCESS: Found the seeded premium Duomo apartment!")
        else:
            print("  ⚠️ WARNING: Seeded premium property not found in results.")

        # 2. Test Feedback Submission
        if appraisal_id:
            print(f"\n2️⃣ Submitting Feedback for Appraisal {appraisal_id}...")
            feedback_payload = {
                "appraisal_id": appraisal_id,
                "rating": 5,
                "speed_rating": 5,
                "accuracy_rating": 5,
                "feedback_text": "Ottimo strumento! Molto veloce e preciso sulla zona del Duomo di Firenze.",
                "appraisal_phone": "+393406789123",
            }

            fb_response = requests.post(f"{API_BASE}/api/feedback/submit", json=feedback_payload)
            fb_response.raise_for_status()
            fb_data = fb_response.json()

            print(f"  ✅ Feedback Submitted! ID: {fb_data.get('feedback_id')}")

        # 3. Verify Performance Stats
        print("\n3️⃣ Verifying Performance Dashboard Stats...")
        stats_response = requests.get(f"{API_BASE}/api/monitoring/performance?hours=1")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"  📊 Stats for last 1 hour: {json.dumps(stats, indent=2)}")
        else:
            print(f"  ❌ Failed to fetch stats: {stats_response.text}")
            print("  💡 HINT: This is likely the known Postgres type mismatch (Double vs Numeric).")
            print(
                "  👉 Action: Please re-apply the get_performance_stats function from docs/sql/20260103_phase3_optimization_indexes.sql"
            )

    except Exception as e:
        print(f"  ❌ TEST FAILED: {str(e)}")


if __name__ == "__main__":
    test_appraisal_and_feedback()
