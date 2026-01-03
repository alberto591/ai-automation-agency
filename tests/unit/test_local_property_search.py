"""
Unit tests for LocalPropertySearchService.
"""

from unittest.mock import Mock

import pytest

from application.services.local_property_search import LocalPropertySearchService


class TestLocalPropertySearchService:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def search_service(self, mock_db):
        return LocalPropertySearchService(mock_db)

    def test_city_normalization_florence(self, search_service, mock_db):
        """Should normalize Florence to Firenze for search."""
        # Setup mock chain
        mock_query = Mock()
        mock_db.table.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.ilike.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.gt.return_value = mock_query
        mock_query.limit.return_value = mock_query

        mock_result = Mock()
        mock_result.data = [
            {"title": "Test 1", "price": 500000, "sqm": 100, "description": "Firenze Centro"},
            {"title": "Test 2", "price": 600000, "sqm": 120, "description": "Firenze Centro"},
            {"title": "Test 3", "price": 400000, "sqm": 80, "description": "Firenze Centro"},
        ]
        mock_query.execute.return_value = mock_result

        results = search_service.search_local_comparables(
            city="Florence", zone="Centro", property_type="apartment", surface_sqm=100
        )

        assert len(results) == 3
        # Verify ilike was called with Firenze
        ilike_calls = [call.args for call in mock_query.ilike.call_args_list]
        assert any("Firenze" in arg[1] for arg in ilike_calls)

    def test_sanity_check_filtering(self, search_service, mock_db):
        """Should filter out properties with unrealistic price/sqm."""
        mock_query = Mock()
        mock_db.table.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.ilike.return_value = mock_query
        mock_query.gte.return_value = mock_query
        mock_query.lte.return_value = mock_query
        mock_query.gt.return_value = mock_query
        mock_query.limit.return_value = mock_query

        mock_result = Mock()
        mock_result.data = [
            {"title": "Valid", "price": 500000, "sqm": 100, "description": "Firenze"},  # 5000/sqm
            {"title": "Too Cheap", "price": 10000, "sqm": 100, "description": "Firenze"},  # 100/sqm
            {
                "title": "Too Expensive",
                "price": 5000000,
                "sqm": 50,
                "description": "Firenze",
            },  # 100000/sqm
        ]
        mock_query.execute.return_value = mock_result

        results = search_service.search_local_comparables(
            city="Florence", zone="Centro", property_type="apartment", surface_sqm=100
        )

        assert len(results) == 1
        assert results[0].title == "Valid"

    def test_empty_results_on_error(self, search_service, mock_db):
        """Should return empty list and not crash on DB error."""
        mock_db.table.side_effect = Exception("DB Connection Failed")

        results = search_service.search_local_comparables(
            city="Florence", zone="Centro", property_type="apartment", surface_sqm=100
        )

        assert results == []
