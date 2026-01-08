import redis  # type: ignore

from domain.ports import CachePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class RedisAdapter(CachePort):
    def __init__(self, redis_url: str):
        self.url = redis_url
        self._client = None
        if redis_url:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
                self._client.ping()
                logger.info("REDIS_CONNECTED", context={"url": redis_url})
            except Exception as e:
                logger.error("REDIS_CONNECTION_FAILED", context={"error": str(e)})
                self._client = None
        else:
            logger.warning("REDIS_URL_NOT_SET")

    def get(self, key: str) -> str | None:
        if not self._client:
            return None
        try:
            result: str | None = self._client.get(key)
            return result
        except Exception as e:
            logger.error("REDIS_GET_FAILED", context={"key": key, "error": str(e)})
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        if not self._client:
            return
        try:
            self._client.setex(key, ttl, value)
        except Exception as e:
            logger.error("REDIS_SET_FAILED", context={"key": key, "error": str(e)})

    def delete(self, key: str) -> None:
        if not self._client:
            return
        try:
            self._client.delete(key)
        except Exception as e:
            logger.error("REDIS_DELETE_FAILED", context={"key": key, "error": str(e)})


class InMemoryCacheAdapter(CachePort):
    """Fallback cache if Redis is not available."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        logger.info("IN_MEMORY_CACHE_INITIALIZED")

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        # Simplistic in-memory cache without TTL for demo/fallback
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
