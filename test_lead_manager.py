import os
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from lead_manager import get_property_details, save_lead_to_dashboard, send_ai_whatsapp, handle_real_estate_lead

# Load environment variables
load_dotenv()

class TestLeadManager(unittest.TestCase):
    @patch('lead_manager.supabase')
    def test_get_property_details(self, mock_supabase):
        """Test the get_property_details function."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "title": "Attico a Milano", "price": 500000, "city": "Milano"}]
        mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_response
        
        # Call the function
        result = get_property_details("Attico")
        
        # Assert the result
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Attico a Milano")
        self.assertEqual(result['price'], 500000)
        self.assertEqual(result['city'], "Milano")

    @patch('lead_manager.supabase')
    def test_get_property_details_not_found(self, mock_supabase):
        """Test the get_property_details function when no property is found."""
        # Mock the Supabase response with no data
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = mock_response
        
        # Call the function
        result = get_property_details("Non Esistente")
        
        # Assert the result
        self.assertIsNone(result)

    @patch('lead_manager.supabase')
    def test_save_lead_to_dashboard(self, mock_supabase):
        """Test the save_lead_to_dashboard function."""
        # Mock the Supabase insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value = None
        
        # Call the function
        save_lead_to_dashboard("Marco", "+34625852546", "Test message", "Test notes")
        
        # Assert the Supabase insert was called
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @patch('lead_manager.mistral')
    @patch('lead_manager.twilio_client')
    def test_send_ai_whatsapp(self, mock_twilio, mock_mistral):
        """Test the send_ai_whatsapp function."""
        # Mock the Mistral response
        mock_mistral_response = MagicMock()
        mock_mistral_response.choices = [MagicMock(message=MagicMock(content="Test AI message"))]
        mock_mistral.chat.complete.return_value = mock_mistral_response
        
        # Mock the Twilio response
        mock_twilio_response = MagicMock()
        mock_twilio_response.sid = "SM123"
        mock_twilio.messages.create.return_value = mock_twilio_response
        
        # Call the function
        result = send_ai_whatsapp("+34625852546", "Marco", "Attico a Milano")
        
        # Assert the result
        self.assertEqual(result, "SM123")

    @patch('lead_manager.get_property_details')
    @patch('lead_manager.mistral')
    @patch('lead_manager.twilio_client')
    @patch('lead_manager.save_lead_to_dashboard')
    def test_handle_real_estate_lead(self, mock_save, mock_twilio, mock_mistral, mock_get_property):
        """Test the handle_real_estate_lead function."""
        # Mock the property details
        mock_get_property.return_value = {"title": "Attico a Milano", "price": 500000, "city": "Milano"}
        
        # Mock the Mistral response
        mock_mistral_response = MagicMock()
        mock_mistral_response.choices = [MagicMock(message=MagicMock(content="Test AI message"))]
        mock_mistral.chat.complete.return_value = mock_mistral_response
        
        # Mock the Twilio response
        mock_twilio_response = MagicMock()
        mock_twilio.messages.create.return_value = mock_twilio_response
        
        # Call the function
        result = handle_real_estate_lead("+34625852546", "Marco", "Attico")
        
        # Assert the result
        self.assertEqual(result, "Messaggio inviato con dati reali!")
        
        # Assert the save function was called
        mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()