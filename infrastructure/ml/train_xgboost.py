"""XGBoost model training script for Fifi AI Appraisal System.

Trains a gradient boosting model to predict property values based on features.
Includes hyperparameter tuning, cross-validation, and model persistence.

Usage:
    python infrastructure/ml/train_xgboost.py --data data/synthetic_transactions.csv --output models/fifi_xgboost_v1.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from infrastructure.logging import get_logger
from infrastructure.ml.model_registry import ModelRegistry

logger = get_logger(__name__)


class XGBoostTrainer:
    """Handles XGBoost model training, evaluation, and persistence."""

    def __init__(self, random_state: int = 42) -> None:
        """Initialize trainer with random seed."""
        self.random_state = random_state
        self.model: XGBRegressor | None = None
        self.scaler = StandardScaler()
        self.feature_names: list[str] = []
        self.metrics: dict[str, Any] = {}
        self.train_metrics: dict[str, Any] = {}

    def prepare_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Prepare feature matrix and target vector."""
        logger.info("FEATURE_PREPARATION_START", context={"n_rows": len(df)})

        # Define features to use
        numeric_features = ["sqm", "bedrooms", "bathrooms", "floor", "property_age_years"]
        boolean_features = ["has_elevator", "has_balcony", "has_garden"]
        categorical_features = ["zone_slug", "condition", "energy_class", "cadastral_category"]

        # Create feature matrix (using lowercase x for ruff)
        x = df[numeric_features + boolean_features].copy()

        # Convert booleans to int
        for col in boolean_features:
            x[col] = x[col].astype(int)

        # One-hot encode categoricals
        for col in categorical_features:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                x = pd.concat([x, dummies], axis=1)

        # Handle missing values
        x = x.fillna(x.median())

        # Target variable
        y = df["sale_price_eur"]

        self.feature_names = x.columns.tolist()
        logger.info("FEATURE_PREPARATION_COMPLETE", context={"n_features": len(self.feature_names)})

        return x, y

    def train(
        self,
        x_train: pd.DataFrame,
        y_train: pd.Series,
        x_val: pd.DataFrame,
        y_val: pd.Series,
        tune_hyperparams: bool = True,
    ) -> None:
        """Train XGBoost model with optional hyperparameter tuning.

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            tune_hyperparams: Whether to run GridSearchCV
        """
        logger.info("MODEL_TRAINING_START", context={"tune_hyperparams": tune_hyperparams})

        if tune_hyperparams:
            # Hyperparameter grid
            param_grid = {
                "n_estimators": [100, 200],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.05, 0.1],
                "subsample": [0.8, 1.0],
                "colsample_bytree": [0.8, 1.0],
            }

            base_model = XGBRegressor(random_state=self.random_state, objective="reg:squarederror")

            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=3,
                scoring="neg_mean_absolute_error",
                n_jobs=-1,
                verbose=1,
            )

            logger.info("GRID_SEARCH_START", context={"param_combinations": len(param_grid)})
            grid_search.fit(x_train, y_train)

            self.model = grid_search.best_estimator_
            logger.info("GRID_SEARCH_COMPLETE", context={"best_params": grid_search.best_params_})
        else:
            # Use default parameters
            self.model = XGBRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                objective="reg:squarederror",
            )

            self.model.fit(
                x_train,
                y_train,
                eval_set=[(x_val, y_val)],
                verbose=False,
            )

        logger.info("MODEL_TRAINING_COMPLETE")

    def evaluate(self, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
        """Evaluate model on test set."""
        assert self.model is not None
        y_pred = self.model.predict(x_test)

        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100  # Convert to percentage
        r2 = r2_score(y_test, y_pred)

        # Calculate train/test delta (check for overfitting)
        if self.train_metrics and "mape" in self.train_metrics:
            train_test_delta = abs(self.train_metrics["mape"] - mape)
        else:
            train_test_delta = None

        self.metrics = {
            "mae": mae,
            "mape": mape,
            "r2": r2,
            "train_test_delta": train_test_delta,
            "n_test": len(y_test),
        }

        logger.info("MODEL_EVALUATION_COMPLETE", context=self.metrics)

        return self.metrics

    def save_model(self, output_path: str, metadata: dict[str, Any] | None = None) -> None:
        """Save trained model and metadata to disk."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save XGBoost model using booster format
        assert self.model is not None, "Model must be trained before saving."
        self.model.get_booster().save_model(output_path)

        # Save metadata
        metadata_path = output_path.replace(".json", "_metadata.json")
        full_metadata = {
            "version": "v1.0",
            "training_date": datetime.now().isoformat(),
            "model_path": output_path,
            "feature_names": self.feature_names,
            "n_features": len(self.feature_names),
            "metrics": self.metrics,
            **(metadata or {}),
        }

        with open(metadata_path, "w") as f:
            json.dump(full_metadata, f, indent=2)

        logger.info(
            "MODEL_SAVED", context={"model_path": output_path, "metadata_path": metadata_path}
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train XGBoost model for property valuation")
    parser.add_argument("--data", type=str, required=True, help="Path to training data CSV")
    parser.add_argument("--no_tune", action="store_true", help="Skip hyperparameter tuning")
    parser.add_argument("--test_size", type=float, default=0.15, help="Test set proportion")

    args = parser.parse_args()

    # Load data
    logger.info("LOADING_DATA", context={"path": args.data})
    df = pd.read_csv(args.data)
    logger.info("DATA_LOADED", context={"shape": df.shape})

    # Initialize trainer
    trainer = XGBoostTrainer()

    # Prepare features
    train_x, train_y = trainer.prepare_features(df)

    # Split data: 70% train, 15% val, 15% test
    x_temp, x_test, y_temp, y_test = train_test_split(
        train_x, train_y, test_size=args.test_size, random_state=42
    )

    x_train, x_val, y_train, y_val = train_test_split(
        x_temp, y_temp, test_size=args.test_size / (1 - args.test_size), random_state=42
    )

    logger.info(
        "DATA_SPLIT_COMPLETE",
        context={
            "train": len(x_train),
            "val": len(x_val),
            "test": len(x_test),
        },
    )

    # Train model
    trainer.train(x_train, y_train, x_val, y_val, tune_hyperparams=not args.no_tune)

    # Evaluate on test set
    metrics = trainer.evaluate(x_test, y_test)

    # Print results
    print("\n" + "=" * 60)
    print("XGBOOST MODEL TRAINING COMPLETE")
    print("=" * 60)
    print("=" * 60)
    print("\nTest Set Metrics:")
    print(f"  MAE: €{metrics['mae']:,.0f}")
    print(f"  MAPE: {metrics['mape']:.2f}%")
    print(f"  R²: {metrics['r2']:.4f}")
    print(f"  Test Samples: {metrics['n_test']:,}")

    if metrics["mape"] < 20:
        print("\n✅ SUCCESS: MAPE < 20% (Target Achieved!)")
    else:
        print("\n⚠️  WARNING: MAPE > 20% (Target Not Met)")

    print("=" * 60)

    # Save to Registry
    logger.info("SAVING_TO_REGISTRY")
    registry = ModelRegistry()

    version = registry.save_model(
        trainer.model,
        metrics=metrics,
        description=f"XGBoost AVM trained on {len(df)} samples",
        author="system_training_script",
    )

    print(f"\n✅ Model saved to registry: {version}")


if __name__ == "__main__":
    main()
