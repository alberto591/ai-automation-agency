#!/usr/bin/env python3
"""
Apply Fifi AVM Foundation Migration

This script applies the database schema for Fifi AI Appraisal:
- historical_transactions table
- property_features_stats table
- appraisal_validations table
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.supabase_adapter import get_supabase_client
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def apply_migration():
    """Apply the Fifi AVM foundation migration."""
    client = get_supabase_client()

    # Read migration SQL
    migration_path = Path(__file__).parent / "20251230_fifi_avm_foundation.sql"
    with open(migration_path) as f:
        migration_sql = f.read()

    # Split into individual statements
    statements = [
        s.strip() for s in migration_sql.split(";") if s.strip() and not s.strip().startswith("--")
    ]

    logger.info(f"Applying {len(statements)} SQL statements...")

    for i, statement in enumerate(statements, 1):
        try:
            # Execute via Supabase RPC or direct SQL
            # Note: Supabase Python client doesn't support direct SQL execution
            # This would need to be run via psql or Supabase dashboard
            logger.info(f"Statement {i}/{len(statements)}: {statement[:50]}...")
            print(f"✅ Statement {i} prepared")
        except Exception as e:
            logger.error(f"Error on statement {i}: {e}")
            print(f"❌ Error: {e}")
            return False

    print("\n⚠️  Note: Supabase Python SDK doesn't support direct SQL execution.")
    print("📋 Please run this migration manually via:")
    print("   1. Supabase Dashboard → SQL Editor")
    print("   2. Or: psql with connection string")
    print(f"   3. Migration file: {migration_path}")

    return True


if __name__ == "__main__":
    logger.info("Starting Fifi AVM migration...")
    success = apply_migration()

    if success:
        print("\n✅ Migration preparation complete")
        print("⚠️  Manual execution required via Supabase Dashboard")
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
