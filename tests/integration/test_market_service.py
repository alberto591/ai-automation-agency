from unittest.mock import MagicMock, patch

from infrastructure.market_service import MarketDataService


@patch("requests.get")
@patch("config.settings.settings.RAPIDAPI_KEY", None)
def test_market_price_tuscany_fallback(mock_get):
    """Verify fallback to TUSCANY_EXPERT_DATA when API key is missing or fails."""
    # Mock API failure to force fallback
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp

    service = MarketDataService()
    price = service.get_avg_price("Firenze")
    assert price == 4546

    price = service.get_avg_price("Figline e Incisa Valdarno")
    assert price == 2400


@patch("requests.get")
@patch("config.settings.settings.RAPIDAPI_KEY", "test-key")
def test_market_price_api_success(mock_get):
    """Verify calculation from successful API response."""
    # Mock Autocomplete
    mock_ac_resp = MagicMock()
    mock_ac_resp.status_code = 200
    mock_ac_resp.json.return_value = {"locations": [{"locationId": "L123"}]}

    # Mock Properties List
    mock_list_resp = MagicMock()
    mock_list_resp.status_code = 200
    mock_list_resp.json.return_value = {
        "elementList": [
            {"price": 300000, "size": 100},  # 3000
            {"price": 400000, "size": 100},  # 4000
            {"price": 100000, "size": 10, "isAuction": True},  # Skipped
            {"price": 10000, "size": 100},  # 100 (Outlier < 800)
            {"price": 5000000, "size": 100},  # 50000 (Outlier > 20000)
        ]
    }

    mock_get.side_effect = [mock_ac_resp, mock_list_resp]

    service = MarketDataService(api_key="test-key")
    price = service.get_avg_price("Milano", "Navigli")

    # Avg of 3000 and 4000 = 3500
    assert price == 3500


@patch("requests.get")
@patch("config.settings.settings.RAPIDAPI_KEY", "test-key")
def test_market_price_api_failure(mock_get):
    """Verify graceful handling of API errors."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    service = MarketDataService(api_key="test-key")
    price = service.get_avg_price("GenericZone")
    assert price is None
