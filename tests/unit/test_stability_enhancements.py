import asyncio
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.adapters.twilio_adapter import TwilioAdapter


@pytest.fixture
def mock_container_stability():
    with patch("presentation.api.api.container") as mock_cnt:
        mock_cnt.db.client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": "lead_123",
            "customer_name": "Test User",
        }
        mock_cnt.main_loop = None
        yield mock_cnt


def test_webhook_phone_prefix_cleaning(client, mock_container_stability):
    """Verify that 'whatsapp:' prefix is stripped from incoming phone number."""
    payload = {
        "From": "whatsapp:+393331234567",
        "Body": "Hello Bot",
        "NumMedia": "0",
    }
    response = client.post("/api/webhooks/twilio", data=payload)

    assert response.status_code == 200
    assert response.json() == "OK"

    # Verify DB lookup used the cleaned number
    mock_container_stability.db.client.table.assert_called_with("leads")
    mock_container_stability.db.client.table().select().eq.assert_called_with(
        "customer_phone", "+393331234567"
    )


def test_webhook_self_loop_prevention(client, mock_container_stability):
    """Verify that messages from the bot's own number are ignored."""
    with patch("config.settings.settings") as mock_set:
        mock_set.TWILIO_PHONE_NUMBER = "+1234567890"

        payload = {
            "From": "whatsapp:+1234567890",
            "Body": "I am the bot responding to myself",
            "NumMedia": "0",
        }
        response = client.post("/api/webhooks/twilio", data=payload)

        assert response.status_code == 200
        assert response.json() == "OK"
        # DB lookup should NOT be called for self-messages
        mock_container_stability.db.client.table.assert_not_called()


def test_webhook_empty_message_blocking(client, mock_container_stability):
    """Verify that empty messages without media are ignored."""
    payload = {
        "From": "whatsapp:+393331234567",
        "Body": "  ",
        "NumMedia": "0",
    }
    response = client.post("/api/webhooks/twilio", data=payload)

    assert response.status_code == 200
    assert response.json() == "OK"
    # DB lookup should NOT be called for empty messages
    mock_container_stability.db.client.table.assert_not_called()


def test_twilio_adapter_rate_limiting():
    """Verify that TwilioAdapter blocks messages exceeding the rate limit."""
    import tenacity

    with patch("infrastructure.adapters.twilio_adapter.RateLimiter") as mock_limiter_class:
        mock_limiter = mock_limiter_class.return_value
        mock_limiter.check_rate_limit.return_value = False

        adapter = TwilioAdapter()
        # Mock Twilio client to avoid actual API calls
        adapter.client = MagicMock()

        # Due to @retry, it will raise RetryError wrapping the ExternalServiceError
        with pytest.raises(tenacity.RetryError):
            adapter.send_message("+393331234567", "Hello")

        adapter.client.messages.create.assert_not_called()


def test_add_message_history_thread_safe_broadcast():
    """Verify that add_message_history uses run_coroutine_threadsafe when main_loop is set."""
    from application.services.lead_processor import LeadProcessor

    mock_db = MagicMock()
    mock_ai = MagicMock()
    mock_msg = MagicMock()
    mock_scorer = MagicMock()

    processor = LeadProcessor(mock_db, mock_ai, mock_msg, mock_scorer, None, None, None, None)

    # Mock lead lookup
    mock_db.get_lead.return_value = {"id": "lead_123", "name": "Test"}

    mock_loop = MagicMock(spec=asyncio.AbstractEventLoop)
    mock_loop.is_running.return_value = True

    from config.container import container

    with patch.object(container, "main_loop", mock_loop):
        with patch("asyncio.run_coroutine_threadsafe") as mock_run_safe:
            processor.add_message_history("+393331234567", "user", "Hello")

            assert mock_run_safe.called
            # The first argument to run_coroutine_threadsafe is a coroutine
            args, _ = mock_run_safe.call_args
            # Cleanup the coroutine to avoid warning
            coro = args[0]
            assert asyncio.iscoroutine(coro)
            assert args[1] == mock_loop
            coro.close()
