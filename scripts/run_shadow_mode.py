import asyncio
import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.validation_adapter import PostgresValidationAdapter
from infrastructure.logging import get_logger
from infrastructure.ml.feature_engineering import PropertyFeatures
from infrastructure.ml.xgboost_adapter import XGBoostAdapter

logger = get_logger(__name__)


async def main():  # noqa: PLR0912, PLR0915
    print("🚀 Starting Shadow Mode Simulation...")

    # 1. Initialize Adapters
    try:
        db = PostgresValidationAdapter()
        ml = XGBoostAdapter()
        print("✅ Adapters initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize adapters: {e}")
        return

    # 2. Fetch Data (Simulate Feed from Historical Transactions)
    # We try historical first, then properties if empty (for testing)
    transactions = []
    try:
        print("🔍 Fetching historical transactions...")
        res = db.client.table("historical_transactions").select("*").limit(50).execute()
        transactions = res.data if res.data else []
    except Exception as e:
        print(f"⚠️ Error fetching historical_transactions: {e}")
        transactions = []

    if not transactions:
        print("⚠️ historical_transactions empty or missing. Trying 'properties' table...")
        try:
            res = db.client.table("properties").select("*").limit(50).execute()
            transactions = res.data if res.data else []
        except Exception as e:
            print(f"❌ Failed to fetch any data: {e}")
            return

    if not transactions:
        print("⚠️ No data found to simulate.")
        return

    print(f"Found {len(transactions)} listings to process.")

    # 3. Process Logic
    success_count = 0
    drift_alerts = 0

    for tx in transactions:
        try:
            # Map DB row to PropertyFeatures
            # Handle different schemas (historical vs properties)
            price = tx.get("sale_price_eur") or tx.get("price")
            sqm = tx.get("sqm") or tx.get("surface")

            if not price or not sqm:
                continue

            features = PropertyFeatures(
                sqm=int(sqm),
                bedrooms=tx.get("bedrooms", 2),
                bathrooms=tx.get("bathrooms", 1),
                floor=tx.get("floor", 1),
                has_elevator=tx.get("has_elevator", False),
                condition=tx.get("condition", "good"),  # type: ignore
                zone_slug=(tx.get("zone") or "unknown").lower().replace(" ", "-"),
                property_age_years=tx.get("property_age_years", 30),
            )

            # Predict
            predicted_value = ml.predict(features)

            # Validate
            # We treat the DB price as "Actual" (Sale or Listing)
            price_type = "sale" if "sale_price_eur" in tx else "listing"

            # Calculate metrics
            comparables = [
                {"sale_price_eur": price}
            ]  # Dummy comp for uncertainty if needed, or fetch real ones
            uncertainty = ml.calculate_uncertainty(predicted_value, comparables)

            # Log to DB
            metadata = {
                "zone": features.zone_slug,
                "city": tx.get("city", "Unknown"),
                "price_type": price_type,
                "fifi_status": "SHADOW_MODE",
            }

            db.log_validation(
                predicted_value=int(predicted_value),
                actual_value=int(price),
                metadata=metadata,
                uncertainty_score=uncertainty,
                model_version=ml.model_version,
            )

            success_count += 1

            # Check for local alert in script output
            error_pct = abs((predicted_value - price) / price)
            if error_pct > 0.20:
                print(
                    f"⚠️ Drift Alert: {features.zone_slug} | Pred: €{predicted_value:,.0f} | Act: €{price:,.0f} | Error: {error_pct:.1%}"
                )
                drift_alerts += 1

        except Exception as e:
            logger.error("SHADOW_PROCESS_FAILED", context={"id": tx.get("id"), "error": str(e)})

    print("\n✅ Shadow Mode Complete.")
    print(f"Processed: {success_count}/{len(transactions)}")
    print(f"Drift Alerts: {drift_alerts}")

    # Check Zone Drift
    print("\n🔍 Checking Zone-Level Drift...")
    zones = set([(t.get("zone") or "unknown").lower().replace(" ", "-") for t in transactions])
    for z in zones:
        if z and db.detect_drift(z):
            print(f"🚨 PERSISTENT DRIFT DETECTED IN ZONE: {z}")


if __name__ == "__main__":
    asyncio.run(main())
