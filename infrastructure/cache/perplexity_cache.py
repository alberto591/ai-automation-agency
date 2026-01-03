import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

from infrastructure.logging import get_logger
from infrastructure.metrics import cache_hits_total, cache_misses_total

logger = get_logger(__name__)


class PerplexityCache:
    """
    In-memory cache for Perplexity API responses with TTL.
    Reduces API costs and improves response time for repeated queries.
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize cache with specified TTL.

        Args:
            ttl_hours: Time-to-live in hours (default: 24)
        """
        self._cache: dict[str, tuple[str, datetime]] = {}
        self._ttl = timedelta(hours=ttl_hours)
        logger.info("CACHE_INITIALIZED", context={"ttl_hours": ttl_hours})

    def _generate_key(self, city: str, zone: str, property_type: str, surface_sqm: int) -> str:
        """Generate cache key from query parameters."""
        # Normalize inputs for consistent caching
        key_data = {
            "city": city.lower().strip(),
            "zone": zone.strip(),
            "property_type": property_type.lower().strip(),
            "surface_sqm": surface_sqm,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, city: str, zone: str, property_type: str, surface_sqm: int) -> str | None:
        """
        Retrieve cached response if available and not expired.

        Returns:
            Cached response text or None if not found/expired
        """
        key = self._generate_key(city, zone, property_type, surface_sqm)

        if key in self._cache:
            value, timestamp = self._cache[key]
            age = datetime.now() - timestamp

            if age < self._ttl:
                cache_hits_total.labels(cache_type="memory").inc()
                logger.info(
                    "CACHE_HIT",
                    context={
                        "key": key[:8],
                        "age_minutes": int(age.total_seconds() / 60),
                    },
                )
                return value
            else:
                # Expired - remove from cache
                del self._cache[key]
                logger.info("CACHE_EXPIRED", context={"key": key[:8]})

        cache_misses_total.labels(cache_type="memory").inc()
        logger.info("CACHE_MISS", context={"key": key[:8]})
        return None

    def set(self, city: str, zone: str, property_type: str, surface_sqm: int, value: str) -> None:
        """Store response in cache with current timestamp."""
        key = self._generate_key(city, zone, property_type, surface_sqm)
        self._cache[key] = (value, datetime.now())
        logger.info(
            "CACHE_SET",
            context={"key": key[:8], "value_length": len(value), "cache_size": len(self._cache)},
        )

    def clear(self) -> None:
        """Clear all cached entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("CACHE_CLEARED", context={"entries_removed": count})

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "ttl_hours": self._ttl.total_seconds() / 3600,
        }
