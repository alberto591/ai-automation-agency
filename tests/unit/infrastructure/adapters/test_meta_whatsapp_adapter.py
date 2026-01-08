from unittest.mock import MagicMock, patch

import pytest

from domain.errors import ExternalServiceError
from domain.messages import Button, InteractiveMessage, Row, Section
from infrastructure.adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter


class TestMetaWhatsAppAdapter:
    @pytest.fixture
    def adapter(self, mock_settings):
        return MetaWhatsAppAdapter()

    @patch("requests.post")
    def test_send_interactive_message_button(self, mock_post, adapter):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "msg_123"}]}
        mock_post.return_value = mock_response

        message = InteractiveMessage(
            type="button",
            body_text="Choose an option",
            buttons=[
                Button(id="btn1", title="Option 1"),
                Button(id="btn2", title="Option 2"),
            ],
            header_text="Header",
            footer_text="Footer",
        )

        # Act
        msg_id = adapter.send_interactive_message("1234567890", message)

        # Assert
        assert msg_id == "msg_123"
        mock_post.assert_called_once()

        # Verify Payload
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]

        assert payload["messaging_product"] == "whatsapp"
        assert payload["to"] == "1234567890"
        assert payload["type"] == "interactive"
        assert payload["interactive"]["type"] == "button"
        assert payload["interactive"]["body"]["text"] == "Choose an option"
        assert payload["interactive"]["header"]["text"] == "Header"
        assert payload["interactive"]["footer"]["text"] == "Footer"
        assert len(payload["interactive"]["action"]["buttons"]) == 2
        assert payload["interactive"]["action"]["buttons"][0]["reply"]["id"] == "btn1"
        assert payload["interactive"]["action"]["buttons"][0]["reply"]["title"] == "Option 1"

    @patch("requests.post")
    def test_send_interactive_message_list(self, mock_post, adapter):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "msg_456"}]}
        mock_post.return_value = mock_response

        message = InteractiveMessage(
            type="list",
            body_text="Select a property",
            button_text="View List",
            sections=[
                Section(
                    title="Apartments",
                    rows=[
                        Row(id="prop1", title="Appt 1", description="Nice view"),
                        Row(id="prop2", title="Appt 2"),
                    ],
                )
            ],
        )

        # Act
        msg_id = adapter.send_interactive_message("1234567890", message)

        # Assert
        assert msg_id == "msg_456"

        # Verify Payload
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]

        assert payload["interactive"]["type"] == "list"
        assert payload["interactive"]["action"]["button"] == "View List"
        assert len(payload["interactive"]["action"]["sections"]) == 1
        assert payload["interactive"]["action"]["sections"][0]["title"] == "Apartments"
        assert len(payload["interactive"]["action"]["sections"][0]["rows"]) == 2
        assert payload["interactive"]["action"]["sections"][0]["rows"][0]["id"] == "prop1"
        assert (
            payload["interactive"]["action"]["sections"][0]["rows"][0]["description"] == "Nice view"
        )

    @patch("requests.post")
    def test_send_interactive_message_error(self, mock_post, adapter):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad Request"}}
        mock_post.return_value = mock_response

        message = InteractiveMessage(type="button", body_text="Error test")

        # Act & Assert
        with pytest.raises(ExternalServiceError):
            adapter.send_interactive_message("1234567890", message)
