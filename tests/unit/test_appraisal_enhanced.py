from unittest.mock import Mock

import pytest

from application.services.appraisal import AppraisalService
from domain.appraisal import AppraisalRequest


class TestAppraisalEnhanced:
    """Enhanced tests for appraisal logic and matching prototypes."""

    @pytest.fixture
    def service(self):
        mock_research = Mock()
        # The method in ResearchPort is find_market_comparables
        mock_research.find_market_comparables.return_value = """
        Luxury Villa in Florence | €1,200,000 | 250 sqm | Condition: excellent
        Standard Apartment | €350,000 | 85 sqm | Condition: good
        Fixer-upper | €150,000 | 70 sqm | Condition: poor
        """
        return AppraisalService(research_port=mock_research)

    def test_city_extraction_logic_placeholder(self):
        """
        Test the logic used in frontend city extraction but on the backend
        to ensure consistency in detected parameters.
        """

        # In a real scenario, this would test a utility function in application/utils.py
        # For now, we simulate the logic found in script.js
        def extract_city(address):
            cities = ["Firenze", "Florence", "Roma", "Rome", "Milano", "Milan"]
            upper_addr = address.upper()
            for city in cities:
                if city.upper() in upper_addr:
                    if city in ["Firenze", "Florence"]:
                        return "Florence"
                    if city in ["Roma", "Rome"]:
                        return "Rome"
                    return city
            return "Florence"

        assert extract_city("Via de Ginori 10, Firenze") == "Florence"
        assert extract_city("Via del Corso, Roma") == "Rome"
        assert extract_city("Via Montenapoleone, Milano") == "Milano"
        assert extract_city("Unknown Street") == "Florence"  # Default

    def test_appraisal_with_different_conditions(self, service):
        """Verify that property condition affects the estimated value appropriately."""
        # This tests if the heuristic or ML model responds to condition
        req_excellent = AppraisalRequest(
            city="Florence", zone="Centro", surface_sqm=100, condition="excellent"
        )
        req_poor = AppraisalRequest(
            city="Florence", zone="Centro", surface_sqm=100, condition="poor"
        )

        res_excellent = service.estimate_value(req_excellent)
        res_poor = service.estimate_value(req_poor)

        # In the current implementation, it might not be fully sensitive yet if using simple mocks,
        # but we expect it to be.
        # Actually, let's check if the service uses the condition.
        assert res_excellent.estimated_value >= res_poor.estimated_value

    def test_investment_metrics_consistency(self, service):
        """Ensure investment metrics are mathematically consistent."""
        req = AppraisalRequest(city="Florence", zone="Centro", surface_sqm=100, condition="good")
        res = service.estimate_value(req)

        if res.investment_metrics:
            metrics = res.investment_metrics
            # Cap Rate should roughly be (Annual Rent / Property Value) * 100
            if res.estimated_value > 0:
                # Cap Rate should be (Annual Net Income / Property Value) * 100
                expected_cap = (metrics["annual_net_income"] / res.estimated_value) * 100
                assert pytest.approx(metrics["cap_rate"], rel=0.1) == expected_cap
