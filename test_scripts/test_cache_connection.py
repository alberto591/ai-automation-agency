import asyncio
import os
import sys
from datetime import UTC, datetime

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


async def test_cache():
    try:
        print("🚀 Initializing SupabaseAdapter...")
        db = SupabaseAdapter()

        test_query = f"test_query_{datetime.now(UTC).timestamp()}"
        test_embedding = [0.1] * 1024  # Standard 1024d embedding
        test_response = "This is a test response for the semantic cache."

        print(f"📝 Attempting to save to cache: {test_query}")
        db.save_to_cache(test_query, test_embedding, test_response)

        # We need to wait a moment or just try to retrieve it
        print("🔍 Attempting to retrieve from cache...")
        cached_response = db.get_cached_response(test_embedding, threshold=0.99)

        if cached_response == test_response:
            print("✅ SUCCESS: Cache write and read verified!")
        else:
            print(f"❌ FAILURE: Cached response mismatch or not found. Got: {cached_response}")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(test_cache())
