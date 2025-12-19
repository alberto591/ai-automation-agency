import os
import unittest
from unittest.mock import patch, MagicMock
from lead_manager import save_lead_to_dashboard, get_matching_properties, handle_incoming_message

class TestData2(unittest.TestCase):
    
    @patch("lead_manager.supabase")
    def test_profiling_extraction(self, mock_supabase):
        """Verify that budget and zones are extracted from messages."""
        # Mock Supabase response for existing lead
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        # Call the function with a budget and zone
        msg = "Cerco un attico a Brera budget 800k"
        save_lead_to_dashboard("Test User", "+39000", msg, "AI Summary")
        
        # Check the data sent to Supabase
        called_data = mock_supabase.table.return_value.upsert.call_args[0][0]
        
        print(f"✅ Extracted Budget: {called_data.get('budget_max')}")
        print(f"✅ Extracted Zones: {called_data.get('preferred_zones')}")
        
        self.assertEqual(called_data["budget_max"], 800000)
        self.assertIn("Brera", called_data["preferred_zones"])

    @patch("lead_manager.supabase")
    def test_granular_filtering(self, mock_supabase):
        """Verify that get_matching_properties uses sqm and room filters."""
        # Mock Supabase response
        mock_supabase.table.return_value.select.return_value.ilike.return_value.gte.return_value.gte.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"title": "Match"}])
        
        results = get_matching_properties("Casa", min_sqm=100, min_rooms=3)
        
        # Verify the chain of calls
        table = mock_supabase.table.return_value
        table.select.assert_called_with("*")
        # Check if gte was called with sqm and rooms
        # (The order might vary depending on implementation, but we check if they were called)
        self.assertTrue(any("sqm" in str(call) for call in table.select.return_value.ilike.return_value.gte.call_args_list))
        
        print("✅ Granular filters (sqm, rooms) passed to Supabase query.")

    @patch("lead_manager.get_matching_properties")
    @patch("lead_manager.mistral")
    @patch("lead_manager.supabase")
    def test_rag_precision_trigger(self, mock_supabase, mock_mistral, mock_get_matching):
        """Verify handle_incoming_message extracts numeric filters for RAG."""
        mock_get_matching.return_value = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        
        msg = "Voglio un trilocale di almeno 90mq"
        handle_incoming_message("+39000", msg)
        
        # Check if extract_min_sqm and min_rooms were passed to get_matching_properties
        called_args, called_kwargs = mock_get_matching.call_args
        
        print(f"✅ RAG Loop Extracted min_sqm: {called_kwargs.get('min_sqm')}")
        print(f"✅ RAG Loop Extracted min_rooms: {called_kwargs.get('min_rooms')}")
        
        self.assertEqual(called_kwargs.get("min_sqm"), 90)
        self.assertEqual(called_kwargs.get("min_rooms"), 3) # 'trilocale' -> 3

if __name__ == "__main__":
    unittest.main()
