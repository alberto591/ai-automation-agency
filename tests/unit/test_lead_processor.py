import pytest
from unittest.mock import MagicMock
from application.services.lead_processor import LeadProcessor, LeadScorer
from domain.ports import DatabasePort, AIPort, MessagingPort

@pytest.fixture
def mock_db():
    return MagicMock(spec=DatabasePort)

@pytest.fixture
def mock_ai():
    return MagicMock(spec=AIPort)

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
    mock_db.get_properties.return_value = [{"title": "Test Prop", "price": 100000}]
    mock_ai.generate_response.return_value = "AI Response"
    
    response = processor.process_lead("+39333000000", "Test User", "Cerco casa e vorrei visitare un appartamento subito")
    
    assert response == "AI Response"
    mock_msg.send_message.assert_called_once()
    mock_db.save_lead.assert_called_once()
