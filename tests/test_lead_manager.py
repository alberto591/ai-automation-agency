from unittest.mock import patch, MagicMock
import os
import sys

# Ensure we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock specific imports BEFORE running any logic that might init clients
# However, lead_manager inits clients at module level.
# We will rely on patching the INSTANCES after import, or patching the classes.

from lead_manager import (
    handle_real_estate_lead,
    handle_incoming_message,
    check_if_human_mode,
)


@patch("lead_manager.supabase")
@patch("lead_manager.mistral")
@patch("lead_manager.twilio_client")
def test_handle_real_estate_lead_happy_path(mock_twilio, mock_mistral, mock_supabase):
    """
    Test the flow: Query DB -> Build Prompt -> Call Mistral -> Send Twilio -> Save DB
    """
    # 1. Mock DB Search (get_property_details)
    # The code does: supabase.table("properties").select...
    # We need to structure the mock chain

    # Mocking get_matching_properties internal call:
    # It does: response = supabase.table("properties").select("*").ilike("title", ...).limit(3).execute()
    mock_supabase_query = (
        mock_supabase.table.return_value.select.return_value.ilike.return_value.limit.return_value.execute
    )
    mock_supabase_query.return_value.data = [
        {
            "title": "Mock Villa",
            "price": 1000000,
            "description": "A nice place",
            "location": "Mock City",
            "features": "Pool",
        }
    ]

    # 2. Mock Mistral AI
    mock_chat_complete = mock_mistral.chat.complete
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Saluti, ho trovato la Mock Villa!"
    mock_chat_complete.return_value = mock_response

    # 3. Executing function
    result = handle_real_estate_lead("+39123", "Mario", "Villa")

    # Assertions
    assert "Saluti" in result or "Messaggio inviato" in result

    # Check AI was called with correct prompt content
    args, _ = mock_chat_complete.call_args
    # args[0] is not used, kwargs is used in code: messages=[...]
    call_kwargs = mock_chat_complete.call_args[1]
    prompt_sent = call_kwargs["messages"][0]["content"]

    assert "Mock Villa" in prompt_sent
    assert "Mario" in prompt_sent
    assert "1,000,000" in prompt_sent

    # Check Twilio was sent
    mock_twilio.messages.create.assert_called_once()
    tw_kwargs = mock_twilio.messages.create.call_args[1]
    assert tw_kwargs["to"] == "whatsapp:+39123"
    assert tw_kwargs["body"] == "Saluti, ho trovato la Mock Villa!"


@patch("lead_manager.supabase")
def test_check_if_human_mode_active(mock_supabase):
    """Test that check_if_human_mode returns True when status is TAKEOVER."""
    mock_execute = mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute

    # Simulating DB return
    mock_execute.return_value.data = [{"status": "human_mode"}]

    assert check_if_human_mode("+39123") is True


@patch("lead_manager.supabase")
def test_check_if_human_mode_inactive(mock_supabase):
    """Test that check_if_human_mode returns False when status is not TAKEOVER."""
    mock_execute = mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute

    # Simulating DB return
    mock_execute.return_value.data = [{"status": "active"}]

    assert check_if_human_mode("+39123") is False


@patch("lead_manager.check_if_human_mode")
@patch("lead_manager.get_chat_history")
def test_handle_incoming_message_muted(mock_history, mock_check_mode):
    """Test that AI does NOT reply if human mode is active."""
    mock_check_mode.return_value = True

    response = handle_incoming_message("+39123", "Hello")

    assert response == "AI is muted. Human agent is in control."
    # Ensure get_chat_history was NOT called (optimization check)
    # The code calls check_if_human_mode first.
    mock_history.assert_not_called()

@patch('lead_manager.notify_owner_urgent')
@patch('lead_manager.toggle_human_mode')
@patch('lead_manager.check_if_human_mode')
def test_handle_incoming_message_keyword_trigger(mock_check_mode, mock_toggle, mock_notify):
    """Test that TIER1 keywords trigger the takeover protocol."""
    mock_check_mode.return_value = False
    
    # User asks for human (TIER1 keyword)
    msg = "Voglio parlare con un umano subito"
    
    response = handle_incoming_message("+39123", msg)
    
    # Check that AI response is the standard 'Wait for boss' message
    assert "responsabile" in response
    
    # Check side effects
    mock_toggle.assert_called_once_with("+39123")
    mock_notify.assert_called_once()
