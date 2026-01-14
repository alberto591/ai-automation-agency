from unittest.mock import Mock, patch

import pytest
from starlette.datastructures import State

from presentation.middleware.tenant import TenantMiddleware


@pytest.fixture
def middleware():
    return TenantMiddleware(app=Mock())


@pytest.mark.asyncio
async def test_tenant_middleware_with_jwt_tenant(middleware):
    """
    Scenario: User has a valid JWT with `active_org_id`.
    Expected: request.state.tenant_id matches the JWT org id.
    """
    # Mock Request
    request = Mock()
    request.state = State()

    # Mock Auth User injection (usually done by AuthMiddleware)
    request.state.user = {"sub": "user_123", "app_metadata": {"active_org_id": "test-org-uuid"}}

    # Mock Next Call
    async def call_next(req):
        return "OK"

    # Execute
    await middleware.dispatch(request, call_next)

    # Assert
    assert request.state.tenant_id == "test-org-uuid"


@pytest.mark.asyncio
async def test_tenant_middleware_no_jwt(middleware):
    """
    Scenario: Anonymous request (no user in state).
    Expected: request.state.tenant_id falls back to DEFAULT_TENANT_ID.
    """
    request = Mock()
    request.state = State()
    # No user attribute

    async def call_next(req):
        return "OK"

    # Patch the settings object IMPORTED in the middleware module,
    # not the original source, because it was already imported.
    with patch("presentation.middleware.tenant.settings") as mock_settings:
        mock_settings.DEFAULT_TENANT_ID = "default-uuid"
        await middleware.dispatch(request, call_next)

    assert request.state.tenant_id == "default-uuid"


@pytest.mark.asyncio
async def test_tenant_middleware_jwt_missing_org(middleware):
    """
    Scenario: User logged in but has no active_org_id (e.g. old user, onboarding failed).
    Expected: fallback to DEFAULT_TENANT_ID.
    """
    request = Mock()
    request.state = State()
    request.state.user = {
        "sub": "user_old",
        "app_metadata": {},  # Empty metadata
    }

    async def call_next(req):
        return "OK"

    with patch("presentation.middleware.tenant.settings") as mock_settings:
        mock_settings.DEFAULT_TENANT_ID = "default-uuid"
        await middleware.dispatch(request, call_next)

    assert request.state.tenant_id == "default-uuid"
