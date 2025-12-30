from unittest.mock import MagicMock, patch

from infrastructure.adapters.validation_adapter import PostgresValidationAdapter


class TestPostgresValidationAdapter:
    @patch("infrastructure.adapters.supabase_adapter.create_client")
    @patch("config.settings.settings")
    def test_log_validation(self, mock_settings, mock_create_client):
        """Test logging validation to DB."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_settings.SUPABASE_URL = "http://test"
        mock_settings.SUPABASE_KEY = "test"

        adapter = PostgresValidationAdapter()

        # Test Data
        predicted = 500000
        actual = 450000
        metadata = {"zone": "centro-milano", "city": "Milano", "price_type": "sale"}

        # Execute
        adapter.log_validation(predicted, actual, metadata, uncertainty_score=0.15)

        # Verify
        mock_client.table.assert_called_with("appraisal_validations")
        mock_client.table().insert.assert_called_once()

        call_args = mock_client.table().insert.call_args[0][0]
        assert call_args["predicted_value_eur"] == 500000
        assert call_args["actual_sale_price_eur"] == 450000
        assert call_args["error_pct"] == round(50000 / 450000, 4)  # ~0.1111
        assert call_args["zone"] == "centro-milano"
        assert call_args["alert_triggered"] is False

    @patch("infrastructure.adapters.supabase_adapter.create_client")
    @patch("config.settings.settings")
    def test_log_validation_alert(self, mock_settings, mock_create_client):
        """Test logging triggers alert on high drift."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        adapter = PostgresValidationAdapter()

        # High error (50%)
        predicted = 600000
        actual = 400000
        metadata = {"zone": "centro-milano"}

        adapter.log_validation(predicted, actual, metadata)

        call_args = mock_client.table().insert.call_args[0][0]
        assert call_args["alert_triggered"] is True
        assert call_args["error_pct"] == 0.5

    @patch("infrastructure.adapters.supabase_adapter.create_client")
    @patch("config.settings.settings")
    def test_detect_drift(self, mock_settings, mock_create_client):
        """Test drift detection via recent history."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        adapter = PostgresValidationAdapter()

        # Mock Response: 50 rows with average error > 15%
        # Let's say 0.20 consistently
        mock_data = [{"error_pct": 0.20}] * 50
        mock_client.table().select().eq().order().limit().execute.return_value.data = mock_data

        is_drifting = adapter.detect_drift("centro-milano", threshold=0.15)

        assert is_drifting is True

        # Verify Query
        mock_client.table.assert_called_with("appraisal_validations")
        mock_client.table().select.assert_called_with("error_pct")
        mock_client.table().select().eq.assert_called_with("zone", "centro-milano")
