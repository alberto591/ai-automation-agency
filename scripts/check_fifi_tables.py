#!/usr/bin/env python3
"""
Quick check if Fifi tables exist in Supabase.
Uses environment variables directly to avoid settings issues.
"""

import os
import sys

try:
    from supabase import create_client
except ImportError:
    print("❌ supabase-py not installed. Run: pip install supabase")
    sys.exit(1)


def check_fifi_tables():  # noqa: PLR0912, PLR0915
    """Check if Fifi tables exist and have data."""

    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        print("   Check your .env file")
        return False

    print("🏠 Fifi Tables Quick Check")
    print("=" * 50)
    print(f"Project: {supabase_url.split('//')[1].split('.')[0]}")
    print()

    try:
        client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        print()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Check tables
    tables = {
        "historical_transactions": "Property sales data",
        "property_features_stats": "Zone statistics",
        "appraisal_validations": "Performance tracking",
    }

    all_good = True

    for table, description in tables.items():
        try:
            result = client.table(table).select("*", count="exact").limit(1).execute()
            count = result.count if hasattr(result, "count") else len(result.data)

            if table == "historical_transactions":
                print(f"📊 {table}")
                print(f"   Description: {description}")
                print(f"   Records: {count}")

                if count > 0:
                    print("   ✅ Data loaded!")
                else:
                    print("   ⚠️  Table exists but no data")
                    print("   → Run: scripts/migrations/mock_data_insert.sql")
                    all_good = False
            else:
                print(f"✅ {table} - exists")

        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "relation" in error_msg:
                print(f"❌ {table} - NOT FOUND")
                print("   → Run: scripts/migrations/20251230_fifi_avm_foundation.sql")
                all_good = False
            else:
                print(f"⚠️  {table} - Error: {error_msg[:100]}")
                all_good = False
        print()

    print("=" * 50)
    if all_good:
        print("🎉 All checks passed! Fifi database ready.")
        print()
        print("Next: Train ML model or test appraisal API")
        return True
    else:
        print("⚠️  Setup incomplete")
        print()
        print("📖 See: docs/guides/fifi-database-setup.md")
        print(
            "🔗 Supabase: https://app.supabase.com/project/"
            + supabase_url.split("//")[1].split(".")[0]
            + "/sql"
        )
        return False


if __name__ == "__main__":
    # Load .env if present
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    success = check_fifi_tables()
    sys.exit(0 if success else 1)
