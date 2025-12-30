import threading
import time
from collections import defaultdict

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Thread-safe rate limiter using a sliding window algorithm.
    Tracks messages per identifier (e.g., phone number) with timestamps.
    """

    def __init__(self, max_messages: int, window_seconds: int):
        """
        Initialize the rate limiter.

        Args:
            max_messages: Maximum number of messages allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if the identifier is within rate limits.

        Args:
            identifier: Unique identifier (e.g., phone number)

        Returns:
            True if within limits, False if rate limit exceeded
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - self.window_seconds

            # Remove timestamps outside the window
            self._timestamps[identifier] = [
                ts for ts in self._timestamps[identifier] if ts > cutoff_time
            ]

            # Check if we're within the limit
            if len(self._timestamps[identifier]) >= self.max_messages:
                logger.warning(
                    "RATE_LIMIT_EXCEEDED",
                    context={
                        "identifier": identifier,
                        "count": len(self._timestamps[identifier]),
                        "limit": self.max_messages,
                        "window_seconds": self.window_seconds,
                    },
                )
                return False

            # Add current timestamp
            self._timestamps[identifier].append(current_time)
            return True

    def get_remaining(self, identifier: str) -> int:
        """
        Get the number of remaining messages allowed for the identifier.

        Args:
            identifier: Unique identifier (e.g., phone number)

        Returns:
            Number of messages remaining in the current window
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - self.window_seconds

            # Remove timestamps outside the window
            self._timestamps[identifier] = [
                ts for ts in self._timestamps[identifier] if ts > cutoff_time
            ]

            return max(0, self.max_messages - len(self._timestamps[identifier]))

    def reset(self, identifier: str) -> None:
        """
        Reset the rate limit for a specific identifier.

        Args:
            identifier: Unique identifier to reset
        """
        with self._lock:
            if identifier in self._timestamps:
                del self._timestamps[identifier]
                logger.info("RATE_LIMIT_RESET", context={"identifier": identifier})
