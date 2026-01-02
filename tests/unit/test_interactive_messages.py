from domain.messages import Button, InteractiveMessage, Row, Section


def test_interactive_message_button_serialization():
    buttons = [Button(id="btn1", title="Option 1"), Button(id="btn2", title="Option 2")]
    msg = InteractiveMessage(type="button", body_text="Choose an option", buttons=buttons)

    serialized = msg.model_dump()
    assert serialized["type"] == "button"
    assert serialized["body_text"] == "Choose an option"
    assert len(serialized["buttons"]) == 2
    assert serialized["buttons"][0]["id"] == "btn1"
    assert serialized["buttons"][0]["title"] == "Option 1"


def test_interactive_message_list_serialization():
    rows = [
        Row(id="row1", title="Item 1", description="Description 1"),
        Row(id="row2", title="Item 2"),
    ]
    sections = [Section(title="Section 1", rows=rows)]

    msg = InteractiveMessage(
        type="list", body_text="Select an item", button_text="View List", sections=sections
    )

    serialized = msg.model_dump()
    assert serialized["type"] == "list"
    assert serialized["body_text"] == "Select an item"
    assert serialized["button_text"] == "View List"
    assert len(serialized["sections"]) == 1
    assert len(serialized["sections"][0]["rows"]) == 2
    assert serialized["sections"][0]["rows"][0]["id"] == "row1"


def test_interactive_message_cta_url_serialization():
    msg = InteractiveMessage(type="cta_url", body_text="Click the link", url="https://example.com")

    serialized = msg.model_dump()
    assert serialized["type"] == "cta_url"
    assert serialized["body_text"] == "Click the link"
    assert serialized["url"] == "https://example.com"


def test_interactive_message_missing_fields_validation():
    # Example validation: if type is 'button', buttons should be present
    # Note: Pydantic validation checks might need custom validators in the model
    # For now, we just check that we can create the object if we provide minimal valid fields
    # based on the current definitions which seem optional.
    # If business logic requires 'buttons' when type='button', that should be tested if validation exists.

    msg = InteractiveMessage(type="button", body_text="Test")
    assert msg.type == "button"
    # Even if buttons is None, it should instantiate without extra validators
    assert msg.buttons is None
