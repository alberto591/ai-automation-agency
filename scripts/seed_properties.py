#!/usr/bin/env python3
"""
Property Seeder Script

Loads properties from a CSV file into Supabase.
Supports tagging data as 'mock' for safe testing.

Usage:
    python scripts/seed_properties.py --mock         # Seed as mock data
    python scripts/seed_properties.py --prod         # Seed as production data
    python scripts/seed_properties.py --clear-mock   # Delete ONLY mock data
"""

import csv
import sys
import os
import argparse
from typing import Any

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)

def load_csv(filepath: str) -> list[dict[str, Any]]:
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    parser = argparse.ArgumentParser(description="Seed properties into Supabase")
    parser.add_argument("--mock", action="store_true", help="Flag data as mock")
    parser.add_argument("--prod", action="store_true", help="Flag data as production")
    parser.add_argument("--clear-mock", action="store_true", help="Delete all mock data")
    parser.add_argument("--file", default="properties_sample.csv", help="CSV file to load")
    
    args = parser.parse_args()
    db = SupabaseAdapter()

    # 1. Clear Mock Data
    if args.clear_mock:
        print("🗑️  Clearing mock data...")
        try:
            db.client.table("mock_properties").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("✅ Mock data cleared.")
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
        return

    # 2. Validation
    if not args.mock and not args.prod:
        print("⚠️  Please specify --mock or --prod")
        return

    is_mock = args.mock
    target_table = "mock_properties" if is_mock else "properties"
    print(f"📦 Seeding {target_table} (MOCK={is_mock}) from {args.file}...")

    # 3. Load Data
    rows = load_csv(args.file)
    if not rows:
        return

    # 4. Transform & Insert
    count = 0
    for row in rows:
        try:
            # Basic validation/transformation
            data = {
                "title": row.get("title"),
                "description": row.get("description"),
                "price": float(row.get("price", 0)),
                "sqm": int(row.get("sqm", 0)) if row.get("sqm") else None,
                "rooms": int(row.get("rooms", 0)) if row.get("rooms") else None,
                "bathrooms": int(row.get("bathrooms", 0)) if row.get("bathrooms") else None,
                "floor": int(row.get("floor", 0)) if row.get("floor") else None,
                "energy_class": row.get("energy_class"),
                "has_elevator": str(row.get("has_elevator", "")).lower() == 'true',
                "status": row.get("status", "available"),
                "image_url": row.get("image_url"),
                # is_mock removed as it's no longer a column
            }
            
            # Remove keys that might not exist in target schema if CSV is messy
            # (Assuming supabase_adapter handles upsert logic or we use raw client here)
            
            # Using raw client for bulk/batch might be better, but loop is safer for validation
            db.client.table(target_table).insert(data).execute()
            count += 1
            print(f"  ✅ Added: {data['title']}")
        except Exception as e:
            print(f"  ❌ Failed to add {row.get('title', 'Unknown')}: {e}")

    print(f"\n✨ Done! Added {count} properties.")

if __name__ == "__main__":
    main()
