import json
import logging
import traceback
from datetime import UTC, datetime
from typing import Any


class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)

    def _log(
        self, level: int, event: str, context: dict[str, Any] | None = None, exc_info: bool = False
    ) -> None:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": logging.getLevelName(level),
            "event": event,
            "context": context or {},
        }
        if exc_info:
            log_data["exception"] = traceback.format_exc()

        # In a real environment, we'd use a JSON formatter.
        # For now, we'll just print structured text.
        self.logger.log(level, json.dumps(log_data))

    def info(self, event: str, *, context: dict[str, Any] | None = None) -> None:
        self._log(logging.INFO, event, context=context)

    def error(
        self, event: str, *, context: dict[str, Any] | None = None, exc_info: bool = True
    ) -> None:
        self._log(logging.ERROR, event, context=context, exc_info=exc_info)

    def warning(self, event: str, *, context: dict[str, Any] | None = None) -> None:
        self._log(logging.WARNING, event, context=context)


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)
