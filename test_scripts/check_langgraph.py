"""Verification script for LangGraph workflow.

This script tests that the LangGraph-based lead processing workflow
is correctly wired and functional with mocked dependencies.
"""

import os
import sys
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.workflows.agents import (
    AgentState,
    PropertyPreferences,
    SentimentAnalysis,
    create_lead_processing_graph,
)
from domain.ports import AIPort, DatabasePort, MessagingPort


def create_mock_ports() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Create mocked ports for testing."""
    mock_db = MagicMock(spec=DatabasePort)
    mock_db.get_lead.return_value = {
        "customer_phone": "+39333000000",
        "customer_name": "Test User",
        "is_ai_active": True,
        "messages": [],
        "status": "active",
        "journey_state": "active",
    }
    mock_db.get_properties.return_value = [
        {"title": "Test Villa", "price": 500000, "similarity": 0.85}
    ]
    mock_db.get_cached_response.return_value = None
    mock_db.get_market_stats.return_value = {"avg_price_sqm": 3500}

    mock_ai = MagicMock(spec=AIPort)
    mock_ai.get_embedding.return_value = [0.1] * 1024

    # Mock LLM with structured output capability
    # Must return real Pydantic objects, not MagicMocks, for JSON serialization
    from application.workflows.agents import (
        IntentExtraction,
        PropertyPreferences,
        SentimentAnalysis,
    )

    mock_intent = IntentExtraction(budget=500000, intent="VISIT", entities=["Milano"])
    mock_prefs = PropertyPreferences(
        rooms=[3], zones=["Milano"], features=["balcony"], property_types=["apartment"]
    )
    mock_sentiment = SentimentAnalysis(sentiment="POSITIVE", urgency="MEDIUM", notes="Test user")

    def get_structured_mock(model):
        """Return a mock that returns the correct Pydantic object based on model."""
        m = MagicMock()
        if model == IntentExtraction:
            m.invoke.return_value = mock_intent
        elif model == PropertyPreferences:
            m.invoke.return_value = mock_prefs
        elif model == SentimentAnalysis:
            m.invoke.return_value = mock_sentiment
        else:
            # For generation, return a mock response
            mock_response = MagicMock()
            mock_response.content = "Ciao! Ecco alcune opzioni interessanti per te..."
            m.invoke.return_value = mock_response
        return m

    mock_llm = MagicMock()
    mock_llm.with_structured_output.side_effect = get_structured_mock
    # For direct invoke (generation node)
    mock_generation_response = MagicMock()
    mock_generation_response.content = "Ciao! Ecco alcune opzioni interessanti per te a Milano."
    mock_llm.invoke.return_value = mock_generation_response
    mock_ai.llm = mock_llm

    mock_msg = MagicMock(spec=MessagingPort)

    return mock_db, mock_ai, mock_msg


def test_graph_creation() -> None:
    """Test that the graph can be created and invoked."""
    print("Testing LangGraph workflow creation...")
    mock_db, mock_ai, mock_msg = create_mock_ports()

    graph = create_lead_processing_graph(
        db=mock_db,
        ai=mock_ai,
        msg=mock_msg,
        journey=None,
        scraper=None,
        market=None,
        calendar=None,
    )

    print("Graph created successfully.")
    print(f"Graph type: {type(graph)}")

    # Test invocation
    print("\nTesting graph invocation...")
    inputs: AgentState = {
        "phone": "+39333000000",
        "user_input": "Cerco una casa a Milano con budget 500k",
        "name": "Test User",
        "postcode": None,
        "lead_data": {},
        "history_text": "",
        "embedding": None,
        "budget": None,
        "intent": None,
        "entities": [],
        "preferences": PropertyPreferences(),
        "sentiment": SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="Init"),
        "retrieved_properties": [],
        "market_data": {},
        "negotiation_data": {},
        "status_msg": "",
        "ai_response": "",
        "source": "WHATSAPP",
        "context_data": {},
        "checkpoint": "continue",
        "language": "it",
    }

    result = graph.invoke(inputs)

    if result.get("ai_response") or result.get("checkpoint") == "done":
        print("\n✅ LangGraph verification SUCCESSFUL!")
        print(f"   Response preview: {str(result.get('ai_response', ''))[:80]}...")
        print(f"   Checkpoint: {result.get('checkpoint')}")
    else:
        print("\n❌ LangGraph verification FAILED: No response or unexpected state.")
        print(f"   Result: {result}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        test_graph_creation()
    except Exception as e:
        print(f"\n❌ Verification FAILED with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
