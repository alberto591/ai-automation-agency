import os
from unittest.mock import patch

import sys
from unittest.mock import MagicMock

# MOCK HEAVY DEPENDENCIES IF MISSING (For CI)
# This allows running unit tests without installing 500MB+ of ML libraries
heavy_modules = [
    "xgboost",
    "sklearn",
    "sklearn.metrics",
    "sklearn.model_selection",
    "sklearn.preprocessing",
    "langchain",
    "langchain.tools",
    "langchain_core",
    "langchain_core.prompts",
    "langchain_mistralai",
    "mistralai",
    "numpy",
    "pandas",
    "openai",
    "tiktoken",
    "langgraph",
    "langgraph.prebuilt"
]

for mod in heavy_modules:
    try:
        __import__(mod)
    except ImportError:
        # Create a mock module
        mock_mod = MagicMock()
        # Ensure it has __path__ so sub-imports might work if not explicitly in list
        mock_mod.__path__ = []
        sys.modules[mod] = mock_mod

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def skip_ml_if_mocked(request):
    """Skip tests marked with @pytest.mark.ml_required if heavy deps are mocked."""
    if request.node.get_closest_marker("ml_required"):
        # Check if xgboost is a mock (proxy for all heavy deps)
        import xgboost
        if isinstance(xgboost, MagicMock) or isinstance(sys.modules.get("xgboost"), MagicMock):
            pytest.skip("Skipping ML test: dependencies are mocked")


# Mock environmental variables BEFORE any imports that might trigger Container instantiation
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"
os.environ["SUPABASE_JWT_SECRET"] = "mock_jwt_secret"
os.environ["MISTRAL_API_KEY"] = "mock_mistral_key"
os.environ["TWILIO_ACCOUNT_SID"] = "mock_sid"
os.environ["TWILIO_AUTH_TOKEN"] = "mock_token"
os.environ["TWILIO_PHONE_NUMBER"] = "+1234567890"
os.environ["WEBHOOK_API_KEY"] = "test_webhook_secret"
os.environ["WHATSAPP_PROVIDER"] = "twilio"
os.environ["CALCOM_API_KEY"] = "mock_calcom_key"
os.environ["CALCOM_EVENT_TYPE_ID"] = "123"
os.environ["CALCOM_WEBHOOK_SECRET"] = "mock_calcom_secret"
os.environ["AGENCY_OWNER_PHONE"] = "+391234567890"
os.environ["AGENCY_OWNER_EMAIL"] = "test@example.com"


@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    with patch("config.settings.settings") as mock_set:
        mock_set.WEBHOOK_API_KEY = "test_webhook_secret"
        mock_set.MISTRAL_MODEL = "mistral-large-latest"
        mock_set.MISTRAL_EMBEDDING_MODEL = "mistral-embed"
        mock_set.MISTRAL_API_KEY = "mock_key"
        mock_set.CALCOM_API_KEY = "mock_key"
        mock_set.CALCOM_EVENT_TYPE_ID = "mock_event_type"
        mock_set.CALCOM_WEBHOOK_SECRET = "mock_secret"
        mock_set.SUPABASE_URL = "https://mock.supabase.co"
        mock_set.SUPABASE_KEY = "mock_key"
        mock_set.RAPIDAPI_KEY = None  # Crucial for triggering fallbacks in MarketDataService tests
        mock_set.AGENCY_OWNER_PHONE = "3912345678"
        mock_set.AGENCY_OWNER_EMAIL = "test@example.com"
        yield mock_set


@pytest.fixture(autouse=True)
def mock_container():
    """Mocks the DI container components."""
    # We patch the singleton at its source
    with patch("config.container.container") as mock_cnt:
        # Define default successful mocks for lead_processor
        mock_cnt.lead_processor.process_lead.return_value = "AI Response"
        mock_cnt.lead_processor.takeover.return_value = None
        mock_cnt.lead_processor.resume.return_value = None
        mock_cnt.lead_processor.update_lead_details.return_value = None
        mock_cnt.lead_processor.send_manual_message.return_value = "mock_sid"
        mock_cnt.lead_processor.add_message_history.return_value = None
        mock_cnt.lead_processor.sync_lead.return_value = None

        # Define mocks for journey
        mock_cnt.journey.transition_to.return_value = None

        # Define mocks for appraisal_service
        mock_cnt.appraisal_service.estimate_value.return_value = {
            "estimated_value": 450000.0,
            "estimated_range_min": 430000.0,
            "estimated_range_max": 470000.0,
            "avg_price_sqm": 4736.0,
            "price_sqm_min": 4526.0,
            "price_sqm_max": 4947.0,
            "comparables": [],
            "reasoning": "Estimated based on market data",
            "market_trend": "stable",
        }

        # Also patch in modules that might have already imported it
        # or will import it via 'from ... import ...'
        try:
            import presentation.api.api

            with patch.object(presentation.api.api, "container", mock_cnt):
                yield mock_cnt
        except (ImportError, AttributeError):
            # Fallback for tests that don't load the API or environments where discovery fails
            yield mock_cnt


@pytest.fixture
def client():
    """FastAPI test client."""
    from presentation.api.api import app
    from presentation.middleware.auth import get_current_user

    # Override auth to bypass JWT check in tests
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test_user",
        "role": "authenticated",
    }

    yield TestClient(app)

    # Cleanup
    app.dependency_overrides = {}
