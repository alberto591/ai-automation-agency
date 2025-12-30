import logging

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.model_selection import train_test_split

from infrastructure.logging import get_logger
from infrastructure.ml.model_registry import ModelRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

DATA_PATH = "data/synthetic_transactions.csv"


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found at {path}")
    df = pd.read_csv(path)
    logger.info("DATA_LOADED", context={"rows": len(df)})
    return df


def calculate_metrics(y_true, y_pred):
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    # Calculate MdAPE (Median Absolute Percentage Error) manually
    ape = np.abs((y_true - y_pred) / y_true)
    mdape = np.median(ape)

    return {"mape": float(mape), "rmse": float(rmse), "mdape": float(mdape)}


from infrastructure.ml.train_xgboost import XGBoostTrainer

# ... (rest of imports)


def run_backtest():
    registry = ModelRegistry()

    # Get best model and its metadata
    # We need to manually find the best version string first to get metadata,
    # as registry.get_best_model only returns the model object currently.
    # Actually, let's list models, find best, then load.

    models = registry.list_models()
    if not models:
        logger.error("NO_MODELS_FOUND")
        return

    # Filter for mape metric
    valid_models = [m for m in models if "mape" in m.metrics]
    if not valid_models:
        logger.error("NO_MODELS_WITH_MAPE")
        return

    best_meta = sorted(valid_models, key=lambda x: x.metrics["mape"])[0]
    best_version = best_meta.version
    logger.info(
        "BEST_MODEL_SELECTED", context={"version": best_version, "mape": best_meta.metrics["mape"]}
    )

    best_model = registry.load_model(best_version)
    if not best_model:
        logger.error("FAILED_TO_LOAD_BEST_MODEL")
        return

    # Load Data
    try:
        df = load_data(DATA_PATH)
    except Exception as e:
        logger.error("BACKTEST_FAILED", context={"reason": "Data load error", "detail": str(e)})
        return

    # Prepare features using the Trainer's logic
    trainer = XGBoostTrainer()
    x_data, y_data = trainer.prepare_features(df)

    # Align columns with model expectation
    # The saved metadata has 'feature_names' in 'parameters' or explicit field?
    # ModelMetadata has 'parameters' which stores model.get_params().
    # train_xgboost.py saved 'feature_names' in the *metadata.json file* but ALSO registry saves ModelMetadata.
    # Wait, registry.save_model receives 'parameters' from model.get_params(), but train_xgboost.py tried to save extra metadata...
    # In train_xgboost.py I didn't pass feature_names to registry.save_model!
    # I only passed metrics and description.
    # CRITICAL MISS: I need the feature names to align validation data.
    # I can try to get them from the booster if saved? model.get_booster().feature_names

    model_feature_names = best_model.get_booster().feature_names

    if not model_feature_names:
        logger.warning("MODEL_HAS_NO_FEATURE_NAMES_SAVED", context={"version": best_version})
        # Fallback to current x_data columns and hope?
        model_feature_names = x_data.columns.tolist()

    # Reindex X to match model features (adds 0 for missing, drops extra)
    x_aligned = x_data.reindex(columns=model_feature_names, fill_value=0)

    # Split
    x_train, x_test, y_train, y_test = train_test_split(
        x_aligned, y_data, test_size=0.2, random_state=42
    )

    # Predict
    y_pred = best_model.predict(x_test)

    # Calculate Metrics
    metrics = calculate_metrics(y_test, y_pred)

    print("\n" + "=" * 40)
    print(" 📉 AVM BACKTEST REPORT")
    print("=" * 40)
    print(f" Datapoints: {len(x_test)}")
    print("-" * 20)
    print(f" ✅ MAPE  : {metrics['mape']:.4%}")
    print(f" ✅ MdAPE : {metrics['mdape']:.4%}")
    print(f" ✅ RMSE  : €{metrics['rmse']:,.2f}")
    print("=" * 40 + "\n")

    logger.info("BACKTEST_COMPLETE", context=metrics)


import os

if __name__ == "__main__":
    run_backtest()
