import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from xgboost import Booster

from infrastructure.logging import get_logger

from .feature_engineering import PropertyFeatures

logger = get_logger(__name__)


class XGBoostAdapter:
    """
    Adapter for XGBoost model inference.
    Loads trained XGBoost model and provides prediction with uncertainty estimation.
    """

    def __init__(self, model_path: str = "models/fifi_xgboost_v1.json") -> None:
        """Initialize adapter and load trained model."""
        self.model_path = model_path
        self.model_version = "v1.0"
        self.feature_names: list[str] = []
        self.model = self._load_model()

    def _load_model(self) -> Booster | None:
        """Load XGBoost model from disk.

        Returns:
            Loaded Booster model or None if file not found
        """
        if not Path(self.model_path).exists():
            logger.warning(
                "MODEL_NOT_FOUND",
                context={"path": self.model_path, "using_fallback": True},
            )
            return None

        try:
            # Load model
            booster = Booster()
            booster.load_model(self.model_path)

            # Load metadata
            metadata_path = self.model_path.replace(".json", "_metadata.json")
            if Path(metadata_path).exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get("version", "v1.0")
                    self.feature_names = metadata.get("feature_names", [])
                    logger.info(
                        "MODEL_LOADED",
                        context={
                            "path": self.model_path,
                            "version": self.model_version,
                            "n_features": len(self.feature_names),
                        },
                    )
            else:
                logger.warning("MODEL_METADATA_NOT_FOUND", context={"metadata_path": metadata_path})

            return booster
        except Exception as e:
            logger.error(
                "MODEL_LOAD_ERROR",
                context={"path": self.model_path, "error": str(e)},
                exc_info=True,
            )
            return None

    def _prepare_features_for_inference(self, features: PropertyFeatures) -> pd.DataFrame:
        """Convert PropertyFeatures to model input format.

        Args:
            features: Pydantic model with property characteristics

        Returns:
            DataFrame with features in correct order and encoding
        """
        # Create base feature dict
        feature_dict = {
            "sqm": features.sqm,
            "bedrooms": features.bedrooms,
            "bathrooms": features.bathrooms,
            "floor": features.floor,
            "has_elevator": int(features.has_elevator),
            "has_balcony": int(features.has_balcony),
            "has_garden": int(features.has_garden),
        }

        # Add optional fields with defaults
        if features.property_age_years:
            feature_dict["property_age_years"] = features.property_age_years
        else:
            feature_dict["property_age_years"] = 30  # Default age

        # One-hot encode categoricals (must match training)
        # Zone slugs
        if features.zone_slug:
            for zone in [
                "brera-milano",
                "centro-bologna",
                "centro-lucca",
                "centro-milano",
                "centro-pisa",
                "centro-storico-roma",
                "duomo-firenze",
                "lambrate-milano",
                "navigli-milano",
                "novoli-firenze",
                "oltrarno-firenze",
                "porta-romana-milano",
                "prati-roma",
                "rifredi-firenze",
                "san-lorenzo-roma",
                "santa-croce-firenze",
                "testaccio-roma",
                "trastevere-roma",
            ]:
                feature_dict[f"zone_slug_{zone}"] = int(features.zone_slug == zone)

        # Condition
        for cond in ["fair", "good", "luxury", "poor"]:
            feature_dict[f"condition_{cond}"] = int(features.condition == cond)

        # Energy class
        if features.energy_class:
            for ec in ["B", "C", "D", "E", "F", "G"]:
                feature_dict[f"energy_class_{ec}"] = int(features.energy_class == ec)

        # Cadastral category
        if features.cadastral_category:
            for cat in ["A/3", "A/4", "A/7"]:
                feature_dict[f"cadastral_category_{cat}"] = int(features.cadastral_category == cat)

        # Convert to DataFrame
        df = pd.DataFrame([feature_dict])

        # Ensure all expected features are present (add missing as 0)
        if self.feature_names:
            for fname in self.feature_names:
                if fname not in df.columns:
                    df[fname] = 0
            # Reorder to match training
            df = df[self.feature_names]

        return df

    def predict(self, features: PropertyFeatures) -> float:
        """Predicts property value based on features.

        Args:
            features: PropertyFeatures object with property characteristics

        Returns:
            Predicted property value in EUR
        """
        logger.info(
            "AVM_PREDICTION_START",
            context={
                "sqm": features.sqm,
                "zone": features.zone_slug,
                "model_version": self.model_version,
            },
        )

        # Fallback to heuristic if model not loaded
        if self.model is None:
            logger.warning("USING_HEURISTIC_FALLBACK")
            base_price_sqm = 5000
            condition_multipliers = {
                "luxury": 1.4,
                "excellent": 1.2,
                "good": 1.0,
                "fair": 0.8,
                "poor": 0.6,
            }
            multiplier = condition_multipliers.get(features.condition, 1.0)
            predicted_value = features.sqm * base_price_sqm * multiplier
            logger.info(
                "HEURISTIC_PREDICTION_COMPLETE", context={"predicted_value": predicted_value}
            )
            return float(predicted_value)

        # Use trained model
        x = self._prepare_features_for_inference(features)

        try:
            # Convert to DMatrix and predict
            from xgboost import DMatrix

            dmatrix = DMatrix(x)
            prediction = self.model.predict(dmatrix)[0]

            logger.info(
                "AVM_PREDICTION_COMPLETE",
                context={"predicted_value": float(prediction), "model_version": self.model_version},
            )
            return float(prediction)
        except Exception as e:
            logger.error("PREDICTION_ERROR", context={"error": str(e)}, exc_info=True)
            # Fallback to heuristic on error
            base_price_sqm = 5000
            return float(features.sqm * base_price_sqm)

    def calculate_uncertainty(self, prediction: float, comps: list[dict[str, Any]]) -> float:
        """
        Calculates uncertainty score (std_dev / prediction).
        """
        if not comps:
            return 0.25  # Default high uncertainty if no comps

        prices = [c.get("sale_price_eur", 0) for c in comps]
        if not prices:
            return 0.25

        std_dev = np.std(prices)
        return float(std_dev / prediction)

    def calculate_investment_metrics(
        self, property_value: float, sqm: int, zone: str | None = None
    ) -> dict[str, Any]:
        """
        Calculate investment metrics for a property.

        Args:
            property_value: Estimated property value in EUR
            sqm: Property size in square meters
            zone: Zone slug for market-specific calculations

        Returns:
            Dictionary with investment metrics
        """
        # Rental yield assumptions by zone (monthly rent per sqm)
        zone_rent_sqm = {
            "centro-milano": 18,
            "centro-firenze": 16,
            "centro-roma": 15,
            "centro-bologna": 14,
            "centro-lucca": 12,
            "default": 13,
        }

        # Get monthly rent per sqm
        monthly_rent_sqm = zone_rent_sqm.get(zone or "default", zone_rent_sqm["default"])
        monthly_rent = monthly_rent_sqm * sqm
        annual_rent = monthly_rent * 12

        # Cap Rate (Gross Yield) = Annual Rent / Property Value
        cap_rate = (annual_rent / property_value) * 100 if property_value > 0 else 0

        # Assume 20% down payment for Cash-on-Cash calculation
        down_payment = property_value * 0.20
        # Annual cash flow (simplified: annual rent - estimated expenses)
        annual_expenses = annual_rent * 0.30  # 30% for taxes, maintenance, vacancy
        annual_cash_flow = annual_rent - annual_expenses

        # Cash-on-Cash Return
        cash_on_cash = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0

        # ROI (5-year projection with 3% annual appreciation)
        appreciation_rate = 0.03
        future_value = property_value * ((1 + appreciation_rate) ** 5)
        total_rental_income = annual_rent * 5
        total_return = (future_value - property_value) + total_rental_income
        roi_5_year = (total_return / property_value) * 100 if property_value > 0 else 0

        return {
            "monthly_rent": int(monthly_rent),
            "annual_rent": int(annual_rent),
            "cap_rate": round(cap_rate, 2),
            "gross_yield": round(cap_rate, 2),  # Same as cap rate
            "cash_on_cash_return": round(cash_on_cash, 2),
            "roi_5_year": round(roi_5_year, 2),
            "down_payment_20pct": int(down_payment),
            "annual_cash_flow": int(annual_cash_flow),
        }
