from unittest.mock import MagicMock, patch

from infrastructure.ml.feature_engineering import PropertyFeatures, extract_property_features
from infrastructure.ml.xgboost_adapter import XGBoostAdapter


def test_property_features_model():
    """Test PropertyFeatures Pydantic model validation."""
    features = PropertyFeatures(sqm=100, bedrooms=3, condition="excellent")
    assert features.sqm == 100
    assert features.bedrooms == 3
    assert features.condition == "excellent"
    assert features.has_elevator is False  # Default


@patch("infrastructure.ml.feature_engineering.ChatMistralAI")
def test_extract_property_features(mock_mistral):
    """Test LLM-based feature extraction."""
    # Mock LLM and structured output
    mock_llm = MagicMock()
    mock_mistral.return_value.with_structured_output.return_value = mock_llm

    mock_llm.invoke.return_value = PropertyFeatures(
        sqm=90, floor=3, has_elevator=True, condition="good"
    )

    res = extract_property_features("Appartamento di 90mq con ascensore")

    assert res.sqm == 90
    assert res.has_elevator is True
    assert res.condition == "good"


@pytest.mark.ml_required
def test_xgboost_adapter_prediction():
    """Test the XGBoostAdapter with trained XGBoost model."""
    adapter = XGBoostAdapter()
    features = PropertyFeatures(sqm=100, condition="excellent")

    prediction = adapter.predict(features)

    # Verify prediction is reasonable (not heuristic and not zero)
    assert prediction > 0, "Prediction must be positive"
    assert (
        300000 < prediction < 1000000
    ), "Prediction should be in reasonable range for 100sqm excellent property"

    # Verify model was loaded (should have version from metadata)
    assert adapter.model_version == "v1.0"
    assert adapter.model is not None, "Model should be loaded"


@pytest.mark.ml_required
def test_xgboost_adapter_uncertainty():
    """Test uncertainty calculation."""
    adapter = XGBoostAdapter()
    prediction = 500000.0

    # Comps with high variance
    comps = [{"sale_price_eur": 400000}, {"sale_price_eur": 600000}]

    uncertainty = adapter.calculate_uncertainty(prediction, comps)
    assert uncertainty > 0.1  # Should be significant

    # No comps -> high uncertainty
    assert adapter.calculate_uncertainty(prediction, []) == 0.25


# --- Investment Metrics Tests ---


@pytest.mark.ml_required
def test_investment_metrics_basic_calculation():
    """Test basic investment metrics calculation."""
    adapter = XGBoostAdapter()

    metrics = adapter.calculate_investment_metrics(
        property_value=500000.0,
        sqm=100,
        zone="centro-milano",
    )

    # Verify all expected keys are present
    assert "monthly_rent" in metrics
    assert "annual_rent" in metrics
    assert "cap_rate" in metrics
    assert "gross_yield" in metrics
    assert "cash_on_cash_return" in metrics
    assert "roi_5_year" in metrics
    assert "down_payment_20pct" in metrics
    assert "annual_cash_flow" in metrics


@pytest.mark.ml_required
def test_investment_metrics_rent_calculation():
    """Test that rent is calculated correctly based on zone."""
    adapter = XGBoostAdapter()

    # Milano: €18/sqm
    metrics_milano = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone="centro-milano"
    )
    assert metrics_milano["monthly_rent"] == 1800  # 100 * 18

    # Lucca: €12/sqm
    metrics_lucca = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone="centro-lucca"
    )
    assert metrics_lucca["monthly_rent"] == 1200  # 100 * 12

    # Default zone
    metrics_default = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone=None
    )
    assert metrics_default["monthly_rent"] == 1300  # 100 * 13 (default)


@pytest.mark.ml_required
def test_investment_metrics_cap_rate():
    """Test Cap Rate calculation."""
    adapter = XGBoostAdapter()

    # Milano: 100sqm = €1800/month = €21600/year
    # Cap Rate = (21600 / 500000) * 100 = 4.32%
    metrics = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone="centro-milano"
    )

    expected_cap_rate = (1800 * 12 / 500000) * 100
    assert metrics["cap_rate"] == round(expected_cap_rate, 2)
    assert metrics["gross_yield"] == metrics["cap_rate"]  # Should be same


@pytest.mark.ml_required
def test_investment_metrics_cash_on_cash():
    """Test Cash-on-Cash Return calculation."""
    adapter = XGBoostAdapter()

    metrics = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone="centro-milano"
    )

    # Monthly rent: €1800
    # Annual rent: €21600
    # Expenses (30%): €6480
    # Cash flow: €15120
    # Down payment (20%): €100000
    # CoC: (15120 / 100000) * 100 = 15.12%
    assert metrics["down_payment_20pct"] == 100000
    assert metrics["annual_cash_flow"] == 15120  # 21600 - 6480
    assert metrics["cash_on_cash_return"] == round((15120 / 100000) * 100, 2)


@pytest.mark.ml_required
def test_investment_metrics_roi_5_year():
    """Test 5-year ROI projection."""
    adapter = XGBoostAdapter()

    metrics = adapter.calculate_investment_metrics(
        property_value=500000.0, sqm=100, zone="centro-milano"
    )

    # Appreciation: 500000 * (1.03^5) = ~579,637
    # Value gain: ~79,637
    # Rental income (5 years): 21600 * 5 = 108000
    # Total return: ~187,637
    # ROI: (187,637 / 500000) * 100 = ~37.5%
    assert metrics["roi_5_year"] > 30  # Should be around 37%
    assert metrics["roi_5_year"] < 45


@pytest.mark.ml_required
def test_investment_metrics_edge_cases():
    """Test edge cases for investment metrics."""
    adapter = XGBoostAdapter()

    # Zero property value (should not divide by zero)
    metrics_zero = adapter.calculate_investment_metrics(
        property_value=0, sqm=100, zone="centro-milano"
    )
    assert metrics_zero["cap_rate"] == 0
    assert metrics_zero["roi_5_year"] == 0

    # Very small property
    metrics_small = adapter.calculate_investment_metrics(
        property_value=100000.0, sqm=20, zone="centro-lucca"
    )
    assert metrics_small["monthly_rent"] == 240  # 20 * 12
    assert metrics_small["cap_rate"] > 0


@pytest.mark.ml_required
def test_investment_metrics_all_zones():
    """Test that all supported zones have different rent rates."""
    adapter = XGBoostAdapter()

    zones = [
        ("centro-milano", 18),
        ("centro-firenze", 16),
        ("centro-roma", 15),
        ("centro-bologna", 14),
        ("centro-lucca", 12),
    ]

    for zone, expected_rate in zones:
        metrics = adapter.calculate_investment_metrics(property_value=500000.0, sqm=100, zone=zone)
        expected_rent = 100 * expected_rate
        assert (
            metrics["monthly_rent"] == expected_rent
        ), f"Zone {zone} should have rent {expected_rent}"
