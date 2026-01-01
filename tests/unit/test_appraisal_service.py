"""
Simplified unit tests for AppraisalService integration.

Tests core functionality and investment metrics integration.
"""

from unittest.mock import Mock

import pytest

from application.services.appraisal import AppraisalService
from domain.appraisal import AppraisalRequest


class TestAppraisalServiceIntegration:
    """Core integration tests for AppraisalService."""

    @pytest.fixture
    def service(self):
        """AppraisalService with mocked research."""
        mock_research = Mock()
        mock_research.search = Mock(
            return_value="""
            Apartment in Centro | €450,000 | 95 sqm
            Renovated Flat | €480,000 |100 sqm
            Luxury Apt | €520,000 | 105 sqm
            """
        )
        return AppraisalService(research=mock_research)

    def test_full_appraisal_with_investment_metrics(self, service):
        """Should generate full appraisal with investment metrics."""
        request = AppraisalRequest(
            city="Florence",
            zone="Florence-Centro",
            surface_sqm=100,
            condition="good",
        )

        result = service.estimate_value(request)

        # Core appraisal
        assert result.estimated_value > 0
        assert result.confidence_level > 0
        assert result.reliability_stars >= 1

        # Investment metrics present
        assert result.investment_metrics is not None
        assert "cap_rate" in result.investment_metrics
        assert "roi" in result.investment_metrics

    def test_confidence_and_stars_correlation(self, service):
        """Confidence level and stars should correlate."""
        # Test with 3 comparables
        request = AppraisalRequest(city="Florence", zone="Florence-Centro", surface_sqm=100)

        result = service.estimate_value(request)

        # 3 comparables should give 75% confidence, 4 stars
        assert result.confidence_level == 75
        assert result.reliability_stars == 4

    def test_fallback_when_no_data(self, service):
        """Should return safe fallback when research fails."""
        service.research.search = Mock(return_value="")

        request = AppraisalRequest(city="Florence", zone="Unknown", surface_sqm=100)

        result = service.estimate_value(request)

        assert result.estimated_value == 0.0
        assert result.confidence_level == 0
        assert result.reliability_stars == 1
        assert result.investment_metrics is None
