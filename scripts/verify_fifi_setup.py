#!/usr/bin/env python3
"""
Verify Fifi data pipeline setup.

Checks:
- Database connection
- Tables exist
- Sample data quality
- Feature engineering works
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def verify_database_connection():
    """Test Supabase connection."""
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_key)
        result = client.table("leads").select("id").limit(1).execute()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_tables_exist():
    """Verify Fifi tables exist."""
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_key)

        tables_to_check = [
            "historical_transactions",
            "property_features_stats",
            "appraisal_validations",
        ]

        for table in tables_to_check:
            try:
                result = client.table(table).select("*").limit(1).execute()
                print(f"✅ Table exists: {table}")
            except Exception as e:
                print(f"❌ Table missing: {table} - {str(e)[:50]}")
                return False

        return True
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False


def check_transaction_data():
    """Check if historical_transactions has data."""
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_key)

        result = client.table("historical_transactions").select("*", count="exact").execute()

        count = result.count if hasattr(result, "count") else len(result.data)
        print(f"📊 Historical transactions: {count} records")

        if count > 0:
            # Sample data
            sample = result.data[0] if result.data else {}
            print(f"   Sample zone: {sample.get('zone', 'N/A')}")
            print(f"   Sample price: €{sample.get('sale_price_eur', 0):,}")
            print("✅ Transaction data loaded")
            return True
        else:
            print("⚠️  No transaction data found")
            print("   Run: scripts/migrations/mock_data_insert.sql in Supabase")
            return False

    except Exception as e:
        print(f"❌ Data check failed: {e}")
        return False


def test_feature_engineering():
    """Test if feature engineering works."""
    try:
        from infrastructure.ml.feature_engineering import FeatureEngineer

        engineer = FeatureEngineer()
        print("✅ Feature engineering module loaded")
        return True
    except Exception as e:
        print(f"⚠️  Feature engineering not ready: {str(e)[:100]}")
        return False


def main():
    """Run all verification checks."""
    print("🏠 Fifi Data Pipeline Verification\n")
    print("=" * 50)

    checks = [
        ("Database Connection", verify_database_connection),
        ("Table Structure", check_tables_exist),
        ("Transaction Data", check_transaction_data),
        ("Feature Engineering", test_feature_engineering),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n{name}:")
        print("-" * 50)
        result = check_fn()
        results.append(result)

    print("\n" + "=" * 50)
    print("\nSummary:")
    passed = sum(results)
    total = len(results)
    print(f"  Checks passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All checks passed! Pipeline ready for ML training.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review output above.")
        print("\n📖 Next steps:")
        print("  1. Run migration: scripts/migrations/20251230_fifi_avm_foundation.sql")
        print("  2. Load data: scripts/migrations/mock_data_insert.sql")
        print("  3. See guide: docs/guides/fifi-database-setup.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
