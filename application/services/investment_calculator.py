"""
Investment Calculator Service for Real Estate Metrics.

Calculates key investment metrics for property appraisals including
Cap Rate, ROI, Price-to-Rent Ratio, and Cash-on-Cash Return.
"""

from dataclasses import dataclass


@dataclass
class InvestmentMetrics:
    """Real estate investment metrics."""

    cap_rate: float  # (Annual Rent / Property Price) * 100
    roi: float  # ((Annual Rent - Expenses) / Investment) * 100
    price_to_rent_ratio: float  # Property Price / Annual Rent
    cash_on_cash_return: float | None  # For leveraged purchases
    monthly_cash_flow: int  # Monthly Rent - Monthly Expenses
    annual_net_income: int  # Annual Rent - Annual Expenses
    breakeven_years: float  # Years to recover investment


class InvestmentCalculator:
    """
    Calculates real estate investment metrics.

    Provides comprehensive financial analysis for property investments
    including rental yields, returns, and cash flow projections.
    """

    def calculate_metrics(
        self,
        property_price: int,
        estimated_monthly_rent: int | None = None,
        monthly_expenses: int | None = None,
        down_payment_pct: float = 20.0,
        interest_rate: float = 4.5,
        loan_term_years: int = 30,
    ) -> InvestmentMetrics | None:
        """
        Calculate comprehensive investment metrics for a property.

        Args:
            property_price: Property purchase price in EUR
            estimated_monthly_rent: Expected monthly rental income in EUR
            monthly_expenses: Monthly expenses (taxes, HOA, maintenance) in EUR
            down_payment_pct: Down payment as percentage (default 20%)
            interest_rate: Annual interest rate as percentage (default 4.5%)
            loan_term_years: Mortgage term in years (default 30)

        Returns:
            InvestmentMetrics object or None if rental data unavailable
        """
        # If no rental data, can't calculate investment metrics
        if not estimated_monthly_rent:
            return None

        # Default expenses to 30% of rent if not provided (conservative estimate)
        if monthly_expenses is None:
            monthly_expenses = int(estimated_monthly_rent * 0.30)

        annual_rent = estimated_monthly_rent * 12
        annual_expenses = monthly_expenses * 12
        annual_net_income = annual_rent - annual_expenses

        # Cap Rate: (Annual Net Income / Property Price) * 100
        cap_rate = (annual_net_income / property_price) * 100 if property_price > 0 else 0

        # ROI: ((Annual Net Income) / Total Investment) * 100
        # For cash purchase, total investment = property price
        roi = (annual_net_income / property_price) * 100 if property_price > 0 else 0

        # Price-to-Rent Ratio: Property Price / Annual Rent
        price_to_rent_ratio = property_price / annual_rent if annual_rent > 0 else 0

        # Cash-on-Cash Return (for leveraged purchase)
        down_payment = property_price * (down_payment_pct / 100)
        loan_amount = property_price - down_payment

        # Monthly mortgage payment (P&I)
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12

        if monthly_rate > 0:
            monthly_mortgage = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                / ((1 + monthly_rate) ** num_payments - 1)
            )
        else:
            monthly_mortgage = loan_amount / num_payments

        # Cash flow with mortgage
        monthly_cash_flow_leveraged = estimated_monthly_rent - monthly_expenses - monthly_mortgage
        annual_cash_flow_leveraged = monthly_cash_flow_leveraged * 12

        # Cash-on-Cash Return: (Annual Cash Flow / Down Payment) * 100
        cash_on_cash_return = (
            (annual_cash_flow_leveraged / down_payment) * 100 if down_payment > 0 else 0
        )

        # Monthly cash flow (without mortgage, for display)
        monthly_cash_flow = estimated_monthly_rent - monthly_expenses

        # Breakeven years (simple payback period)
        breakeven_years = property_price / annual_net_income if annual_net_income > 0 else 999.9

        return InvestmentMetrics(
            cap_rate=round(cap_rate, 2),
            roi=round(roi, 2),
            price_to_rent_ratio=round(price_to_rent_ratio, 1),
            cash_on_cash_return=round(cash_on_cash_return, 2),
            monthly_cash_flow=int(monthly_cash_flow),
            annual_net_income=int(annual_net_income),
            breakeven_years=round(breakeven_years, 1),
        )

    def estimate_monthly_rent(self, property_price: int, zone: str | None = None) -> int:
        """
        Estimate monthly rental income based on property price and zone.

        Uses typical rental yields for Italian real estate markets.

        Args:
            property_price: Property value in EUR
            zone: Optional zone identifier for market-specific yields

        Returns:
            Estimated monthly rent in EUR
        """
        # Typical rental yields in Italy: 3-5% gross annual
        # Premium zones (historic centers): 3%
        # Standard zones: 4%
        # Suburban zones: 5%

        gross_yield = 0.04  # Default 4% annual yield

        # Adjust based on zone (simplified for MVP)
        if zone:
            zone_lower = zone.lower()
            if any(keyword in zone_lower for keyword in ["centro", "duomo", "center", "historic"]):
                gross_yield = 0.03  # 3% for premium zones
            elif any(keyword in zone_lower for keyword in ["periferia", "suburban", "outskirts"]):
                gross_yield = 0.05  # 5% for suburban

        annual_rent = property_price * gross_yield
        monthly_rent = int(annual_rent / 12)

        return monthly_rent
