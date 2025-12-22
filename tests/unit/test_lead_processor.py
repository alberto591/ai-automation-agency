from unittest.mock import MagicMock

import pytest

from application.services.lead_processor import LeadProcessor, LeadScorer
from domain.ports import DatabasePort, MessagingPort
from infrastructure.adapters.langchain_adapter import LangChainAdapter


@pytest.fixture
def mock_db():
    return MagicMock(spec=DatabasePort)


@pytest.fixture
def mock_ai():
    mock = MagicMock(spec=LangChainAdapter)
    mock.llm = MagicMock()
    return mock


@pytest.fixture
def mock_msg():
    return MagicMock(spec=MessagingPort)


@pytest.fixture
def scorer():
    return LeadScorer()


@pytest.fixture
def processor(mock_db, mock_ai, mock_msg, scorer):
    return LeadProcessor(mock_db, mock_ai, mock_msg, scorer)


def test_lead_scoring(scorer):
    # Test high intent
    score = scorer.calculate_score("Vorrei visitare una casa domani pomeriggio")
    assert score >= 45

    # Test zero intent
    assert scorer.calculate_score("Buongiorno") == 0


def test_process_lead_success(processor, mock_db, mock_ai, mock_msg):
    # Mock LLM for intent extraction
    from application.workflows.agents import (
        IntentExtraction,
        PropertyPreferences,
        SentimentAnalysis,
    )

    mock_extraction = IntentExtraction(budget=100000, intent="VISIT", entities=["Milano"])
    mock_prefs = PropertyPreferences(
        rooms=[3], zones=["Milano"], features=["balcony"], property_types=["apartment"]
    )
    mock_sentiment = SentimentAnalysis(sentiment="POSITIVE", urgency="MEDIUM", notes="Happy user")

    # Setup mock_ai.llm.with_structured_output to return different mocks for different models
    def get_structured_mock(model):
        m = MagicMock()
        if model == IntentExtraction:
            m.invoke.return_value = mock_extraction
        elif model == PropertyPreferences:
            m.invoke.return_value = mock_prefs
        elif model == SentimentAnalysis:
            m.invoke.return_value = mock_sentiment
        return m

    mock_ai.llm.with_structured_output.side_effect = get_structured_mock

    # Mock LLM for generation
    mock_response = MagicMock()
    mock_response.content = "AI Response"
    mock_ai.llm.invoke.return_value = mock_response

    # Mock other ports
    mock_db.get_properties.return_value = [
        {"title": "Test Prop", "price": 100000, "similarity": 0.9}
    ]
    mock_db.get_cached_response.return_value = None
    mock_db.get_lead.return_value = {
        "customer_phone": "+39333000000",
        "customer_name": "Test User",
        "is_ai_active": True,
        "messages": [],
    }
    mock_ai.get_embedding.return_value = [0.1] * 1024

    response = processor.process_lead(
        "+39333000000", "Test User", "Cerco casa e vorrei visitare un appartamento subito"
    )

    assert response == "AI Response"
    mock_msg.send_message.assert_called_once()
    assert mock_db.save_lead.call_count >= 1
