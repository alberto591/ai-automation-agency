import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure we can import the module from parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from config import config

client = TestClient(app)
HEADERS = {"X-Webhook-Key": config.WEBHOOK_API_KEY}

def test_lead_full_journey():
    """
    E2E Journey:
    1. Portal Webhook (Inbound Lead)
    2. WhatsApp Webhook (Conversation)
    3. Takeover (Pause AI)
    4. Manual Message (Dashboard)
    """
    
    # --- 1. MOCK Setup ---
    with patch("api.handle_real_estate_lead") as mock_handle_lead, \
         patch("lead_manager.handle_incoming_message") as mock_handle_msg, \
         patch("lead_manager.send_whatsapp_safe") as mock_send_ws, \
         patch("lead_manager.supabase") as mock_supabase:
        
        # Mocking Supabase responses
        mock_handle_lead.return_value = "AI Response"
        mock_handle_msg.return_value = "AI Chat Reply"
        mock_send_ws.return_value = "msg_sid_123"
        
        # Mock Single row return for takeover/message logging
        mock_row = MagicMock()
        mock_row.data = {"messages": [], "status": "active"}
        mock_supabase.table().select().eq().single().execute.return_value = mock_row
        
        # --- 2. Step 1: Portal Lead Ingestion ---
        portal_payload = {
            "name": "E2E Lead",
            "phone": "+393339998888",
            "source": "immobiliare"
        }
        res_portal = client.post("/webhooks/portal", json=portal_payload, headers=HEADERS)
        assert res_portal.status_code == 200
        assert mock_handle_lead.called

        # --- 3. Step 2: WhatsApp Conversation ---
        twilio_payload = {
            "Body": "Vorrei informazioni sulla casa",
            "From": "whatsapp:+393339998888"
        }
        res_twilio = client.post("/webhooks/twilio", data=twilio_payload, headers=HEADERS)
        assert res_twilio.status_code == 200
        assert "AI Chat Reply" in res_twilio.json()["message"]

        # --- 4. Step 3: Human Takeover ---
        takeover_payload = {"phone": "+393339998888"}
        res_takeover = client.post("/api/leads/takeover", json=takeover_payload)
        assert res_takeover.status_code == 200
        assert "Human Control Active" in res_takeover.json()["message"]

        # --- 5. Step 4: Manual Outbound Message ---
        manual_payload = {
            "phone": "+393339998888",
            "message": "Ciao, sono l'agente umano. Come posso aiutarti?"
        }
        res_manual = client.post("/api/leads/message", json=manual_payload)
        assert res_manual.status_code == 200
        assert res_manual.json()["status"] == "sent"
        assert mock_send_ws.called

    print("\n✅ E2E Full Journey Test Passed!")
