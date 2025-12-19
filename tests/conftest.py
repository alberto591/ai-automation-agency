import pytest
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock environmental variables for testing
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"
os.environ["MISTRAL_API_KEY"] = "mock_mistral_key"
os.environ["TWILIO_ACCOUNT_SID"] = "mock_sid"
os.environ["TWILIO_AUTH_TOKEN"] = "mock_token"
os.environ["TWILIO_PHONE_NUMBER"] = "+1234567890"
os.environ["AGENCY_OWNER_PHONE"] = "+39123456789"
os.environ["WEBHOOK_API_KEY"] = "test_webhook_secret"

@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Resets the in-memory rate limit stores before each test."""
    from api import rate_limit_store, phone_limit_store
    rate_limit_store.clear()
    phone_limit_store.clear()
    yield

@pytest.fixture(autouse=True)
def mock_external_services():
    """Globally mocks external services to avoid real API calls."""
    with patch("lead_manager.supabase") as mock_supabase, \
         patch("lead_manager.mistral") as mock_mistral, \
         patch("lead_manager.twilio_client") as mock_twilio, \
         patch("market_scraper.supabase") as mock_scraper_supabase:
        
        # Setup common mock behaviors
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[])
        
        mock_mistral.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="AI Mock Response"))]
        )
        
        mock_twilio.messages.create.return_value = MagicMock(sid="SMmock123")
        
        yield {
            "supabase": mock_supabase,
            "mistral": mock_mistral,
            "twilio": mock_twilio,
            "scraper_supabase": mock_scraper_supabase
        }

@pytest.fixture
def client():
    """FastAPI test client."""
    from api import app
    return TestClient(app)
