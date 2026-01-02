from unittest.mock import patch

import pytest

from infrastructure.adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter


@pytest.fixture
def adapter():
    with patch("config.settings.settings") as mock_set:
        mock_set.META_ACCESS_TOKEN = "test_token"
        mock_set.META_PHONE_ID = "test_id"
        mock_set.WHATSAPP_PROVIDER = "meta"

        # Patch the Container to avoid real instantiation of other adapters
        with patch("config.container.Container"):
            yield MetaWhatsAppAdapter()


def test_send_message_success(adapter):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messaging_product": "whatsapp",
            "messages": [{"id": "mid.123"}],
        }

        adapter.send_message("+393331234567", "Hello Meta")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["to"] == "393331234567"
        assert kwargs["json"]["text"]["body"] == "Hello Meta"


def test_send_message_failure(adapter):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Error detail"

        with pytest.raises(Exception) as excinfo:
            adapter.send_message("+393331234567", "Fail")

        assert "Failed to connect to Meta WhatsApp API" in str(excinfo.value)
