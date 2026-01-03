"""
Performance Metric Logger
Logs appraisal performance metrics to Supabase for monitoring and analysis
"""

import time
from functools import wraps

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PerformanceMetricLogger:
    """Logs appraisal performance metrics to database."""

    def __init__(self, db_client):
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
    ) -> None:
        """
        Log appraisal performance metrics.

        Args:
            city: City name
            zone: Zone/neighborhood
            response_time_ms: Total response time in milliseconds
            used_local_search: Whether local database search was used
            used_perplexity: Whether Perplexity API fallback was used
            comparables_found: Number of comparables found
            confidence_level: Confidence percentage (0-100)
            reliability_stars: Star rating (1-5)
            estimated_value: Estimated property value
            property_type: Type of property (optional)
            surface_sqm: Property size in square meters (optional)
            user_phone: User phone for correlation (optional)
            user_email: User email for correlation (optional)
        """
        try:
            # Use RPC function for secure insert
            self.db.rpc(
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

        except Exception as e:
            # Don't fail the request if logging fails
            logger.warning(
                "PERFORMANCE_METRIC_LOG_FAILED",
                context={"error": str(e)},
            )


def track_performance(db_client):
    """
    Decorator to track appraisal performance metrics.

    Usage:
        @track_performance(db_client)
        def estimate_property(request):
            # ... appraisal logic ...
            return result
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Execute function
            result = func(*args, **kwargs)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Extract request data (assumes first arg is AppraisalRequest)
            request = args[1] if len(args) > 1 else kwargs.get("request")

            if request and hasattr(result, "confidence_level"):
                try:
                    metric_logger = PerformanceMetricLogger(db_client)
                    metric_logger.log_appraisal_performance(
                        city=request.city,
                        zone=request.zone,
                        property_type=request.property_type,
                        surface_sqm=request.surface_sqm,
                        response_time_ms=response_time_ms,
                        used_local_search=hasattr(result, "_used_local_search")
                        and result._used_local_search,
                        used_perplexity=hasattr(result, "_used_perplexity")
                        and result._used_perplexity,
                        comparables_found=len(result.comparables),
                        confidence_level=result.confidence_level,
                        reliability_stars=result.reliability_stars,
                        estimated_value=result.estimated_value,
                        user_phone=getattr(request, "phone", None),
                        user_email=getattr(request, "email", None),
                    )
                except Exception as e:
                    logger.warning("Performance tracking failed", context={"error": str(e)})

            return result

        return wrapper

    return decorator
