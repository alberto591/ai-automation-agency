"""Pydantic v1/v2 compatibility shim."""
try:
    # Pydantic v2
    from pydantic import model_validator  # noqa: F401
except ImportError:
    # Fallback for Pydantic v1
    from collections.abc import Callable
    from typing import Any

    def model_validator(  # type: ignore[no-redef]
        *args: Any, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """No-op shim for Pydantic v1 compatibility."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            return fn

        return decorator
