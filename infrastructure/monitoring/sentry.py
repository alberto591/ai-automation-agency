"""Sentry error monitoring and performance tracking.

Initializes Sentry for error tracking, performance monitoring,
and debugging in production environments.
"""

import logging
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from domain.services.logging import get_logger

logger = get_logger(__name__)


def init_sentry(
    dsn: str, environment: str = "development", traces_sample_rate: float = 1.0
) -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.

    Args:
        dsn: Sentry Data Source Name (project-specific URL)
        environment: Environment name (development, staging, production)
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
    """
    if not dsn:
        logger.warning("SENTRY_DISABLED", context={"reason": "No DSN provided"})
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            # Integrations
            integrations=[
                # FastAPI integration for automatic request tracking
                FastApiIntegration(
                    transaction_style="url",  # Group by URL pattern
                ),
                # Logging integration for breadcrumbs
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above
                    event_level=logging.ERROR,  # Send errors as events
                ),
            ],
            # Performance monitoring
            enable_tracing=True,
            # Release tracking (optional)
            # release="agenzia-ai@1.0.0",
            # Additional options
            attach_stacktrace=True,  # Include stack traces
            send_default_pii=False,  # Don't send personally identifiable info
            max_breadcrumbs=50,  # Keep last 50 breadcrumbs
            # Error filtering
            before_send=before_send_filter,
        )

        logger.info(
            "SENTRY_INITIALIZED",
            context={"environment": environment, "traces_sample_rate": traces_sample_rate},
        )

    except Exception as e:
        logger.error("SENTRY_INIT_FAILED", context={"error": str(e)}, exc_info=True)


def before_send_filter(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    """
    Filter events before sending to Sentry.

    Use this to:
    - Remove sensitive data
    - Filter out specific errors
    - Add custom context
    """
    # Example: Filter out specific errors
    if "exception" in event:
        exc_type = event["exception"]["values"][0]["type"]

        # Don't send 404 errors
        if exc_type == "HTTPException" and "404" in str(hint.get("exc_info")):
            return None

    return event


def capture_exception(error: Exception, context: dict[str, Any] | None = None) -> None:
    """
    Manually capture an exception with optional context.

    Args:
        error: Exception to capture
        context: Additional context data
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)

        sentry_sdk.capture_exception(error)


def capture_message(
    message: str, level: str = "info", context: dict[str, Any] | None = None
) -> None:
    """
    Manually capture a message with optional context.

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context data
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)

        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: str | None = None, phone: str | None = None) -> None:
    """
    Set user context for error tracking.

    Args:
        user_id: User identifier
        email: User email (optional)
        phone: User phone (optional)
    """
    sentry_sdk.set_user(
        {
            "id": user_id,
            "email": email,
            "phone": phone,
        }
    )


def add_breadcrumb(
    category: str, message: str, level: str = "info", data: dict[str, Any] | None = None
) -> None:
    """
    Add a breadcrumb for debugging context.

    Args:
        category: Breadcrumb category (e.g., "database", "api", "user_action")
        message: Breadcrumb message
        level: Severity level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(category=category, message=message, level=level, data=data or {})
