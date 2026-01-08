from unittest.mock import Mock

import pytest

from application.services.journey_manager import JourneyManager


class TestJourneyManager:
    @pytest.fixture
    def mock_dependencies(self):
        """Setup mock dependencies for JourneyManager."""
        return {"db": Mock(), "calendar": Mock(), "doc_gen": Mock(), "msg": Mock()}

    @pytest.fixture
    def journey_manager(self, mock_dependencies):
        """Create JourneyManager instance with mocked dependencies."""
        return JourneyManager(**mock_dependencies)

    def test_send_property_brochure_records_interest(self, journey_manager, mock_dependencies):
        """Test that sending a brochure records property interest in lead metadata."""
        # Setup
        phone = "+393331234567"
        property_data = {"id": "prop-123", "title": "Luxury Apartment Milano", "price": 500000}

        # Mock existing lead with empty metadata
        mock_dependencies["db"].get_lead.return_value = {"customer_phone": phone, "metadata": {}}

        # Mock PDF generation success
        mock_dependencies["doc_gen"].generate_pdf.return_value = "/path/to/brochure.pdf"

        # Mock message sending success
        mock_dependencies["msg"].send_whatsapp.return_value = True

        # Execute
        result = journey_manager.send_property_brochure(phone, property_data)

        # Verify PDF was generated
        mock_dependencies["doc_gen"].generate_pdf.assert_called_once_with("brochure", property_data)

        # Verify metadata update was called
        mock_dependencies["db"].update_lead.assert_called_once()
        update_call = mock_dependencies["db"].update_lead.call_args

        assert update_call[0][0] == phone
        assert "metadata" in update_call[0][1]
        assert "interested_property_ids" in update_call[0][1]["metadata"]
        assert "prop-123" in update_call[0][1]["metadata"]["interested_property_ids"]

        # Verify result is the PDF path
        assert result == "/path/to/brochure.pdf"

    def test_send_property_brochure_appends_to_existing_interests(
        self, journey_manager, mock_dependencies
    ):
        """Test that new property interests are appended to existing ones."""
        # Setup
        phone = "+393331234567"
        property_data = {"id": "prop-456", "title": "Villa Roma"}

        # Mock existing lead with existing interests
        mock_dependencies["db"].get_lead.return_value = {
            "customer_phone": phone,
            "metadata": {"interested_property_ids": ["prop-123"]},
        }

        mock_dependencies["doc_gen"].generate_pdf.return_value = "/path/to/brochure.pdf"
        mock_dependencies["msg"].send_whatsapp.return_value = True

        # Execute
        journey_manager.send_property_brochure(phone, property_data)

        # Verify
        update_call = mock_dependencies["db"].update_lead.call_args
        interests = update_call[0][1]["metadata"]["interested_property_ids"]

        assert len(interests) == 2
        assert "prop-123" in interests
        assert "prop-456" in interests

    def test_send_property_brochure_no_duplicate_interests(
        self, journey_manager, mock_dependencies
    ):
        """Test that duplicate property interests are not added."""
        # Setup
        phone = "+393331234567"
        property_data = {"id": "prop-123", "title": "Same Property"}

        # Mock existing lead with the same property already in interests
        mock_dependencies["db"].get_lead.return_value = {
            "customer_phone": phone,
            "metadata": {"interested_property_ids": ["prop-123"]},
        }

        mock_dependencies["doc_gen"].generate_pdf.return_value = "/path/to/brochure.pdf"
        mock_dependencies["msg"].send_whatsapp.return_value = True

        # Execute
        journey_manager.send_property_brochure(phone, property_data)

        # Verify update_lead was NOT called (since property already in interests)
        # Looking at the actual implementation, it should still call update_lead
        # but with the same list (no duplicate added)
        if mock_dependencies["db"].update_lead.called:
            update_call = mock_dependencies["db"].update_lead.call_args
            interests = update_call[0][1]["metadata"]["interested_property_ids"]

            assert len(interests) == 1
            assert interests[0] == "prop-123"

    def test_send_property_brochure_handles_missing_metadata(
        self, journey_manager, mock_dependencies
    ):
        """Test that missing metadata is handled gracefully."""
        # Setup
        phone = "+393331234567"
        property_data = {"id": "prop-789", "title": "New Property"}

        # Mock lead with None metadata
        mock_dependencies["db"].get_lead.return_value = {"customer_phone": phone, "metadata": None}

        mock_dependencies["doc_gen"].generate_pdf.return_value = "/path/to/brochure.pdf"
        mock_dependencies["msg"].send_whatsapp.return_value = True

        # Execute
        result = journey_manager.send_property_brochure(phone, property_data)

        # Verify metadata was created
        update_call = mock_dependencies["db"].update_lead.call_args
        assert "metadata" in update_call[0][1]
        assert update_call[0][1]["metadata"]["interested_property_ids"] == ["prop-789"]
        assert result == "/path/to/brochure.pdf"

    def test_send_property_brochure_fails_gracefully_on_pdf_error(
        self, journey_manager, mock_dependencies
    ):
        """Test that PDF generation failure is handled."""
        # Setup
        phone = "+393331234567"
        property_data = {"id": "prop-999", "title": "Test Property"}

        # Mock PDF generation failure
        mock_dependencies["doc_gen"].generate_pdf.return_value = None

        # Execute
        result = journey_manager.send_property_brochure(phone, property_data)

        # Verify no metadata update occurred
        mock_dependencies["db"].update_lead.assert_not_called()
        assert result == ""
