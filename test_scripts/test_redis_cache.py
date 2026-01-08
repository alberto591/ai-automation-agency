import os

import dotenv

from infrastructure.adapters.cache_adapter import RedisAdapter

dotenv.load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


def test_redis():
    print(f"Testing Redis at: {REDIS_URL}")
    if not REDIS_URL:
        print("❌ REDIS_URL not set in .env")
        return

    try:
        adapter = RedisAdapter(REDIS_URL)
        adapter.set("test_key", "test_value", ttl=10)
        val = adapter.get("test_key")
        if val == "test_value":
            print("✅ Redis SET/GET successful.")
        else:
            print(f"❌ Redis mismatch: expected 'test_value', got '{val}'")
    except Exception as e:
        print(f"❌ Redis test failed: {e}")


if __name__ == "__main__":
    test_redis()
