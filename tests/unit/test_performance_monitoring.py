"""
Unit tests for Performance Monitoring.
"""

from unittest.mock import Mock

import pytest

from infrastructure.monitoring.performance_logger import PerformanceMetricLogger, track_performance


class TestPerformanceMonitoring:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def logger(self, mock_db):
        return PerformanceMetricLogger(mock_db)

    def test_log_appraisal_performance_success(self, logger, mock_db):
        """Should call RPC with correct parameters."""
        mock_db.rpc.return_value = Mock(execute=Mock(return_value=Mock(data="test-uuid")))

        result_id = logger.log_appraisal_performance(
            city="Milan",
            zone="Centro",
            response_time_ms=500,
            used_local_search=True,
            used_perplexity=False,
            comparables_found=5,
            confidence_level=90,
            reliability_stars=5,
            estimated_value=1000000.0,
        )

        assert result_id == "test-uuid"

        # Verify RPC call
        rpc_args = mock_db.rpc.call_args[0][1]
        assert rpc_args["p_city"] == "Milan"
        assert rpc_args["p_used_local_search"] is True

    def test_track_performance_decorator(self, mock_db):
        """Should track performance when decorator is used on a class method."""
        mock_db.rpc.return_value = Mock(execute=Mock(return_value=Mock(data="dec-uuid")))

        class MockService:
            @track_performance(mock_db)
            def mock_service_call(self, request):
                result = Mock()
                result.confidence_level = 80
                result.reliability_stars = 4
                result.estimated_value = 500000
                result.comparables = [Mock(), Mock()]
                result._used_local_search = True
                result._used_perplexity = False
                return result

        service = MockService()
        request = Mock()
        request.city = "Rome"
        request.zone = "Trastevere"
        request.property_type = "apartment"
        request.surface_sqm = 80
        request.phone = "+3912345"

        service.mock_service_call(request)

        assert mock_db.rpc.called
        rpc_args = mock_db.rpc.call_args[0][1]
        assert rpc_args["p_city"] == "Rome"
        assert rpc_args["p_user_phone"] == "+3912345"
