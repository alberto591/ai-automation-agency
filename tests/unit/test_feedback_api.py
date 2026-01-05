"""
Unit tests for Feedback API.
"""

from unittest.mock import Mock, patch

import pytest

from presentation.api.feedback import FeedbackRequest, submit_feedback


class TestFeedbackAPI:
    def test_feedback_request_validation(self):
        """Test Pydantic validation for FeedbackRequest."""
        # Valid request
        req = FeedbackRequest(
            overall_rating=5,
            speed_rating=4,
            accuracy_rating=5,
            appraisal_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert req.overall_rating == 5

        # Invalid rating (< 1)
        with pytest.raises(ValueError):
            FeedbackRequest(overall_rating=0, speed_rating=5, accuracy_rating=5)

        # Invalid rating (> 5)
        with pytest.raises(ValueError):
            FeedbackRequest(overall_rating=6, speed_rating=5, accuracy_rating=5)

    @patch("presentation.api.feedback.SupabaseAdapter")
    def test_submit_feedback_success(self, mock_adapter_class):
        """Should successfully submit feedback."""
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        mock_table = Mock()
        mock_adapter.client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test-fb-id"}])

        req = FeedbackRequest(
            overall_rating=5,
            speed_rating=5,
            accuracy_rating=5,
            appraisal_id="550e8400-e29b-41d4-a716-446655440000",
            feedback_text="Excellent",
        )

        import asyncio

        response = asyncio.run(submit_feedback(req))

        assert response["success"] is True
        assert response["feedback_id"] == "test-fb-id"

        # Verify appraisal_id was included in insert
        insert_args = mock_table.insert.call_args[0][0]
        assert insert_args["appraisal_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert insert_args["overall_rating"] == 5

    @patch("presentation.api.feedback.SupabaseAdapter")
    def test_submit_feedback_resilience(self, mock_adapter_class):
        """Should fall back if appraisal_id column is missing in DB."""
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        mock_table = Mock()
        mock_adapter.client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table

        # First call fails with missing column error
        mock_table.execute.side_effect = [
            Exception("PGRST204: Could not find the 'appraisal_id' column"),
            Mock(data=[{"id": "fallback-id"}]),  # Second call succeeds
        ]

        req = FeedbackRequest(
            overall_rating=5,
            speed_rating=5,
            accuracy_rating=5,
            appraisal_id="550e8400-e29b-41d4-a716-446655440000",
        )

        import asyncio

        response = asyncio.run(submit_feedback(req))

        assert response["success"] is True
        assert response["feedback_id"] == "fallback-id"

        # Verify second insert removed appraisal_id
        second_insert_args = mock_table.insert.call_args_list[1][0][0]
        assert "appraisal_id" not in second_insert_args
