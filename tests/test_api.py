from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

# Create a dummy .env file if it doesn't exist
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("SUPABASE_URL=http://mock\nSUPABASE_KEY=mock\n")

# Ensure we can import the module from parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, validate_phone

client = TestClient(app)


def test_health_check():
    """Test the /health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "service": "Agenzia AI Backend"}


@patch("api.handle_real_estate_lead")
def test_create_lead_success(mock_handle_lead):
    """Test POST /api/leads with valid data."""
    # Setup mock return
    mock_handle_lead.return_value = "Mock AI Response"

    payload = {
        "name": "Mario Rossi",
        "agency": "Immobiliare.it",
        "phone": "+393331234567",
        "properties": "Attico Centro",
    }

    response = client.post("/api/leads", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["ai_response"] == "Mock AI Response"

    # Verify the logic function was called with correct args
    mock_handle_lead.assert_called_once_with(
        "+393331234567",
        "Mario Rossi",
        "Agenzia: Immobiliare.it. Gestione: Attico Centro",
    )


@patch("lead_manager.handle_incoming_message")
def test_twilio_webhook(mock_handle_msg):
    """Test POST /webhooks/twilio receives form data and calls logic."""
    # Note: We patch lead_manager.handle_incoming_message because api.py imports it inside the function
    # OR we need to see how api.py imports it.
    # checking api.py: 'from lead_manager import handle_incoming_message' inside the route.
    # So we must patch 'lead_manager.handle_incoming_message'

    mock_handle_msg.return_value = "Mock Reply"

    # Twilio sends form data
    form_data = {"Body": "Ciao, info?", "From": "whatsapp:+393331234567"}

    response = client.post("/webhooks/twilio", data=form_data)

    assert response.status_code == 200
    assert response.json() == {"status": "replied", "message": "Mock Reply"}

    msg_arg = mock_handle_msg.call_args[0][1]
    phone_arg = mock_handle_msg.call_args[0][0]

    assert msg_arg == "Ciao, info?"
    assert phone_arg == "+393331234567"


@patch("lead_manager.toggle_human_mode")
def test_takeover_success(mock_toggle):
    """Test POST /api/leads/takeover calls the toggle function."""
    mock_toggle.return_value = True

    payload = {"phone": "+393331234567"}
    response = client.post("/api/leads/takeover", json=payload)

    assert response.status_code == 200
    assert "AI Muted" in response.json()["message"]
    mock_toggle.assert_called_once_with("+393331234567")


@patch("lead_manager.toggle_human_mode")
def test_takeover_failure(mock_toggle):
    """Test takeover endpoint handles failure gracefully."""
    mock_toggle.return_value = False

    payload = {"phone": "+393331234567"}
    response = client.post("/api/leads/takeover", json=payload)

    assert response.status_code == 500


@patch("api.handle_real_estate_lead")
def test_portal_webhook_success(mock_handle_lead):
    """Test the universal /webhooks/portal endpoint."""
    mock_handle_lead.return_value = "AI Response"
    payload = {
        "name": "Portal Lead",
        "phone": "+393330001111",
        "source": "idealista"
    }
    response = client.post("/webhooks/portal", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "idealista" in response.json()["source"]


@patch("api.handle_real_estate_lead")
def test_immobiliare_webhook_success(mock_handle_lead):
    """Test the specific /webhooks/immobiliare endpoint."""
    mock_handle_lead.return_value = "AI Response"
    payload = {
        "contact_name": "Immo Client",
        "contact_phone": "3331234567",  # Testing auto-fix +39
        "listing_title": "Modern Loft"
    }
    response = client.post("/webhooks/immobiliare", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    # Verify auto-fix worked
    mock_handle_lead.assert_called_once_with("+393331234567", "Immo Client", "Modern Loft")


@patch("api.handle_real_estate_lead")
def test_email_parser_webhook_success(mock_handle_lead):
    """Test the /webhooks/email-parser endpoint from Make.com."""
    mock_handle_lead.return_value = "AI Response"
    payload = {
        "parsed_name": "Email Client",
        "parsed_phone": "+393339998888",
        "property": "Villa"
    }
    response = client.post("/webhooks/email-parser", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@patch("lead_manager.resume_ai_mode")
def test_resume_ai_success(mock_resume):
    """Test the /api/leads/resume endpoint."""
    mock_resume.return_value = True
    payload = {"phone": "+393331112222"}
    response = client.post("/api/leads/resume", json=payload)
    assert response.status_code == 200
    assert "AI Resumed" in response.json()["message"]


def test_validate_phone_formats():
    """Test the validate_phone utility directly."""
    assert validate_phone("+393331234567") is True
    assert validate_phone("+14155552671") is True
    assert validate_phone("021234567") is False
    assert validate_phone("invalid") is False
