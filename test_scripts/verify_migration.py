import os
import sys
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.getcwd())

from application.services.lead_processor import LeadProcessor, LeadScorer
from domain.enums import LeadStatus
from domain.ports import AIPort, DatabasePort, MessagingPort


def verify_full_flow():
    print("Verifying full migrated LeadProcessor flow...")

    # Mock dependencies
    mock_db = MagicMock(spec=DatabasePort)
    mock_ai = MagicMock(spec=AIPort)
    mock_msg = MagicMock(spec=MessagingPort)
    scorer = LeadScorer()

    # Setup mocks
    mock_db.get_lead.return_value = {
        "customer_phone": "+39333000000",
        "customer_name": "Mario Rossi",
        "is_ai_active": True,
        "journey_state": LeadStatus.ACTIVE,
        "messages": [],
    }
    mock_ai.get_embedding.return_value = [0.1] * 1024
    mock_db.get_cached_response.return_value = None
    mock_db.get_properties.return_value = [
        {"title": "Appartamento Milano", "price": 500000, "similarity": 0.85}
    ]
    mock_ai.generate_response.return_value = (
        "Ciao Mario, ho trovato un appartamento a Milano per te!"
    )

    processor = LeadProcessor(mock_db, mock_ai, mock_msg, scorer)

    print("Processing message...")
    response = processor.process_lead(
        "+39333000000", "Mario Rossi", "Cerco un appartamento a Milano"
    )

    print(f"Response: {response}")
    assert "Milano" in response
    assert mock_msg.send_message.called
    assert mock_db.save_to_cache.called

    print("Migration verification SUCCESSFUL!")


if __name__ == "__main__":
    try:
        verify_full_flow()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
