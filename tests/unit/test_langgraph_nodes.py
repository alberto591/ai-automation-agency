"""Unit tests for LangGraph nodes in agents.py.

Tests each node's behavior through graph invocation with proper state setup.
"""

from unittest.mock import MagicMock

import pytest

from application.workflows.agents import (
    IntentExtraction,
    PropertyPreferences,
    SentimentAnalysis,
    create_lead_processing_graph,
)
from domain.enums import LeadStatus
from domain.ports import AIPort, DatabasePort, MessagingPort
from infrastructure.ml.feature_engineering import PropertyFeatures


@pytest.fixture
def mock_db():
    """Mock database port."""
    db = MagicMock(spec=DatabasePort)

    # Track saved leads to simulate proper new lead creation
    saved_leads = {}

    def save_lead_side_effect(lead_data):
        phone = lead_data.get("customer_phone")
        if phone:
            saved_leads[phone] = {**lead_data, "id": "test-lead-uuid"}
        return {"id": "test-lead-uuid"}

    def get_lead_side_effect(phone):
        return saved_leads.get(phone)

    db.get_lead.side_effect = get_lead_side_effect
    db.save_lead.side_effect = save_lead_side_effect
    db.get_properties.return_value = []
    db.get_cached_response.return_value = None
    db.get_market_stats.return_value = {"avg_price_sqm": 3500}
    return db


@pytest.fixture
def mock_ai():
    """Mock AI port with LangChain adapter."""
    ai = MagicMock(spec=AIPort)
    ai.get_embedding.return_value = [0.1] * 1024

    # Mock LLM with structured output
    mock_llm = MagicMock()

    # Default structured output responses
    def get_structured_mock(model):
        m = MagicMock()
        if model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(budget=0, intent="INFO", entities=[])
        elif model == PropertyPreferences:
            m.invoke.return_value = PropertyPreferences(
                rooms=[3], zones=["Milano"], features=["balcony"], property_types=["apartment"]
            )
        elif model == SentimentAnalysis:
            m.invoke.return_value = SentimentAnalysis(
                sentiment="POSITIVE", urgency="MEDIUM", notes="Interested buyer"
            )
        elif model == PropertyFeatures:
            m.invoke.return_value = PropertyFeatures(
                sqm=85, floor=2, has_elevator=True, condition="excellent"
            )
        return m

    mock_llm.with_structured_output.side_effect = get_structured_mock

    # Mock generation response
    mock_response = MagicMock()
    mock_response.content = "AI generated response"
    mock_llm.invoke.return_value = mock_response

    ai.llm = mock_llm

    return ai


@pytest.fixture
def mock_msg():
    """Mock messaging port."""
    return MagicMock(spec=MessagingPort)


# =============================================================================
# INGEST NODE TESTS (via graph invocation)
# =============================================================================


def test_ingest_node_new_lead_creation(mock_db, mock_ai, mock_msg):
    """Test that ingest_node creates a new lead when none exists."""
    mock_db.get_lead.return_value = None
    mock_db.get_properties.return_value = [
        {"title": "Test Property", "price": 400000, "similarity": 0.85}
    ]


# =============================================================================
# FIFI APPRAISAL NODE TESTS
# =============================================================================


def test_fifi_appraisal_node_logic(mock_db, mock_ai, mock_msg):
    """Test the specialized appraisal node."""
    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    state = {
        "phone": "+39123456789",
        "user_input": "Valutazione casa 90mq",
        "source": "FIFI_APPRAISAL",
        "lead_data": {"id": "test-id"},
        "history_text": "",
        "checkpoint": "continue",
        "language": "it",
    }

    # Mock properties for uncertainty calc
    mock_db.get_properties.return_value = [
        {"title": "Comp 1", "price": 440000, "sale_price_eur": 440000, "similarity": 0.9},
        {"title": "Comp 2", "price": 460000, "sale_price_eur": 460000, "similarity": 0.9},
    ]

    # We need to manually call the node or run the graph.
    # The node is internal, so we run the graph.
    res = graph.invoke(state)

    assert "fifi_data" in res
    fifi = res["fifi_data"]
    assert fifi["predicted_value"] > 0
    assert fifi["fifi_status"] == "AUTO_APPROVED"
    assert "€" in fifi["confidence_range"]

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa",
            "name": "New User",
            "postcode": None,
        }
    )

    # Verify lead was saved
    assert mock_db.save_lead.called
    # Verify AI response generated
    assert result["ai_response"]
    # Verify message sent
    assert mock_msg.send_message.called


