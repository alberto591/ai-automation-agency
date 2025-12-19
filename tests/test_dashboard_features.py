from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure we can import the module from parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from lead_manager import save_lead_to_dashboard

client = TestClient(app)

# 1. Test Lead Profiling (Budget & Zone Extraction)
@patch("lead_manager.supabase")
def test_save_lead_to_dashboard_profiling(mock_supabase):
    """
    Verify that budget and zones are extracted correctly from last_msg.
    """
    # Setup mock chain
    mock_execute = (
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute
    )
    mock_execute.return_value.data = [] # No existing history

    # Case A: Budget + Zone in message
    save_lead_to_dashboard(
        customer_name="Mario Rossi",
        customer_phone="+393331112222",
        last_msg="Cerco casa a Brera con budget 500k",
        ai_notes="Interessato",
        lead_score=60
    )

    # Verify the data passed to upsert
    upsert_args = mock_supabase.table.return_value.upsert.call_args[0][0]
    
    assert upsert_args["budget_max"] == 500000
    assert "Brera" in upsert_args["preferred_zones"]
    assert upsert_args["customer_name"] == "Mario Rossi"
    assert upsert_args["status"] == "HOT" # score 60 >= 50

    # Case B: Just large number as budget
    save_lead_to_dashboard(
        customer_name="Marta",
        customer_phone="+393334445555",
        last_msg="Mio budget 1200000",
        ai_notes="High budget",
        lead_score=30
    )
    
    upsert_args_2 = mock_supabase.table.return_value.upsert.call_args_list[1][0][0]
    assert upsert_args_2["budget_max"] == 1200000
    assert upsert_args_2["status"] == "Warm" # score 30

# 2. Test Manual Message Endpoint
@patch("lead_manager.send_whatsapp_safe")
def test_manual_message_endpoint(mock_send_safe):
    """
    Verify that POST /api/leads/message sends WhatsApp and logs to DB.
    """
    from datetime import datetime
    import lead_manager
    mock_supabase = lead_manager.supabase
    mock_send_safe.return_value = "SM123"

    # 2. Setup mock supabase for history fetch
    mock_fetch = mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute
    mock_fetch.return_value.data = {"messages": []} # single() returns a dict, not a list of 1 dict

    payload = {
        "phone": "+393331112222",
        "message": "Ciao, sono l'agente umano!"
    }

    response = client.post("/api/leads/message", json=payload)

    # Assertions
    assert response.status_code == 200
    assert response.json()["status"] == "sent"

    # Verify Sender was called
    mock_send_safe.assert_called_once_with("+393331112222", "Ciao, sono l'agente umano!")

    # Verify Logging was called (update)
    mock_supabase.table.assert_any_call("lead_conversations")
    
    # Filter calls to find the one where 'messages' is updated
    update_calls = [c for c in mock_supabase.table.return_value.update.call_args_list if "messages" in c[0][0]]
    assert len(update_calls) > 0, "Update was not called with messages"
    
    logged_data = update_calls[0][0][0]

    assert logged_data["status"] == "human_mode"
    
    # Check that the history contains the human message
    last_hist_entry = logged_data["messages"][-1]
    assert last_hist_entry["content"] == "Ciao, sono l'agente umano!"
    assert last_hist_entry["metadata"]["by"] == "human_agent"
