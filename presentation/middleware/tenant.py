"""
Tenant Middleware for Multi-Tenancy Support.

Injects tenant_id into request state for downstream use.
Defense-in-depth layer alongside RLS.
"""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config.settings import settings
from domain.services.logging import get_logger

logger = get_logger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts tenant_id from authenticated user's JWT
    and injects it into request.state for downstream use.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Default to service-level tenant for webhooks/unauthenticated requests
        tenant_id: str | None = settings.DEFAULT_TENANT_ID

        # Check if user is authenticated (set by auth middleware)
        user = getattr(request.state, "user", None)

        if user and isinstance(user, dict):
            # Extract tenant from JWT app_metadata
            app_metadata = user.get("app_metadata", {})
            jwt_tenant_id = app_metadata.get("active_org_id")

            if jwt_tenant_id:
                tenant_id = jwt_tenant_id
                logger.debug(
                    "TENANT_RESOLVED",
                    context={"tenant_id": tenant_id, "source": "jwt"},
                )
            else:
                logger.warning(
                    "NO_TENANT_IN_JWT",
                    context={"user_id": user.get("sub")},
                )

        # Inject into request state
        request.state.tenant_id = tenant_id

        return await call_next(request)


def get_tenant_id(request: Request) -> str | None:
    """
    Helper function to retrieve tenant_id from request.
    Use this in route handlers for explicit tenant filtering.
    """
    return getattr(request.state, "tenant_id", None)
