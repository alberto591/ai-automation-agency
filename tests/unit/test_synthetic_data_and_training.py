"""Unit tests for synthetic data generation and XGBoost training pipeline.

Tests cover:
- SyntheticDataGenerator class
- Data quality and statistical properties
- Feature distributions
- XGBoost training script components
"""

from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pandas as pd
import pytest

from scripts.data.generate_synthetic_data import SyntheticDataGenerator


@pytest.mark.ml_required
class TestSyntheticDataGenerator:
    """Test suite for synthetic real estate data generation."""

    def test_generator_initialization(self):
        """Test generator initializes with correct seed."""
        generator = SyntheticDataGenerator(seed=42)
        assert generator is not None

    def test_generate_transactions_returns_dataframe(self):
        """Test that generation returns a pandas DataFrame."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=10)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10

    def test_dataframe_has_required_columns(self):
        """Test that generated data has all required columns."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=10)

        required_columns = [
            "zone_slug",
            "city",
            "address",
            "sale_date",
            "sale_price_eur",
            "sqm",
            "bedrooms",
            "bathrooms",
            "floor",
            "has_elevator",
            "has_balcony",
            "has_garden",
            "condition",
            "energy_class",
            "property_age_years",
            "cadastral_category",
            "latitude",
            "longitude",
        ]

        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_price_is_positive(self):
        """Test that all sale prices are positive."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=100)

        assert (df["sale_price_eur"] > 0).all()

    def test_sqm_within_reasonable_range(self):
        """Test that sqm values are realistic (30-250 sqm)."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=100)

        assert (df["sqm"] >= 30).all()
        assert (df["sqm"] <= 250).all()

    def test_bedrooms_correlation_with_sqm(self):
        """Test that larger properties have more bedrooms."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=500)

        # Properties <50sqm should mostly be 1 bedroom
        small_properties = df[df["sqm"] < 50]
        assert (small_properties["bedrooms"] <= 2).mean() > 0.9

        # Properties >140sqm should mostly be 4+ bedrooms
        large_properties = df[df["sqm"] > 140]
        assert (large_properties["bedrooms"] >= 4).mean() > 0.7

    def test_elevator_logic_by_floor(self):
        """Test that high floors are more likely to have elevators."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=500)

        # Ground floor properties should rarely have elevator marked as relevant
        ground_floor = df[df["floor"] == 0]
        high_floor = df[df["floor"] >= 4]

        # High floors should have elevator more often than ground floor
        assert high_floor["has_elevator"].mean() > ground_floor["has_elevator"].mean()

    def test_zone_distribution(self):
        """Test that zones are distributed across dataset."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=1000)

        # Should have multiple zones
        unique_zones = df["zone_slug"].nunique()
        assert unique_zones >= 10, f"Only {unique_zones} zones found, expected >=10"

        # No single zone should dominate (>30% of dataset)
        zone_counts = df["zone_slug"].value_counts()
        max_zone_pct = zone_counts.iloc[0] / len(df)
        assert max_zone_pct < 0.15, f"Zone distribution too skewed: {max_zone_pct:.1%}"

    def test_condition_distribution(self):
        """Test that property conditions follow expected distribution."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=1000)

        condition_counts = df["condition"].value_counts()

        # "good" should be most common (45% target)
        assert condition_counts.loc["good"] > condition_counts.loc["luxury"]
        assert condition_counts.loc["good"] > condition_counts.loc["poor"]

        # "luxury" and "poor" should be least common (5% each target)
        assert condition_counts.loc["luxury"] < condition_counts.loc["excellent"]
        assert condition_counts.loc["poor"] < condition_counts.loc["fair"]

    def test_price_varies_by_zone(self):
        """Test that different zones have different average prices."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=500)

        price_by_zone = df.groupby("zone_slug")["sale_price_eur"].mean()

        # Expensive zones (Milan, Florence Centro)
        if "centro-milano" in price_by_zone.index:
            centro_milano = price_by_zone.loc["centro-milano"]
            # Should be more expensive than average
            assert centro_milano > price_by_zone.median()

    def test_price_varies_by_condition(self):
        """Test that condition affects price as expected."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=500)

        # For same sqm range, luxury should cost more than poor
        sqm_range = df[(df["sqm"] >= 80) & (df["sqm"] <= 100)]

        if (
            len(sqm_range[sqm_range["condition"] == "luxury"]) > 5
            and len(sqm_range[sqm_range["condition"] == "poor"]) > 5
        ):
            luxury_avg = sqm_range[sqm_range["condition"] == "luxury"]["sale_price_eur"].mean()
            poor_avg = sqm_range[sqm_range["condition"] == "poor"]["sale_price_eur"].mean()

            assert luxury_avg > poor_avg

    def test_garden_only_on_ground_floor(self):
        """Test that gardens are only on ground floor properties."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=500)

        # All properties with garden should be floor 0
        has_garden_df = df[df["has_garden"] == True]  # noqa: E712
        assert (has_garden_df["floor"] == 0).all()

    def test_different_seed_produces_different_data(self):
        """Test that different seeds produce different data."""
        gen1 = SyntheticDataGenerator(seed=42)
        gen2 = SyntheticDataGenerator(seed=99)

        df1 = gen1.generate_transactions(n_samples=50)
        df2 = gen2.generate_transactions(n_samples=50)

        # At least some prices should differ
        assert not (df1["sale_price_eur"] == df2["sale_price_eur"]).all()

    def test_infer_bedrooms_logic(self):
        """Test bedroom inference from sqm."""
        generator = SyntheticDataGenerator(seed=42)

        assert generator._infer_bedrooms(40) == 1
        assert generator._infer_bedrooms(65) == 2
        assert generator._infer_bedrooms(90) in [2, 3]
        assert generator._infer_bedrooms(150) in [4, 5]

    def test_fake_coordinates_by_city(self):
        """Test that coordinates vary by city."""
        generator = SyntheticDataGenerator(seed=42)

        lat_firenze = generator._fake_lat("duomo-firenze")
        lat_milano = generator._fake_lat("centro-milano")

        # Florence and Milan have different base coordinates
        assert abs(lat_firenze - lat_milano) > 1.0  # At least 1 degree difference

    def test_price_statistics_are_reasonable(self):
        """Test that aggregate price statistics are realistic."""
        generator = SyntheticDataGenerator(seed=42)
        df = generator.generate_transactions(n_samples=1000)

        mean_price = df["sale_price_eur"].mean()
        median_price = df["sale_price_eur"].median()
        std_price = df["sale_price_eur"].std()

        # Mean should be in realistic range for Italian market (€200K - €800K)
        assert 200_000 < mean_price < 800_000

        # Std should be significant but not crazy (30-70% of mean)
        assert 0.3 < (std_price / mean_price) < 0.7

        # Median should be lower than mean (right-skewed distribution)
        assert median_price < mean_price


@pytest.mark.ml_required
class TestXGBoostTrainingComponents:
    """Test suite for XGBoost training script components."""

    @patch("infrastructure.ml.train_xgboost.pd.read_csv")
    def test_trainer_initialization(self, mock_read_csv):
        """Test XGBoostTrainer initializes correctly."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        trainer = XGBoostTrainer(random_state=42)
        assert trainer.random_state == 42
        assert trainer.model is None
        assert trainer.feature_names == []

    def test_feature_preparation_creates_correct_columns(self):
        """Test that feature preparation creates expected columns."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        # Create sample data
        df = pd.DataFrame(
            {
                "sqm": [100, 80],
                "bedrooms": [3, 2],
                "bathrooms": [2, 1],
                "floor": [2, 0],
                "property_age_years": [20, 30],
                "has_elevator": [True, False],
                "has_balcony": [True, True],
                "has_garden": [False, True],
                "zone_slug": ["duomo-firenze", "centro-milano"],
                "condition": ["good", "excellent"],
                "energy_class": ["C", "B"],
                "cadastral_category": ["A/3", "A/2"],
                "sale_price_eur": [500000, 600000],
            }
        )

        trainer = XGBoostTrainer()
        x_matrix, y = trainer.prepare_features(df)

        # Should have numeric + boolean + one-hot encoded features
        assert len(x_matrix.columns) > 8  # At least the base numeric/boolean features

        # Target should be sale price
        assert len(y) == 2
        assert (y == df["sale_price_eur"]).all()

    def test_feature_preparation_handles_missing_values(self):
        """Test that missing values are handled correctly."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        df = pd.DataFrame(
            {
                "sqm": [100, 80],
                "bedrooms": [3, None],  # Missing value
                "bathrooms": [2, 1],
                "floor": [2, 0],
                "property_age_years": [None, 30],  # Missing value
                "has_elevator": [True, False],
                "has_balcony": [True, True],
                "has_garden": [False, True],
                "zone_slug": ["duomo-firenze", "centro-milano"],
                "condition": ["good", "excellent"],
                "energy_class": ["C", "B"],
                "cadastral_category": ["A/3", "A/2"],
                "sale_price_eur": [500000, 600000],
            }
        )

        trainer = XGBoostTrainer()
        x_matrix, y = trainer.prepare_features(df)

        # No NaN values should remain
        assert not x_matrix.isnull().any().any()

    @patch("infrastructure.ml.train_xgboost.GridSearchCV")
    def test_train_with_hyperparameter_tuning(self, mock_grid_search):
        """Test training with hyperparameter tuning enabled."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        # Mock GridSearchCV
        mock_estimator = MagicMock()
        mock_grid_search.return_value.best_estimator_ = mock_estimator
        mock_grid_search.return_value.best_params_ = {"max_depth": 5}

        # Create sample data
        x_train = pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]})
        y_train = pd.Series([100, 200, 300])
        x_val = pd.DataFrame({"feature1": [7], "feature2": [8]})
        y_val = pd.Series([400])

        trainer = XGBoostTrainer()
        trainer.train(x_train, y_train, x_val, y_val, tune_hyperparams=True)

        # GridSearchCV should have been called
        mock_grid_search.assert_called_once()
        assert trainer.model == mock_estimator

    def test_model_save_creates_files(self):
        """Test that save_model creates both model and metadata files."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        trainer = XGBoostTrainer()
        trainer.feature_names = ["sqm", "bedrooms"]
        trainer.metrics = {"mape": 15.0, "r2": 0.75}

        # Mock the model
        mock_model = MagicMock()
        trainer.model = mock_model

        with patch("builtins.open", mock_open()):
            with patch("pathlib.Path.mkdir"):
                trainer.save_model("test_model.json", metadata={"test": "value"})

        # Model save should have been called
        mock_model.get_booster.return_value.save_model.assert_called_once_with("test_model.json")

    def test_evaluate_calculates_metrics(self):
        """Test that evaluate calculates all required metrics."""
        from infrastructure.ml.train_xgboost import XGBoostTrainer

        trainer = XGBoostTrainer()

        # Mock model predictions
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([100, 200, 300])
        x_test = pd.DataFrame({"feature1": [1, 2, 3]})
        y_test = pd.Series([110, 190, 310])
        trainer.model = mock_model

        metrics = trainer.evaluate(x_test, y_test)

        assert "mae" in metrics
        assert "mape" in metrics
        assert "r2" in metrics
        assert "n_test" in metrics
        assert metrics["n_test"] == 3
