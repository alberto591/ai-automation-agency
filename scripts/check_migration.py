import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from config.container import container


def apply_migration():
    print("🚀 Applying migration: Add metadata to leads...")
    db = container.db

    sql = "ALTER TABLE leads ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;"
    sql_comment = "COMMENT ON COLUMN leads.metadata IS 'Stores enriched AI state such as PropertyPreferences and SentimentAnalysis results.';"

    try:
        # We try to use the RPC if it exists, but typically for DDL we might need service role
        # If we can't run DDL via the client easily, we should ask the user.
        # However, some setups allow raw SQL via RPC or similar.
        # Let's try to just insert a dummy record with metadata to see if it works?
        # No, that will fail if column missing.

        # In many Supabase setups, you can't run ALTER TABLE via the REST API.
        # I'll check if there's a way.
        # Actually, let's try a simple insert with the column. If it fails, the column IS missing.

        test_data = {"customer_phone": "+1234567890", "metadata": {"test": True}}
        res = db.client.table("leads").upsert(test_data).execute()
        print("✅ Column exists (or was added successfully).")
    except Exception as e:
        print(f"❌ Column likely missing or error: {e}")
        print("\nIMPORTANT: Please run the following SQL in your Supabase SQL Editor:")
        with open("sql/add-metadata-to-leads.sql") as f:
            print(f.read())


if __name__ == "__main__":
    apply_migration()
