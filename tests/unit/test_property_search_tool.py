from unittest.mock import MagicMock

import pytest

from domain.ports import DatabasePort
from infrastructure.tools.property_search import PropertySearchInput, PropertySearchTool


class MockDatabasePort(DatabasePort):
    """Mock that passes isinstance(x, DatabasePort) checks."""

    pass


# Allow instantiation of ABC by clearing abstract methods
MockDatabasePort.__abstractmethods__ = set()


@pytest.fixture
def mock_db():
    # Use a concrete class that satisfies isinstance(db, DatabasePort)
    class ConcreteMockDB(DatabasePort):
        pass

    ConcreteMockDB.__abstractmethods__ = set()

    mock = ConcreteMockDB()
    # Manually attach MagicMock to the method we are testing
    mock.get_properties = MagicMock()

    return mock


def test_property_search_tool_initialization(mock_db):
    tool = PropertySearchTool(db=mock_db)
    assert tool.name == "property_search"
    assert tool.args_schema == PropertySearchInput


def test_property_search_found_results(mock_db):
    mock_db.get_properties.return_value = [
        {"title": "Luxury Villa", "price": 500000},
        {"title": "City Apartment", "price": 250000},
    ]

    tool = PropertySearchTool(db=mock_db)
    result = tool._run(query="villa", budget=1000000)

    # Check that database port was called correctly
    mock_db.get_properties.assert_called_once()
    # call_kwargs checking
    call_kwargs = mock_db.get_properties.call_args[1]
    assert call_kwargs["query"] == "villa"

    # Check output formatting
    assert "Found the following properties" in result
    assert "Luxury Villa: €500,000" in result
    assert "City Apartment: €250,000" in result


def test_property_search_no_results(mock_db):
    mock_db.get_properties.return_value = []

    tool = PropertySearchTool(db=mock_db)
    result = tool._run(query="castle", budget=500000)

    mock_db.get_properties.assert_called_once()
    assert "No specific properties found matching the criteria" in result


def test_property_search_error_handling(mock_db):
    mock_db.get_properties.side_effect = Exception("Database connection failed")

    tool = PropertySearchTool(db=mock_db)
    result = tool._run(query="error test")

    assert "Error searching properties" in result
    assert "Database connection failed" in result
