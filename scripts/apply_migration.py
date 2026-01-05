import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def apply_migration(sql_file: str):
    """Reads and applies a SQL migration file."""
    try:
        db = SupabaseAdapter()

        with open(sql_file) as f:
            sql_content = f.read()

        logger.info("APPLYING_MIGRATION", context={"file": sql_file})

        # Supabase-py doesn't have a direct raw SQL method exposed easily without RPC
        # But for this purpose, we might need to use the 'rpc' call if a 'exec_sql' function exists
        # OR we can try to use a REST endpoint if available.
        # However, looking at the adapter, let's see if we can use the client directly or if we need a workaround.

        # NOTE: The python client for supabase is limited for DDL.
        # We often need to use the postgres connection string for migrations,
        # or an RPC function 'exec_sql' if we enabled it.
        # Let's assume we can try to use the REST API via a special RPC if it exists,
        # OR we check if there's a psycopg2 connection string in env.

        # CHECKING FOR 'DATABASE_URL'
        db_url = os.getenv("DATABASE_URL")  # This is usually needed for DDL
        if db_url:
            import psycopg2

            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            conn.close()
            print("Migration applied successfully via psycopg2.")
            return

        # Fallback: Try a known RPC function 'exec_sql' often added for tools
        try:
            # This is a shot in the dark if DATABASE_URL isn't set, depending on project setup
            res = db.client.rpc("exec_sql", {"sql_query": sql_content}).execute()
            print(f"Migration applied via RPC: {res}")
        except Exception as e:
            print(f"RPC/Fallback failed: {e}")
            print("CRITICAL: DATABASE_URL not found and RPC failed. Cannot apply DDL.")
            sys.exit(1)

    except Exception as e:
        logger.error("MIGRATION_FAILED", context={"error": str(e)})
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/apply_migration.py <path_to_sql_file>")
        sys.exit(1)

    apply_migration(sys.argv[1])
