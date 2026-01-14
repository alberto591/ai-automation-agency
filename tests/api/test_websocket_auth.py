from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from presentation.api.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_websocket_missing_token(client):
    """
    Scenario: Client connects without a token.
    Expected: Connection accepted but tenant_id is None, returning empty data.
    """
    # Patch targets must be local to where they are imported
    with (
        patch("presentation.api.api.ws_manager") as mock_ws_manager,
        patch("presentation.api.api.settings") as mock_settings,
        patch("presentation.api.api.container"),
    ):
        # Explicitly set defaults so they aren't Truthy Mocks
        mock_settings.SUPABASE_JWT_SECRET = "mock_secret"
        mock_settings.DEFAULT_TENANT_ID = None

        mock_ws_manager.connect = AsyncMock()
        mock_ws_manager.subscribe_to_room = Mock()

        # TestClient.websocket_connect
        try:
            with client.websocket_connect("/ws/conversations") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "connected"

                data_leads = websocket.receive_json()
                assert data_leads["type"] == "conversations"
                assert data_leads["data"] == []  # Expect empty list when no tenant context
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")


def test_websocket_valid_token(client):
    """
    Scenario: Client connects with valid tenant token.
    Expected: Tenant ID extracted, DB queried with tenant filter.
    """
    # A valid-looking JWT token (even if fake, jose will try to parse it if not mocked)
    token = "header.payload.signature"
    mock_payload = {"sub": "user_123", "app_metadata": {"active_org_id": "tenant-xyz"}}

    with (
        patch("presentation.api.api.ws_manager") as mock_ws_manager,
        patch("jose.jwt.decode") as mock_decode,
        patch("presentation.api.api.container") as mock_container,
        patch("presentation.api.api.settings") as mock_settings,
    ):
        mock_settings.SUPABASE_JWT_SECRET = "secret"
        mock_settings.DEFAULT_TENANT_ID = "default"

        mock_decode.return_value = mock_payload
        mock_ws_manager.connect = AsyncMock()

        # Mock DB Chain: container.db.client.table().select().eq().in_().order().limit().execute()
        mock_execute = Mock()
        mock_execute.data = [{"id": "lead-1", "tenant_id": "tenant-xyz"}]

        # Build the chain mock
        mock_chain = mock_container.db.client.table.return_value.select.return_value.eq.return_value.in_.return_value.order.return_value.limit.return_value.execute
        mock_chain.return_value = mock_execute

        try:
            with client.websocket_connect(f"/ws/conversations?token={token}") as websocket:
                websocket.receive_json()  # connected
                data = websocket.receive_json()
                assert data["type"] == "conversations"
                assert len(data["data"]) > 0
                assert data["data"][0]["id"] == "lead-1"

                # VERIFY TENANT ISOLATION
                mock_container.db.client.table.return_value.select.return_value.eq.assert_called_with(
                    "tenant_id", "tenant-xyz"
                )
        except Exception as e:
            pytest.fail(f"WebSocket valid token test failed: {e}")


def test_websocket_invalid_token(client):
    """
    Scenario: Token is invalid (JWTError).
    Expected: Fallback to None tenant -> Empty Data.
    """
    from jose import JWTError

    token = "invalid-token"

    with (
        patch("presentation.api.api.ws_manager") as mock_ws_manager,
        patch("jose.jwt.decode") as mock_decode,
        patch("presentation.api.api.settings") as mock_settings,
    ):
        mock_settings.SUPABASE_JWT_SECRET = "secret"
        mock_settings.DEFAULT_TENANT_ID = None

        mock_decode.side_effect = JWTError("Invalid signature")
        mock_ws_manager.connect = AsyncMock()

        try:
            with client.websocket_connect(f"/ws/conversations?token={token}") as websocket:
                websocket.receive_json()  # connected
                data = websocket.receive_json()
                assert data["type"] == "conversations"
                assert data["data"] == []
        except Exception as e:
            pytest.fail(f"WebSocket invalid token test failed: {e}")
