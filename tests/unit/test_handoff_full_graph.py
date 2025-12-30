from unittest.mock import MagicMock, patch

import pytest

from application.workflows.agents import create_lead_processing_graph
from domain.handoff import HandoffReason
from domain.ports import AIPort, DatabasePort, MessagingPort


@pytest.fixture
def mock_db():
    db = MagicMock(spec=DatabasePort)
    saved_leads = {}

    def save_lead_side_effect(lead_data):
        phone = lead_data.get("customer_phone")
        if phone:
            saved_leads[phone] = {**lead_data, "id": "test-id"}
        return {"id": "test-id"}

    def get_lead_side_effect(phone):
        return saved_leads.get(phone)

    def update_lead_side_effect(phone, data):
        if phone in saved_leads:
            saved_leads[phone].update(data)

    db.save_lead.side_effect = save_lead_side_effect
    db.get_lead.side_effect = get_lead_side_effect
    db.update_lead.side_effect = update_lead_side_effect
    db.get_properties.return_value = []
    return db


@pytest.fixture
def mock_ai():
    ai = MagicMock(spec=AIPort)
    ai.get_embedding.return_value = [0.1] * 1024

    mock_llm = MagicMock()
    from application.workflows.agents import (
        IntentExtraction,
        PropertyPreferences,
        SentimentAnalysis,
    )

    def get_structured_mock(model):
        m = MagicMock()
        if model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=None, intent="INFO", entities=[])
        elif model == PropertyPreferences:
            m.invoke.return_value = PropertyPreferences(
                rooms=[], zones=[], features=[], property_types=[]
            )
        elif model == SentimentAnalysis:
            m.invoke.return_value = SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="")
        return m

    mock_llm.with_structured_output.side_effect = get_structured_mock

    # Mock generation response
    mock_response = MagicMock()
    mock_response.content = "AI response"
    mock_llm.invoke.return_value = mock_response

    ai.llm = mock_llm
    return ai


@pytest.fixture
def mock_msg():
    return MagicMock(spec=MessagingPort)


@patch("infrastructure.adapters.notification_adapter.NotificationAdapter")
def test_graph_routing_sentiment_handoff(mock_notifier, mock_db, mock_ai, mock_msg):
    """Test that ANGRY sentiment routes to Handoff Node."""
    from application.workflows.agents import (
        IntentExtraction,
        PropertyPreferences,
        SentimentAnalysis,
    )

    # 1. Setup Mock for Sentiment and Ensure others are real models
    def specific_structured_mock(model):
        m = MagicMock()
        if model == SentimentAnalysis:
            m.invoke.return_value = SentimentAnalysis(
                sentiment="ANGRY", urgency="HIGH", notes="Mad"
            )
        elif model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=None, intent="INFO", entities=[])
        elif model == PropertyPreferences:
            m.invoke.return_value = PropertyPreferences(
                rooms=[], zones=[], features=[], property_types=[]
            )
        return m

    mock_ai.llm.with_structured_output.side_effect = specific_structured_mock

    # 2. Create Graph
    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)
    mock_db.save_lead({"customer_phone": "+39333999888", "customer_name": "Angry User"})

    result = graph.invoke(
        {
            "phone": "+39333999888",
            "user_input": "Voglio parlare con un umano adesso! Basta AI!",
            "name": "Angry User",
            "postcode": None,
        }
    )

    assert "Handed off" in result.get("status_msg", "")
    instance = mock_notifier.return_value
    instance.notify_agency.assert_called_once()
    req = instance.notify_agency.call_args[0][0]
    assert req.reason == HandoffReason.SENTIMENT
    assert req.priority == "urgent"


@patch("infrastructure.adapters.notification_adapter.NotificationAdapter")
def test_graph_routing_keyword_handoff(mock_notifier, mock_db, mock_ai, mock_msg):
    """Test that 'parlare con agente' triggers Handoff."""
    from application.workflows.agents import (
        IntentExtraction,
        PropertyPreferences,
        SentimentAnalysis,
    )

    # Neutral Sentiment but Keyword match
    def specific_mock(model):
        m = MagicMock()
        if model == SentimentAnalysis:
            m.invoke.return_value = SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="")
        elif model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=None, intent="INFO", entities=[])
        elif model == PropertyPreferences:
            m.invoke.return_value = PropertyPreferences(
                rooms=[], zones=[], features=[], property_types=[]
            )
        return m

    mock_ai.llm.with_structured_output.side_effect = specific_mock

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)
    mock_db.save_lead({"customer_phone": "+39333777666", "customer_name": "Curious User"})

    result = graph.invoke(
        {
            "phone": "+39333777666",
            "user_input": "Posso parlare con un agente umano per favore?",
            "name": "Curious User",
            "postcode": None,
        }
    )

    assert "Handed off" in result.get("status_msg", "")
    instance = mock_notifier.return_value
    instance.notify_agency.assert_called_once()
    req = instance.notify_agency.call_args[0][0]
    assert req.reason == HandoffReason.USER_REQUEST


@patch("infrastructure.adapters.notification_adapter.NotificationAdapter")
def test_graph_routing_high_value_handoff(mock_notifier, mock_db, mock_ai, mock_msg):
    """Test that High Value appraisal triggers Handoff."""
    from application.workflows.agents import IntentExtraction

    # 1. Mock intent to be INFO (but source will be set to FIFI_APPRAISAL via input)
    mock_intent_tool = MagicMock()
    mock_intent_tool.invoke.return_value = IntentExtraction(budget=None, intent="INFO", entities=[])

    def specific_mock(model):
        m = MagicMock()
        if model == IntentExtraction:
            return mock_intent_tool
        return m

    mock_ai.llm.with_structured_output.side_effect = specific_mock

    # 2. Mock DB to return properties (needed for fifi_node if it calculates uncertainty)
    mock_db.get_properties.return_value = []

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)
    mock_db.save_lead({"customer_phone": "+39333555444", "customer_name": "Rich User"})

    # 3. Simulate High Value Appraisal
    # We need to ensure the XGBoostAdapter (simulated) returns > 2M.
    # Since XGBoostAdapter is currently a simulator in the node, we can patch its predict.
    with patch("infrastructure.ml.xgboost_adapter.XGBoostAdapter.predict", return_value=2500000.0):
        result = graph.invoke(
            {
                "phone": "+39333555444",
                "user_input": "Valutazione villa di lusso 500mq",
                "name": "Rich User",
                "source": "FIFI_APPRAISAL",  # Mandatory for Fifi node execution
            }
        )

    assert "Handed off" in result.get("status_msg", "")
    instance = mock_notifier.return_value
    instance.notify_agency.assert_called_once()
    req = instance.notify_agency.call_args[0][0]
    assert req.reason == HandoffReason.HIGH_VALUE
    assert req.priority == "urgent"
