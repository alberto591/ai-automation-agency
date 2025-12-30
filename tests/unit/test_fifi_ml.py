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
