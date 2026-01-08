from unittest.mock import MagicMock

import pytest

from application.services.routing_service import RoutingService
from domain.models import Lead


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def routing_service(mock_db):
    return RoutingService(db=mock_db)


def test_assign_lead_zone_match(routing_service, mock_db):
    # Setup
    lead = Lead(phone="+39123", postcode="20121")
    mock_db.get_active_agents.return_value = [
        {"id": "agent1", "email": "a1@ex.com", "zones": ["20121"]},
        {"id": "agent2", "email": "a2@ex.com", "zones": ["20155"]},
    ]

    # Execute
    agent_id = routing_service.assign_lead(lead)

    # Assert
    assert agent_id == "agent1"


def test_assign_lead_fallback(routing_service, mock_db):
    # Setup
    lead = Lead(phone="+39123", name="No Zone")
    mock_db.get_active_agents.return_value = [
        {"id": "agent1", "email": "a1@ex.com", "zones": ["20121"]}
    ]

    # Execute
    agent_id = routing_service.assign_lead(lead)

    # Assert
    assert agent_id == "agent1"  # Only one available


def test_assign_lead_no_agents(routing_service, mock_db):
    # Setup
    lead = Lead(phone="+39123")
    mock_db.get_active_agents.return_value = []

    # Execute
    agent_id = routing_service.assign_lead(lead)

    # Assert
    assert agent_id is None
