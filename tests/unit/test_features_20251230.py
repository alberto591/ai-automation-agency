from unittest.mock import MagicMock, patch

from domain.messages import Button, InteractiveMessage, Row, Section
from domain.ports import DatabasePort
from infrastructure.adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from infrastructure.tools.property_search import PropertySearchTool


# 1. Test Domain Models (InteractiveMessage)
def test_interactive_message_list_serialization():
    rows = [Row(id="1", title="Row 1", description="Desc 1")]
    section = Section(title="Section 1", rows=rows)
    msg = InteractiveMessage(type="list", body_text="Body", button_text="Menu", sections=[section])

    assert msg.type == "list"
    assert msg.sections[0].rows[0].id == "1"


def test_interactive_message_button_serialization():
    buttons = [Button(id="btn1", title="Yes")]
    msg = InteractiveMessage(type="button", body_text="Click me", buttons=buttons)
    assert msg.type == "button"
    assert msg.buttons[0].title == "Yes"


# 2. Test Meta WhatsApp Adapter (Mocked)
@patch("infrastructure.adapters.meta_whatsapp_adapter.requests.post")
def test_meta_adapter_send_interactive_list(mock_post):
    # Setup
    adapter = MetaWhatsAppAdapter()
    adapter.rate_limiter = MagicMock()
    adapter.rate_limiter.check_rate_limit.return_value = True

    # Mock Response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": "wamid.123"}]}
    mock_post.return_value = mock_response

    # Payload
    rows = [Row(id="1", title="House")]
    msg = InteractiveMessage(
        type="list",
        body_text="Choose",
        button_text="View",
        sections=[Section(title="A", rows=rows)],
    )

    # Execute
    res = adapter.send_interactive_message("+393330000000", msg)

    # Verify
    assert res == "wamid.123"
    assert mock_post.called
    args, kwargs = mock_post.call_args
    json_body = kwargs["json"]

    assert json_body["type"] == "interactive"
    assert json_body["interactive"]["type"] == "list"
    assert json_body["interactive"]["action"]["button"] == "View"


# 3. Test Property Search Tool
def test_property_search_tool():
    # Mock DB
    mock_db = MagicMock(spec=DatabasePort)
    mock_db.get_properties.return_value = [
        {"title": "Villa Rosa", "price": 500000},
        {"title": "Cheap Flat", "price": 100000},
    ]

    tool = PropertySearchTool(db=mock_db)

    # Test valid search
    result = tool._run(query="villa")

    assert "Villa Rosa" in result
    assert "€500,000" in result
    assert "Cheap Flat" in result

    # Verify DB call
    mock_db.get_properties.assert_called_with(query="villa", limit=3)


def test_property_search_empty():
    mock_db = MagicMock(spec=DatabasePort)
    mock_db.get_properties.return_value = []

    tool = PropertySearchTool(db=mock_db)
    result = tool._run(query="castle")

    assert "No specific properties found" in result
