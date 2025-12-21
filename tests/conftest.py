import pytest
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock environmental variables
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"
os.environ["MISTRAL_API_KEY"] = "mock_mistral_key"
os.environ["TWILIO_ACCOUNT_SID"] = "mock_sid"
os.environ["TWILIO_AUTH_TOKEN"] = "mock_token"
os.environ["TWILIO_PHONE_NUMBER"] = "+1234567890"
os.environ["WEBHOOK_API_KEY"] = "test_webhook_secret"

@pytest.fixture(autouse=True)
def mock_container():
    """Mocks the DI container components."""
    with patch("config.container.container") as mock_cnt:
        mock_cnt.lead_processor.process_lead.return_value = "AI Mock Response"
        yield mock_cnt

@pytest.fixture
def client():
    """FastAPI test client."""
    from presentation.api.api import app
    return TestClient(app)
