"""Redis-backed cache with fallback to in-memory cache."""
import hashlib
import json
from datetime import timedelta

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from infrastructure.cache.perplexity_cache import PerplexityCache
from infrastructure.logging import get_logger
from infrastructure.metrics import cache_hits_total, cache_misses_total

logger = get_logger(__name__)


class RedisPerplexityCache:
    """
    Redis-backed cache with automatic fallback to in-memory cache.
    Provides production-ready caching with persistence.
    """

    def __init__(self, redis_url: str | None = None, ttl_hours: int = 24):
        """
        Initialize Redis cache with fallback.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            ttl_hours: Time-to-live in hours
        """
        self._ttl_seconds = int(timedelta(hours=ttl_hours).total_seconds())
        self._fallback = PerplexityCache(ttl_hours=ttl_hours)
        self._use_redis = False

        if redis_url and REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(
                    redis_url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2
                )
                # Test connection
                self._redis.ping()
                self._use_redis = True
                logger.info(
                    "REDIS_CACHE_INITIALIZED", context={"url": redis_url, "ttl_hours": ttl_hours}
                )
            except Exception as e:
                logger.warning(
                    "REDIS_UNAVAILABLE", context={"error": str(e), "fallback": "in-memory"}
                )
                self._use_redis = False
        else:
            if not REDIS_AVAILABLE:
                logger.warning("REDIS_NOT_INSTALLED", context={"fallback": "in-memory"})
            logger.info("CACHE_INITIALIZED", context={"type": "in-memory", "ttl_hours": ttl_hours})

    def _generate_key(self, city: str, zone: str, property_type: str, surface_sqm: int) -> str:
        """Generate cache key from query parameters."""
        key_data = {
            "city": city.lower().strip(),
            "zone": zone.strip(),
            "property_type": property_type.lower().strip(),
            "surface_sqm": surface_sqm,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        hash_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"perplexity:{hash_key}"

    def get(self, city: str, zone: str, property_type: str, surface_sqm: int) -> str | None:
        """Retrieve cached response if available."""
        key = self._generate_key(city, zone, property_type, surface_sqm)

        if self._use_redis:
            try:
                value = self._redis.get(key)
                if value:
                    cache_hits_total.labels(cache_type="redis").inc()
                    logger.info("REDIS_CACHE_HIT", context={"key": key[:20]})
                    return value
                else:
                    cache_misses_total.labels(cache_type="redis").inc()
                    logger.info("REDIS_CACHE_MISS", context={"key": key[:20]})
                    return None
            except Exception as e:
                logger.error("REDIS_GET_ERROR", context={"error": str(e)})
                # Fallback to in-memory
                return self._fallback.get(city, zone, property_type, surface_sqm)
        else:
            return self._fallback.get(city, zone, property_type, surface_sqm)

    def set(self, city: str, zone: str, property_type: str, surface_sqm: int, value: str) -> None:
        """Store response in cache."""
        key = self._generate_key(city, zone, property_type, surface_sqm)

        if self._use_redis:
            try:
                self._redis.setex(key, self._ttl_seconds, value)
                logger.info(
                    "REDIS_CACHE_SET", context={"key": key[:20], "value_length": len(value)}
                )
            except Exception as e:
                logger.error("REDIS_SET_ERROR", context={"error": str(e)})
                # Fallback to in-memory
                self._fallback.set(city, zone, property_type, surface_sqm, value)
        else:
            self._fallback.set(city, zone, property_type, surface_sqm, value)

    def clear(self) -> None:
        """Clear all cached entries."""
        if self._use_redis:
            try:
                # Delete all keys matching pattern
                keys = self._redis.keys("perplexity:*")
                if keys:
                    self._redis.delete(*keys)
                logger.info("REDIS_CACHE_CLEARED", context={"keys_removed": len(keys)})
            except Exception as e:
                logger.error("REDIS_CLEAR_ERROR", context={"error": str(e)})
        else:
            self._fallback.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        stats = {
            "backend": "redis" if self._use_redis else "in-memory",
            "ttl_hours": self._ttl_seconds / 3600,
        }

        if self._use_redis:
            try:
                info = self._redis.info("stats")
                stats["redis_keys"] = self._redis.dbsize()
                stats["redis_hits"] = info.get("keyspace_hits", 0)
                stats["redis_misses"] = info.get("keyspace_misses", 0)
            except Exception:
                pass

        return stats
