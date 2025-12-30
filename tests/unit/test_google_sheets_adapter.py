"""Unit tests for GoogleSheetsAdapter."""

from unittest.mock import MagicMock, patch

import pytest
from gspread.exceptions import APIError

from infrastructure.adapters.google_sheets_adapter import GoogleSheetsAdapter


@pytest.fixture
def mock_settings():
    """Mock settings with credentials."""
    with patch("infrastructure.adapters.google_sheets_adapter.settings") as mock:
        mock.GOOGLE_SHEETS_CREDENTIALS_JSON = '{"type": "service_account"}'
        mock.GOOGLE_SHEET_ID = "test-sheet-id"
        yield mock


@pytest.fixture
def mock_gspread():
    """Mock gspread client and credentials."""
    with (
        patch("infrastructure.adapters.google_sheets_adapter.gspread") as mock_gspread,
        patch("infrastructure.adapters.google_sheets_adapter.Credentials"),
    ):
        # Setup mock client and sheet
        mock_client = MagicMock()
        mock_sheet = MagicMock()
        mock_spreadsheet = MagicMock()

        mock_gspread.authorize.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.sheet1 = mock_sheet

        yield mock_gspread, mock_client, mock_sheet


def test_initialization_connects_if_creds_present(mock_settings, mock_gspread):
    """Test that adapter connects on init if credentials are available."""
    adapter = GoogleSheetsAdapter()

    assert adapter.is_connected is True
    assert adapter.sheet is not None
    mock_gspread[0].authorize.assert_called_once()
    mock_gspread[1].open_by_key.assert_called_with("test-sheet-id")


def test_initialization_skips_if_no_creds():
    """Test that adapter does not connect if credentials are missing."""
    with patch("infrastructure.adapters.google_sheets_adapter.settings") as mock_sets:
        mock_sets.GOOGLE_SHEETS_CREDENTIALS_JSON = None
        mock_sets.GOOGLE_SHEET_ID = None

        adapter = GoogleSheetsAdapter()
        assert adapter.is_connected is False


def test_sync_lead_updates_existing(mock_settings, mock_gspread):
    """Test syncing a lead that already exists in the sheet."""
    _, _, mock_sheet = mock_gspread
    adapter = GoogleSheetsAdapter()

    # Mock finding existing row
    mock_cell = MagicMock()
    mock_cell.row = 5
    mock_sheet.find.return_value = mock_cell

    lead_data = {
        "phone": "+393331234567",
        "name": "Mario Ross",
        "status": "active",
        "intent": "purchase",
        "budget": 500000,
        "zones": ["Milano"],
        "message_count": 10,
    }

    success = adapter.sync_lead(lead_data)

    assert success is True
    mock_sheet.find.assert_called_with("+393331234567", in_column=1)
    mock_sheet.update.assert_called_once()

    # Verify update call arguments
    call_args = mock_sheet.update.call_args
    # call_args[1] is kwargs, we expect range_name="A5:I5"
    assert call_args.kwargs["range_name"] == "A5:I5"


def test_sync_lead_appends_new(mock_settings, mock_gspread):
    """Test syncing a new lead."""
    _, _, mock_sheet = mock_gspread
    adapter = GoogleSheetsAdapter()

    # Mock not finding row
    mock_sheet.find.return_value = None

    lead_data = {
        "phone": "+393331234567",
        # other fields...
    }

    success = adapter.sync_lead(lead_data)

    assert success is True
    mock_sheet.append_row.assert_called_once()


def test_sync_lead_handles_api_error(mock_settings, mock_gspread):
    """Test API error handling."""
    _, _, mock_sheet = mock_gspread
    adapter = GoogleSheetsAdapter()

    # Mock Response object expected by APIError
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": {"code": 500, "message": "API Error"}}
    mock_response.text = '{"error": ...}'

    mock_sheet.find.side_effect = APIError(mock_response)

    lead_data = {"phone": "+39123"}
    success = adapter.sync_lead(lead_data)

    assert success is False
