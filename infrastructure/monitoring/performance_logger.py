"""
Performance Metric Logger
Logs appraisal performance metrics to Supabase for monitoring and analysis
"""

import time
from functools import wraps
from typing import Any, cast

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PerformanceMetricLogger:
    """Logs appraisal performance metrics to database."""

    def __init__(self, db_client: Any):
        """
        Initialize logger with database client.

        Args:
            db_client: Supabase client for logging metrics
        """
        self.db = db_client

    def log_appraisal_performance(
        self,
        city: str,
        zone: str,
        response_time_ms: int,
        used_local_search: bool,
        used_perplexity: bool,
        comparables_found: int,
        confidence_level: int,
        reliability_stars: int,
        estimated_value: float,
        property_type: str | None = None,
        surface_sqm: int | None = None,
        user_phone: str | None = None,
        user_email: str | None = None,
    ) -> str | None:
        """
        Log appraisal performance metrics to the database.

        Returns:
            The ID of the logged metric if successful, else None.
        """
        try:
            # Use RPC function for secure insert
            result = self.db.rpc(
                "log_appraisal_performance",
                {
                    "p_city": city,
                    "p_zone": zone,
                    "p_property_type": property_type,
                    "p_surface_sqm": surface_sqm,
                    "p_response_time_ms": response_time_ms,
                    "p_used_local_search": used_local_search,
                    "p_used_perplexity": used_perplexity,
                    "p_comparables_found": comparables_found,
                    "p_confidence_level": confidence_level,
                    "p_reliability_stars": reliability_stars,
                    "p_estimated_value": estimated_value,
                    "p_user_phone": user_phone,
                    "p_user_email": user_email,
                },
            ).execute()

            logger.info(
                "PERFORMANCE_METRIC_LOGGED",
                context={
                    "city": city,
                    "zone": zone,
                    "response_ms": response_time_ms,
                    "local_search": used_local_search,
                    "confidence": confidence_level,
                },
            )

            # Return the ID if possible
            if result.data and isinstance(result.data, list) and len(result.data) > 0:
                return cast(str, result.data[0].get("id"))
            if isinstance(result.data, str):
                return result.data

            return None

        except Exception as e:
            # Don't fail the request if logging fails
            logger.warning(
                "PERFORMANCE_METRIC_LOG_FAILED",
                context={"error": str(e)},
            )
            return None


def track_performance(db_client: Any) -> Any:
    """
    Decorator to track appraisal performance metrics.

    Usage:
        @track_performance(db_client)
        def estimate_property(self, request):
            # ... appraisal logic ...
            return result
    """

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()

            # Execute function
            result = func(*args, **kwargs)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Extract request data (assumes first or second arg is AppraisalRequest)
            # In a class method, args[0] is self, args[1] is the request
            request = args[1] if len(args) > 1 else kwargs.get("request")

            if request and hasattr(result, "confidence_level"):
                try:
                    metric_logger = PerformanceMetricLogger(db_client)
                    metric_logger.log_appraisal_performance(
                        city=getattr(request, "city", "Unknown"),
                        zone=getattr(request, "zone", "Unknown"),
                        property_type=getattr(request, "property_type", None),
                        surface_sqm=getattr(request, "surface_sqm", None),
                        response_time_ms=response_time_ms,
                        used_local_search=getattr(result, "_used_local_search", False),
                        used_perplexity=getattr(result, "_used_perplexity", False),
                        comparables_found=len(getattr(result, "comparables", [])),
                        confidence_level=getattr(result, "confidence_level", 0),
                        reliability_stars=getattr(result, "reliability_stars", 1),
                        estimated_value=float(getattr(result, "estimated_value", 0)),
                        user_phone=getattr(request, "phone", None),
                        user_email=getattr(request, "email", None),
                    )
                except Exception as e:
                    logger.warning("DECORATOR_LOGGING_FAILED", context={"error": str(e)})

            return result

        return wrapper

    return decorator
