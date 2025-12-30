from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from infrastructure.adapters.calcom_adapter import CalComAdapter


@pytest.fixture
def cal_adapter():
    with patch("config.settings.settings") as mock_settings:
        mock_settings.CALCOM_API_KEY = "test_key"
        mock_settings.CALCOM_EVENT_TYPE_ID = "12345"
        mock_settings.CALCOM_BOOKING_LINK = "https://cal.com/test"
        yield CalComAdapter()


def test_get_availability_success(cal_adapter):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": "success",
        "data": {"slots": ["2023-10-27T10:00:00Z", "2023-10-27T10:30:00Z"]},
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        slots = cal_adapter.get_availability("staff_1", "2023-10-27")

        assert len(slots) == 2
        assert "2023-10-27T10:00:00Z" in slots

        # Verify params
        args, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params["eventTypeId"] == "12345"
        assert params["startTime"] == "2023-10-27T00:00:00Z"


def test_get_availability_failure(cal_adapter):
    with patch("requests.get", side_effect=requests.exceptions.RequestException("API Error")):
        slots = cal_adapter.get_availability("staff_1", "2023-10-27")
        assert slots == []


def test_create_event_success(cal_adapter):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success", "data": {"id": 999}}

    start = datetime(2023, 10, 27, 10, 0)
    end = datetime(2023, 10, 27, 10, 30)

    with patch("requests.post", return_value=mock_response) as mock_post:
        link = cal_adapter.create_event("Meeting", start, end, ["test@example.com"])

        # Expect fallback link even on success if API doesn't return a specific booking URL
        # (Based on current implementation which returns settings.CALCOM_BOOKING_LINK)
        assert link == "https://cal.com/test"

        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["eventTypeId"] == "12345"
        assert payload["responses"]["email"] == "test@example.com"
