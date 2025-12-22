import asyncio
import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


async def main():
    try:
        print("Initializing SupabaseAdapter...")
        db = SupabaseAdapter()

        print("Attempting to fetch properties...")
        properties = db.get_properties(query="", limit=1)

        if properties:
            print(f"SUCCESS: Fetched {len(properties)} properties.")
            print(f"Sample: {properties[0]['title']}")
        else:
            print("SUCCESS: Connection worked but no properties found.")

    except Exception as e:
        print(f"FAILURE: {e}")


if __name__ == "__main__":
    asyncio.run(main())