def test_ingest_node_language_detection_italian(mock_db, mock_ai, mock_msg):
    """Test language detection for Italian phone number."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = []

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Ciao, cerco casa",
            "name": None,
            "postcode": None,
        }
    )

    # Language should be detected as Italian
    assert result["language"] == "it"


def test_ingest_node_language_detection_english(mock_db, mock_ai, mock_msg):
    """Test language detection for English (non-Italian phone + English keywords)."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+44123456789",
        "customer_name": "Tourist",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = []

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+44123456789",
            "user_input": "Hello, looking for a house",
            "name": None,
            "postcode": None,
        }
    )

    # Language should be detected as English
    assert result["language"] == "en"


def test_ingest_node_source_detection_appraisal(mock_db, mock_ai, mock_msg):
    """Test source detection for FIFI_APPRAISAL."""
    mock_db.get_lead.return_value = None
    mock_db.get_properties.return_value = []

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Vorrei una valutazione della mia casa",
            "name": "User",
            "postcode": "50100",
        }
    )

    # Source should be detected as WEB_APPRAISAL
    assert result["source"] == "FIFI_APPRAISAL"


def test_ingest_node_human_mode_stops_processing(mock_db, mock_ai, mock_msg):
    """Test that human mode stops AI processing."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": False,  # Human mode
        "messages": [],
    }

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Test message",
            "name": None,
            "postcode": None,
        }
    )

    # Should stop at ingest with human_mode checkpoint
    assert result["checkpoint"] == "human_mode"
    # Should not send message
    assert not mock_msg.send_message.called


# =============================================================================
# INTENT NODE TESTS
# =============================================================================


def test_intent_node_extracts_budget_and_intent(mock_db, mock_ai, mock_msg):
    """Test that intent_node extracts budget and intent correctly."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
        "journey_state": LeadStatus.ACTIVE,
    }
    mock_db.get_properties.return_value = []

    # Override default mock to return specific intent extraction
    def get_structured_mock_intent(model):
        m = MagicMock()
        if model == IntentExtraction:
            m.invoke.return_value = IntentExtraction(
                budget=500000, intent="PURCHASE", entities=["Milano", "Porta Nuova"]
            )
        elif model == PropertyPreferences:
            m.invoke.return_value = PropertyPreferences(
                rooms=[3], zones=["Milano"], features=[], property_types=["apartment"]
            )
        elif model == SentimentAnalysis:
            m.invoke.return_value = SentimentAnalysis(
                sentiment="POSITIVE", urgency="MEDIUM", notes="Interested buyer"
            )
        return m

    mock_ai.llm.with_structured_output.side_effect = get_structured_mock_intent

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa a Milano con budget 500k",
            "name": None,
            "postcode": None,
        }
    )

    # Verify budget and intent extracted
    assert result["budget"] == 500000
    assert result["intent"] == "buy"
    assert result["qualification_data"]["intent"] == "buy"
    assert result["qualification_data"]["budget"] == 500000
    assert "Milano" in result["entities"]


# =============================================================================
# CACHE NODE TESTS
# =============================================================================


def test_cache_check_node_returns_cached_response(mock_db, mock_ai, mock_msg):
    """Test that cache_check_node returns cached response when available."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_cached_response.return_value = "This is a cached response"

    # Ensure intent doesn't trigger qualification
    mock_ai.llm.with_structured_output(IntentExtraction).invoke.return_value = IntentExtraction(
        budget=0, intent="INFO", entities=[]
    )

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa",
            "name": None,
            "postcode": None,
        }
    )

    # Should return cached response
    assert result["ai_response"] == "This is a cached response"
    assert result["checkpoint"] == "done"


def test_cache_check_node_continues_when_no_cache(mock_db, mock_ai, mock_msg):
    """Test that cache_check_node continues processing when no cache."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_cached_response.return_value = None
    mock_db.get_properties.return_value = []

    # Ensure intent doesn't trigger qualification
    mock_ai.llm.with_structured_output(IntentExtraction).invoke.return_value = IntentExtraction(
        budget=0, intent="INFO", entities=[]
    )

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa",
            "name": None,
            "postcode": None,
        }
    )

    # Should generate new response
    assert result["ai_response"] != ""
    assert result["checkpoint"] == "done"
    # Should save to cache
    assert mock_db.save_to_cache.called


