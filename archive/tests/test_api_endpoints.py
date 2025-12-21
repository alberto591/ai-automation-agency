import pytest
import time

def test_api_health(client):
    """Verify health check endpoint returns online status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "service": "Agenzia AI Backend"}

def test_post_leads_minimal(client, mock_external_services):
    """Verify basic lead capture from the landing page form."""
    payload = {
        "name": "Mario Rossi",
        "phone": "+39123456789",
        "agency": "Test Agency",
        "properties": "Trilocale Milano"
    }
    # No API Key required for the public /api/leads endpoint
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_post_leads_valuation_trigger(client, mock_external_services):
    """Verify that the 'RICHIESTA VALUTAZIONE' trigger works through the API."""
    # We need to mock market context in lead_manager because handle_real_estate_lead calls it
    supabase = mock_external_services["supabase"]
    supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=[{"price_per_mq": 4000}])
    
    payload = {
        "name": "Valuation Lead",
        "phone": "+39111222333",
        "agency": "Appraisal",
        "properties": "RICHIESTA VALUTAZIONE: Isola, Milano"
    }
    
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 200
    assert "VALUTAZIONE AI COMPLETATA" in response.json()["ai_response"]
    assert "€3720/mq" in response.json()["ai_response"] # 4000 - 7%

def test_portal_webhook_immobiliare(client, mock_external_services):
    """Verify specific format parsing for Immobiliare.it leads."""
    payload = {
        "contact_name": "Portal User",
        "contact_phone": "3331112223",
        "property_title": "Bilocale Lussuoso",
        "source": "immobiliare.it"
    }
    # Webhooks require the security key
    response = client.post(
        "/webhooks/immobiliare", 
        json=payload,
        headers={"x-webhook-key": "test_webhook_secret"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Portal User" in response.json()["message"]

def test_rate_limiting_api(client, mock_external_services):
    """Verify that multiple requests from the same phone number are throttled."""
    payload = {
        "name": "Spammer",
        "phone": "+39000000000",
        "agency": "Test",
        "properties": "Spam msg"
    }
    
    # Send 20 requests (the limit)
    for _ in range(20):
        client.post("/api/leads", json=payload)
        
    # The 21st should fail
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

from unittest.mock import MagicMock
