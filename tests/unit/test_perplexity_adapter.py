from unittest.mock import MagicMock, patch

import pytest

from domain.errors import ExternalServiceError
from infrastructure.adapters.perplexity_adapter import PerplexityAdapter


def test_search_success():
    """Test successful Perplexity API search."""
    adapter = PerplexityAdapter()

    with patch.object(adapter.client.chat.completions, "create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Research findings here"
        mock_create.return_value = mock_response

        result = adapter.search("Test query")

        assert result == "Research findings here"
        mock_create.assert_called_once()


def test_search_with_context():
    """Test Perplexity search with context."""
    adapter = PerplexityAdapter()

    with patch.object(adapter.client.chat.completions, "create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Contextual research"
        mock_create.return_value = mock_response

        result = adapter.search("Query", context="Background info")

        assert "Contextual research" in result
        # Verify context was included in messages
        call_args = mock_create.call_args
        messages = call_args.args[0] if call_args.args else call_args.kwargs["messages"]
        assert len(messages) == 2  # System + user
        assert messages[0]["role"] == "system"


def test_search_api_failure():
    """Test handling of Perplexity API failures."""
    adapter = PerplexityAdapter()

    with patch.object(adapter.client.chat.completions, "create") as mock_create:
        mock_create.side_effect = Exception("API Error")

        with pytest.raises(ExternalServiceError):
            adapter.search("Test query")
