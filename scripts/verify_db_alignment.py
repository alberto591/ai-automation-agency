import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infrastructure.adapters.supabase_adapter import SupabaseAdapter

REQUIRED_COLUMNS = [
    "price_per_mq",
    "zone",
    "has_terrace",
    "has_garden",
    "has_parking",
    "has_air_conditioning",
    "condition",
    "heating_type",
    "construction_year",
    "images",
]


def verify_schema():
    print("🔍 Checking Supabase Schema Alignment...")
    db = SupabaseAdapter()

    try:
        # Fetch one property to check columns
        props = db.get_properties("", limit=1)
        if not props:
            print("❌ No properties found to check schema. Please add at least one property.")
            return

        current_columns = props[0].keys()
        missing = [col for col in REQUIRED_COLUMNS if col not in current_columns]

        if not missing:
            print("✅ Database schema is PERFECTLY aligned with real estate standards!")
        else:
            print(f"⚠️  Missing Columns: {missing}")
            print(
                "\n👉 To fix this, please run the SQL migration found in 'db_alignment_plan.md' inside your Supabase SQL Editor."
            )

    except Exception as e:
        print(f"❌ Error during verification: {e}")


if __name__ == "__main__":
    verify_schema()
