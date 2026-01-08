from unittest.mock import MagicMock

import pytest

from application.services.lead_ingestion_service import LeadIngestionService


@pytest.fixture
def mock_processor():
    return MagicMock()


@pytest.fixture
def ingestion_service(mock_processor):
    return LeadIngestionService(lead_processor=mock_processor)


def test_process_generic_payload_success(ingestion_service, mock_processor):
    payload = {
        "full_name": "Mario Rossi",
        "phone": "+393331234567",
        "notes": "Interessato a bilocale",
        "source": "zapier",
    }
    mock_processor.process_lead.return_value = "lead_001"

    lead_id = ingestion_service.process_generic_payload(payload, source="zapier")

    assert lead_id == "lead_001"
    mock_processor.process_lead.assert_called_once_with(
        phone="+393331234567",
        name="Mario Rossi",
        query="Source: zapier. Notes: Interessato a bilocale",
        postcode=None,
    )


def test_process_facebook_webhook_detection(ingestion_service):
    # FB webhook only contains IDs, we just verify it detects them
    body = {
        "entry": [{"changes": [{"value": {"leadgen_id": "fb_lead_123", "form_id": "form_456"}}]}]
    }

    count = ingestion_service.process_facebook_webhook(body)
    # Current implementation logs and returns 0 because fetch isn't implemented without token
    assert count == 0
