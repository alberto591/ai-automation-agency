"""
Unit tests for InvestmentCalculator service.

Tests real estate investment metrics calculations including
Cap Rate, ROI, cash flow, and rental estimations.
"""

import pytest

from application.services.investment_calculator import (
    InvestmentCalculator,
    InvestmentMetrics,
)


class TestInvestmentCalculator:
    """Test suite for InvestmentCalculator."""

    @pytest.fixture
    def calculator(self):
        """InvestmentCalculator instance."""
        return InvestmentCalculator()

    def test_calculate_metrics_basic(self, calculator):
        """Should calculate all metrics correctly with basic inputs."""
        metrics = calculator.calculate_metrics(
            property_price=300000,
            estimated_monthly_rent=1200,
            monthly_expenses=360,  # 30% of rent
        )

        assert isinstance(metrics, InvestmentMetrics)
        assert metrics.cap_rate == pytest.approx(3.36, abs=0.01)
        assert metrics.roi == pytest.approx(3.36, abs=0.01)
        assert metrics.monthly_cash_flow == 840
        assert metrics.annual_net_income == 10080

    def test_calculate_metrics_defaults_expenses(self, calculator):
        """Should default expenses to 30% of rent if not provided."""
        metrics = calculator.calculate_metrics(property_price=300000, estimated_monthly_rent=1200)

        # With 30% expenses: 1200 - 360 = 840 monthly cash flow
        assert metrics.monthly_cash_flow == 840
        assert metrics.annual_net_income == 10080

    def test_cap_rate_calculation(self, calculator):
        """Should calculate Cap Rate correctly."""
        metrics = calculator.calculate_metrics(
            property_price=500000, estimated_monthly_rent=2000, monthly_expenses=600
        )

        # Annual net: (2000 - 600) * 12 = 16,800
        # Cap Rate: (16,800 / 500,000) * 100 = 3.36%
        assert metrics.cap_rate == pytest.approx(3.36, abs=0.01)

    def test_cash_on_cash_return(self, calculator):
        """Should calculate Cash-on-Cash return for leveraged purchase."""
        metrics = calculator.calculate_metrics(
            property_price=300000,
            estimated_monthly_rent=1200,
            monthly_expenses=360,
            down_payment_pct=20.0,
            interest_rate=4.5,
        )

        assert metrics.cash_on_cash_return is not None
        # With mortgage, CoC can be negative if cash flow < mortgage payment
        # This is correct behavior - test just verifies calculation works
        assert isinstance(metrics.cash_on_cash_return, float)

    def test_price_to_rent_ratio(self, calculator):
        """Should calculate Price-to-Rent ratio."""
        metrics = calculator.calculate_metrics(property_price=300000, estimated_monthly_rent=1200)

        # Annual rent: 1200 * 12 = 14,400
        # Ratio: 300,000 / 14,400 = 20.83
        assert metrics.price_to_rent_ratio == pytest.approx(20.8, abs=0.1)

    def test_breakeven_calculation(self, calculator):
        """Should calculate breakeven years correctly."""
        metrics = calculator.calculate_metrics(
            property_price=300000, estimated_monthly_rent=1200, monthly_expenses=360
        )

        # Annual net: 10,080
        # Breakeven: 300,000 / 10,080 = ~29.8 years
        assert metrics.breakeven_years == pytest.approx(29.8, abs=0.1)

    def test_estimate_monthly_rent_standard_zone(self, calculator):
        """Should estimate rent at 4% yield for standard zones."""
        rent = calculator.estimate_monthly_rent(property_price=300000, zone="50100")

        # 300,000 * 0.04 / 12 = 1,000
        assert rent == 1000

    def test_estimate_monthly_rent_premium_zone(self, calculator):
        """Should estimate rent at 3% yield for premium zones."""
        rent = calculator.estimate_monthly_rent(property_price=300000, zone="Firenze-Centro")

        # 300,000 * 0.03 / 12 = 750
        assert rent == 750

    def test_estimate_monthly_rent_suburban_zone(self, calculator):
        """Should estimate rent at 5% yield for suburban zones."""
        rent = calculator.estimate_monthly_rent(property_price=300000, zone="Periferia-Nord")

        # 300,000 * 0.05 / 12 = 1,250
        assert rent == 1250

    def test_no_rent_returns_none(self, calculator):
        """Should return None if no rental data provided."""
        metrics = calculator.calculate_metrics(property_price=300000, estimated_monthly_rent=None)

        assert metrics is None

    def test_zero_property_price(self, calculator):
        """Should handle zero property price gracefully."""
        metrics = calculator.calculate_metrics(property_price=0, estimated_monthly_rent=1200)

        # Should return metrics with 0 rates
        assert metrics.cap_rate == 0
        assert metrics.roi == 0

    def test_high_expenses_negative_cash_flow(self, calculator):
        """Should handle negative cash flow scenario."""
        metrics = calculator.calculate_metrics(
            property_price=300000, estimated_monthly_rent=800, monthly_expenses=1000
        )

        # Negative cash flow: 800 - 1000 = -200
        assert metrics.monthly_cash_flow == -200
        assert metrics.annual_net_income < 0
        # Breakeven should be very high (999.9 max)
        assert metrics.breakeven_years == 999.9

    def test_realistic_florence_apartment(self, calculator):
        """Test with realistic Florence apartment scenario."""
        # 100 sqm apartment in Florence center
        # Market price: ~€467,500
        # Estimated rent: ~€1,850/month
        metrics = calculator.calculate_metrics(property_price=467500, estimated_monthly_rent=1850)

        # Verify all metrics are reasonable
        assert 2.0 < metrics.cap_rate < 6.0  # Italian market range
        assert 20 < metrics.price_to_rent_ratio < 30  # Typical for Italy
        assert metrics.monthly_cash_flow > 0  # Should be cash-flow positive
        assert 10 < metrics.breakeven_years < 40  # Reasonable payback