# =============================================================================
# RETRIEVAL NODE TESTS
# =============================================================================


def test_retrieval_node_filters_by_similarity(mock_db, mock_ai, mock_msg):
    """Test that retrieval_node filters properties by similarity threshold."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = [
        {"title": "High Match", "price": 450000, "similarity": 0.92},
        {"title": "Good Match", "price": 380000, "similarity": 0.85},
        {"title": "Low Match", "price": 300000, "similarity": 0.65},  # Below threshold
    ]

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa Milano",
            "name": None,
            "postcode": None,
        }
    )

    # Should only include properties above 0.78 threshold
    assert len(result["retrieved_properties"]) == 2
    assert all(p["similarity"] >= 0.78 for p in result["retrieved_properties"])


def test_retrieval_node_fallback_mechanism(mock_db, mock_ai, mock_msg):
    """Test retrieval_node fallback when no properties above threshold."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = [
        {"title": "Property 1", "price": 300000, "similarity": 0.65},
        {"title": "Property 2", "price": 350000, "similarity": 0.60},
        {"title": "Property 3", "price": 400000, "similarity": 0.55},
    ]

    # Ensure intent doesn't trigger qualification
    mock_ai.llm.with_structured_output(IntentExtraction).invoke.return_value = IntentExtraction(
        budget=0, intent="INFO", entities=[]
    )

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa",
            "name": None,
            "postcode": None,
        }
    )

    # Should return top 2 as fallback
    assert len(result["retrieved_properties"]) == 2
    # Should set status message about alternatives
    assert "closest alternatives" in result["status_msg"]


# =============================================================================
# FINALIZE NODE TESTS
# =============================================================================


def test_finalize_node_sends_message_and_updates_db(mock_db, mock_ai, mock_msg):
    """Test that finalize_node sends message and updates database."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = []

    # Ensure intent doesn't trigger qualification
    mock_ai.llm.with_structured_output(IntentExtraction).invoke.return_value = IntentExtraction(
        budget=0, intent="INFO", entities=[]
    )

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    result = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa",
            "name": None,
            "postcode": None,
        }
    )

    # Verify message sent
    assert mock_msg.send_message.called
    # Verify database updated with metadata
    assert mock_db.update_lead.called
    # Verify final checkpoint
    assert result["checkpoint"] == "done"


def test_finalize_node_saves_metadata(mock_db, mock_ai, mock_msg):
    """Test that finalize_node persists enriched metadata."""
    # Clear side_effect to use return_value
    mock_db.get_lead.side_effect = None
    mock_db.get_lead.return_value = {
        "id": "test-lead-uuid",
        "customer_phone": "+39333000000",
        "customer_name": "Test",
        "is_ai_active": True,
        "messages": [],
    }
    mock_db.get_properties.return_value = []

    graph = create_lead_processing_graph(mock_db, mock_ai, mock_msg)

    # Run the graph with metadata saving
    _ = graph.invoke(
        {
            "phone": "+39333000000",
            "user_input": "Cerco casa Milano budget 500k",
            "name": None,
            "postcode": None,
        }
    )

    # Verify update_lead was called with metadata
    update_calls = mock_db.update_lead.call_args_list
    assert len(update_calls) > 0

    # Check that final call includes metadata
    # update_lead is called as: db.update_lead(phone, update_payload)
    # So call_args_list[-1] will be ((phone, payload), kwargs)
    final_call_args = update_calls[-1][0]  # positional args tuple
    update_payload = final_call_args[1]  # second arg is the payload dict
    assert "metadata" in update_payload
    assert "preferences" in update_payload["metadata"]
    assert "sentiment" in update_payload["metadata"]
