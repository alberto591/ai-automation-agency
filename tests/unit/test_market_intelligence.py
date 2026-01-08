import json
from unittest.mock import MagicMock, Mock

import pytest

from application.services.market_intelligence import MarketIntelligenceService


class TestMarketIntelligenceService:
    @pytest.fixture
    def mock_dependencies(self):
        """Setup mock dependencies."""
        return {"db": Mock(), "ai": Mock(), "cache": Mock()}

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create MarketIntelligenceService instance."""
        return MarketIntelligenceService(**mock_dependencies)

    def test_get_market_analysis_uses_cache_on_hit(self, service, mock_dependencies):
        """Test that cached market analysis is returned when available."""
        # Setup
        city = "Milano"
        zone = "Centro"
        cache_key = f"market_analysis:{city}:{zone}"

        cached_data = {
            "sentiment": "POSITIVO",
            "summary": "Cached market summary",
            "investor_tip": "Cached tip",
            "stats": {"avg_price": 5000, "count": 10},
        }

        mock_dependencies["cache"].get.return_value = json.dumps(cached_data)

        # Execute
        result = service.get_market_analysis(city=city, zone=zone)

        # Verify
        mock_dependencies["cache"].get.assert_called_once_with(cache_key)
        assert result == cached_data

        # Verify database and AI were NOT called
        mock_dependencies["db"].client.table.assert_not_called()
        mock_dependencies["ai"].generate_response.assert_not_called()

    def test_get_market_analysis_fetches_and_caches_on_miss(self, service, mock_dependencies):
        """Test that market analysis is generated and cached when cache misses."""
        # Setup
        city = "Roma"
        zone = None
        cache_key = f"market_analysis:{city}:all"

        # Cache miss
        mock_dependencies["cache"].get.return_value = None

        # Mock database response
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_result = MagicMock()

        mock_dependencies["db"].client.table.return_value = mock_table
        mock_table.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_result

        mock_result.data = [
            {"price_per_mq": 4000, "zone": "Centro"},
            {"price_per_mq": 3500, "zone": "Prati"},
            {"price_per_mq": 4500, "zone": "Trastevere"},
        ]

        # Mock AI response
        ai_response = json.dumps(
            {
                "sentiment": "POSITIVO",
                "summary": "Il mercato è in crescita",
                "investor_tip": "Comprare subito",
            }
        )
        mock_dependencies["ai"].generate_response.return_value = ai_response

        # Execute
        result = service.get_market_analysis(city=city, zone=zone)

        # Verify cache was checked
        mock_dependencies["cache"].get.assert_called_once_with(cache_key)

        # Verify database was queried
        mock_dependencies["db"].client.table.assert_called_once_with("market_data")

        # Verify AI was called
        mock_dependencies["ai"].generate_response.assert_called_once()

        # Verify result structure
        assert result["sentiment"] == "POSITIVO"
        assert "stats" in result
        assert result["stats"]["avg_price"] == 4000.0
        assert result["stats"]["count"] == 3

        # Verify cache was updated
        mock_dependencies["cache"].set.assert_called_once()
        set_call = mock_dependencies["cache"].set.call_args
        assert set_call[0][0] == cache_key
        assert set_call[1]["ttl"] == 86400  # 24 hours

    def test_get_market_analysis_handles_no_data(self, service, mock_dependencies):
        """Test graceful handling when no market data is available."""
        # Setup
        mock_dependencies["cache"].get.return_value = None

        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_result = MagicMock()

        mock_dependencies["db"].client.table.return_value = mock_table
        mock_table.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_result
        mock_result.data = []  # No data

        # Execute
        result = service.get_market_analysis(city="Unknown City")

        # Verify fallback response
        assert result["sentiment"] == "NEUTRAL"
        assert "Dati insufficienti" in result["summary"]

    def test_get_market_analysis_works_without_cache(self, service, mock_dependencies):
        """Test that service works when cache is None (fallback mode)."""
        # Create service without cache
        service_no_cache = MarketIntelligenceService(
            db=mock_dependencies["db"], ai=mock_dependencies["ai"], cache=None
        )

        # Mock database
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_result = MagicMock()

        mock_dependencies["db"].client.table.return_value = mock_table
        mock_table.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_result
        mock_result.data = [{"price_per_mq": 5000}]

        # Mock AI
        ai_response = json.dumps(
            {"sentiment": "NEUTRALE", "summary": "Test", "investor_tip": "Test tip"}
        )
        mock_dependencies["ai"].generate_response.return_value = ai_response

        # Execute (should not throw)
        result = service_no_cache.get_market_analysis()

        # Verify it worked
        assert "sentiment" in result

    def test_get_market_analysis_handles_invalid_json_from_cache(self, service, mock_dependencies):
        """Test that invalid JSON in cache is handled gracefully."""
        # Setup
        mock_dependencies["cache"].get.return_value = "invalid json{{"

        # Mock database and AI for fallback
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_result = MagicMock()

        mock_dependencies["db"].client.table.return_value = mock_table
        mock_table.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_result
        mock_result.data = [{"price_per_mq": 3000}]

        ai_response = json.dumps(
            {
                "sentiment": "POSITIVO",
                "summary": "Recovered from cache error",
                "investor_tip": "Good to go",
            }
        )
        mock_dependencies["ai"].generate_response.return_value = ai_response

        # Execute
        result = service.get_market_analysis()

        # Verify fallback to database
        mock_dependencies["db"].client.table.assert_called_once()
        assert result["sentiment"] == "POSITIVO"
