#!/usr/bin/env python3
"""
Check recent appraisal validations in the database.
Shows the most recent audit log entries to verify logging is working.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def check_appraisal_logs():
    """Check recent appraisal validation logs."""

    print("🔍 Checking Appraisal Validation Logs")
    print("=" * 70)

    try:
        adapter = SupabaseAdapter()

        # Get the 5 most recent appraisal validations
        result = (
            adapter.client.table("appraisal_validations")
            .select("*")
            .order("appraisal_date", desc=True)
            .limit(5)
            .execute()
        )

        if not result.data:
            print("\n📭 No appraisal validations found in database")
            print("   This is expected if this is the first run")
            return

        print(f"\n📊 Found {len(result.data)} recent validation(s)")
        print()

        for i, entry in enumerate(result.data, 1):
            print(f"{'─' * 70}")
            print(f"Validation #{i}")
            print(f"{'─' * 70}")
            print(f"📅 Date: {entry.get('appraisal_date', 'N/A')}")
            print(f"🏷️  Model: {entry.get('model_version', 'N/A')}")
            print(f"💶 Predicted: €{entry.get('predicted_value_eur', 0):,}")
            print(f"📍 Zone: {entry.get('zone', 'N/A')}")
            print(f"🏙️  City: {entry.get('city', 'N/A')}")
            print(f"📈 Uncertainty: {entry.get('uncertainty_score', 0):.4f}")
            print(f"✅ Status: {entry.get('fifi_status', 'N/A')}")
            print(f"🚨 Alert: {'Yes' if entry.get('alert_triggered') else 'No'}")

            if entry.get("actual_sale_price_eur"):
                print(f"💰 Actual Sale: €{entry.get('actual_sale_price_eur'):,}")
                print(f"📉 Error: {entry.get('error_pct', 0):.2f}%")
            elif entry.get("actual_listing_price_eur"):
                print(f"💰 Actual Listing: €{entry.get('actual_listing_price_eur'):,}")
                print(f"📉 Error: {entry.get('error_pct', 0):.2f}%")
            else:
                print("💰 Actual Price: (Pending sale validation)")

            print()

        # Summary stats
        print(f"{'=' * 70}")
        print("📊 Summary Statistics")
        print(f"{'=' * 70}")

        total_logged = len(result.data)
        auto_approved = sum(1 for e in result.data if e.get("fifi_status") == "AUTO_APPROVED")
        human_review = sum(
            1 for e in result.data if e.get("fifi_status") == "HUMAN_REVIEW_REQUIRED"
        )
        alerts = sum(1 for e in result.data if e.get("alert_triggered"))

        avg_uncertainty = (
            sum(e.get("uncertainty_score", 0) for e in result.data) / total_logged
            if total_logged > 0
            else 0
        )

        print(f"Total Validations: {total_logged}")
        print(f"Auto-Approved: {auto_approved}")
        print(f"Human Review: {human_review}")
        print(f"Alerts Triggered: {alerts}")
        print(f"Average Uncertainty: {avg_uncertainty:.4f}")
        print()

        return True

    except Exception as e:
        logger.error("Failed to check appraisal logs", context={"error": str(e)})
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = check_appraisal_logs()
    sys.exit(0 if success else 1)
