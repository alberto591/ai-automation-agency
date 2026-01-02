#!/usr/bin/env python3
"""
Apply Appraisal Validations Enhancement Migration

Adds missing columns (zone, city, fifi_status, alert_triggered, etc.)
to the appraisal_validations table.

Usage:
    python scripts/apply_appraisal_validations_migration.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def apply_migration():
    """Apply the appraisal validations enhancement migration."""

    print("🔄 Applying Appraisal Validations Enhancement Migration...")
    print("=" * 60)

    migration_path = (
        Path(__file__).parent / "migrations" / "20260101_appraisal_validations_enhancement.sql"
    )

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False

    with open(migration_path) as f:
        migration_sql = f.read()

    print(f"\n📄 Migration file: {migration_path.name}")
    print(f"📏 Size: {len(migration_sql)} bytes")
    print("\n⚠️  Note: Supabase Python SDK doesn't support direct SQL execution.")
    print("\n📋 Please run this migration manually via one of these methods:")
    print("\n1. **Supabase Dashboard → SQL Editor**")
    print("   - Navigate to: https://app.supabase.com/project/[project-id]/sql")
    print(f"   - Copy and paste the contents of: {migration_path}")
    print("   - Click 'Run'")
    print("\n2. **psql Command Line**")
    print("   - Get connection string from Supabase Dashboard")
    print(f"   - Run: psql [connection-string] -f {migration_path}")
    print("\n3. **SQL Preview:**")
    print("-" * 60)
    print(migration_sql)
    print("-" * 60)

    # Try to verify current schema
    try:
        adapter = SupabaseAdapter()
        result = adapter.client.table("appraisal_validations").select("*").limit(1).execute()

        if result.data:
            print("\n✅ appraisal_validations table exists")
            print(f"📊 Current columns: {', '.join(result.data[0].keys())}")
        else:
            print("\n✅ appraisal_validations table exists (no data yet)")

    except Exception as e:
        logger.error("Schema check failed", context={"error": str(e)})
        print(f"\n⚠️  Could not verify current schema: {e}")

    return True


if __name__ == "__main__":
    logger.info("Starting Appraisal Validations Enhancement migration...")
    success = apply_migration()

    if success:
        print("\n✅ Migration instructions provided")
        print("⚠️  Please apply manually via Supabase Dashboard or psql")
    else:
        print("\n❌ Migration preparation failed")
        sys.exit(1)
