"""Unit tests for AVM Audit Logging (ADR 046)."""

from unittest.mock import MagicMock, patch

import pytest

from application.workflows.agents import AgentState, create_lead_processing_graph
from domain.enums import LeadStatus
from domain.ports import AIPort, DatabasePort, MessagingPort
from infrastructure.ml.feature_engineering import PropertyFeatures


@pytest.fixture
def mock_validation():
    return MagicMock()


@patch("infrastructure.ml.feature_engineering.extract_property_features")
def test_fifi_appraisal_node_triggers_audit_log(mock_extract, mock_validation):
    """Verify that appraisal node calls validation.log_validation."""
    mock_extract.return_value = PropertyFeatures(
        sqm=100, floor=3, has_elevator=True, condition="good", zone_slug="milano-centro"
    )
    mock_db = MagicMock(spec=DatabasePort)
    mock_ai = MagicMock(spec=AIPort)
    mock_msg = MagicMock(spec=MessagingPort)

    # Mock DB returns
    mock_db.get_lead.return_value = {
        "id": "test-lead-id",
        "customer_phone": "+39123456789",
        "customer_name": "Test User",
        "is_ai_active": True,
        "journey_state": LeadStatus.ACTIVE,
    }
    mock_db.get_properties.return_value = []
    mock_db.get_market_stats.return_value = {"avg_price_sqm": 3500}

    # Mock AI returns
    mock_ai.get_embedding.return_value = [0.1] * 1024

    # Mock Sentiment / Preferences
    from application.workflows.agents import PropertyPreferences, SentimentAnalysis

    sentiment = SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="")
    preferences = PropertyPreferences()

    mock_llm = MagicMock()
    # Structured output for PropertyFeatures (ML simulation)
    from application.workflows.agents import IntentExtraction

    def get_structured_mock(model):
        m = MagicMock()
        if model == PropertyFeatures:
            m.invoke.return_value = PropertyFeatures(
                sqm=100, floor=3, has_elevator=True, condition="good", zone_slug="milano-centro"
            )
        elif model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=0, intent="INFO", entities=[])
        elif model == SentimentAnalysis:
            m.invoke.return_value = sentiment
        elif model == PropertyPreferences:
            m.invoke.return_value = preferences
        return m

    mock_llm.with_structured_output.side_effect = get_structured_mock
    mock_ai.llm = mock_llm

    # Create graph with validation port
    graph = create_lead_processing_graph(
        db=mock_db, ai=mock_ai, msg=mock_msg, validation=mock_validation
    )

    state: AgentState = {
        "phone": "+39123456789",
        "user_input": "Valuta appartamento 100mq in centro",
        "source": "FIFI_APPRAISAL",
        "lead_data": {
            "id": "test-lead-id",
            "address": "Via Torino 1",
            "journey_state": LeadStatus.ACTIVE,
        },
        "history_text": "",
        "checkpoint": "continue",
        "language": "it",
        "fifi_data": {},
        "retrieved_properties": [],
        "qualification_data": {},
        "lead_score": {},
        "sentiment": MagicMock(),
        "preferences": MagicMock(),
    }

    # Invoke graph - it should run fifi_appraisal_node
    # Note: ingest will overwrite lead_data if we don't mock it to match
    graph.invoke(state)

    # Assert validation.log_validation was called
    assert mock_validation.log_validation.called
    args, kwargs = mock_validation.log_validation.call_args
    assert kwargs["predicted_value"] > 0
    assert kwargs["metadata"]["phone"] == "+39123456789"
    assert kwargs["zone"] == "milano-centro"


@patch("infrastructure.ml.feature_engineering.extract_property_features")
def test_fifi_appraisal_node_handles_logging_failure(mock_extract, mock_validation):
    """Verify that appraisal node doesn't crash if logging fails."""
    mock_extract.return_value = PropertyFeatures(
        sqm=100, floor=3, has_elevator=True, condition="good", zone_slug="milano-centro"
    )
    mock_validation.log_validation.side_effect = Exception("DB Connection Error")

    mock_db = MagicMock(spec=DatabasePort)
    mock_ai = MagicMock(spec=AIPort)
    mock_msg = MagicMock(spec=MessagingPort)
    # Mock DB returns
    mock_db.get_lead.return_value = {
        "id": "test-id",
        "customer_phone": "+39123456789",
        "is_ai_active": True,
    }
    mock_db.get_properties.return_value = []
    mock_db.get_market_stats.return_value = {"avg_price_sqm": 3500}

    # Mock AI returns
    mock_ai.get_embedding.return_value = [0.1] * 1024
    from application.workflows.agents import PropertyPreferences, SentimentAnalysis

    sentiment = SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="")
    preferences = PropertyPreferences()

    mock_llm = MagicMock()
    from application.workflows.agents import IntentExtraction

    def get_structured_mock_2(model):
        m = MagicMock()
        if model == PropertyFeatures:
            m.invoke.return_value = PropertyFeatures(
                sqm=100, floor=3, has_elevator=True, condition="good", zone_slug="milano-centro"
            )
        elif model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=0, intent="INFO", entities=[])
        elif model == SentimentAnalysis:
            m.invoke.return_value = sentiment
        elif model == PropertyPreferences:
            m.invoke.return_value = preferences
        return m

    mock_llm.with_structured_output.side_effect = get_structured_mock_2
    mock_ai.llm = mock_llm

    graph = create_lead_processing_graph(
        db=mock_db, ai=mock_ai, msg=mock_msg, validation=mock_validation
    )

    state: AgentState = {
        "phone": "+39123456789",
        "user_input": "Valuta appartamento 100mq",
        "source": "FIFI_APPRAISAL",
        "lead_data": {"id": "test-id", "journey_state": LeadStatus.ACTIVE},
        "history_text": "",
        "checkpoint": "continue",
        "language": "it",
        "fifi_data": {},
        "retrieved_properties": [],
        "qualification_data": {},
        "lead_score": {},
        "sentiment": sentiment,
        "preferences": preferences,
    }

    # Should not raise exception
    res = graph.invoke(state)
    assert res["fifi_data"]["predicted_value"] > 0
