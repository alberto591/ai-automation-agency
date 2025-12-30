import json
import os
import shutil
import time
from datetime import datetime
from typing import Any, cast

import xgboost as xgb
from pydantic import BaseModel, Field

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class ModelMetadata(BaseModel):
    """Metadata for a saved model version."""

    version: str
    timestamp: float
    author: str = Field(default="system")
    metrics: dict[str, float | None] = Field(default_factory=dict)
    description: str = Field(default="")
    parameters: dict[str, Any] = Field(default_factory=dict)


class ModelRegistry:
    """
    Manages storage and versioning of ML models.
    Uses a local filesystem directory structure.
    """

    def __init__(self, storage_path: str = ".models"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Creates storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def _get_version_path(self, version: str) -> str:
        return os.path.join(self.storage_path, version)

    def list_models(self) -> list[ModelMetadata]:
        """Lists all available models in the registry."""
        models: list[ModelMetadata] = []
        if not os.path.exists(self.storage_path):
            return models

        for version in os.listdir(self.storage_path):
            meta_path = os.path.join(self.storage_path, version, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path) as f:
                        data = json.load(f)
                        models.append(ModelMetadata(**data))
                except Exception as e:
                    logger.warning(
                        "FAILED_TO_LOAD_MODEL_METADATA",
                        context={"version": version, "error": str(e)},
                    )

        # Sort by timestamp descending (newest first)
        return sorted(models, key=lambda x: x.timestamp, reverse=True)

    def save_model(
        self,
        model: xgb.XGBRegressor,
        metrics: dict[str, float],
        description: str = "",
        author: str = "system",
    ) -> str:
        """
        Saves a model to the registry.
        Returns the version string (timestamp-based).
        """
        timestamp = time.time()
        # Use microseconds to avoid collision in tests
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S_%f")
        version = f"v_{date_str}"

        version_path = self._get_version_path(version)
        os.makedirs(version_path, exist_ok=True)

        # Save model artifact - using UBJ (Binary) for robustness
        model_path = os.path.join(version_path, "model.ubj")
        # Use underlying booster to avoid sklearn metadata issues
        model.get_booster().save_model(model_path)

        if not os.path.exists(model_path):
            raise RuntimeError(f"Failed to save model artifact to {model_path}")

        # Save metadata
        metadata = ModelMetadata(
            version=version,
            timestamp=timestamp,
            author=author,
            metrics=cast(dict[str, float | None], metrics),
            description=description,
            parameters=model.get_params(),
        )

        meta_path = os.path.join(version_path, "metadata.json")
        with open(meta_path, "w") as f:
            f.write(metadata.model_dump_json(indent=2))

        logger.info("MODEL_SAVED", context={"version": version, "metrics": metrics})
        return version

    def load_model(self, version: str) -> xgb.XGBRegressor | None:
        """Loads a specific model version."""
        version_path = self._get_version_path(version)
        model_path = os.path.join(version_path, "model.ubj")

        if not os.path.exists(model_path):
            logger.error("MODEL_NOT_FOUND", context={"version": version})
            return None

        try:
            # Load as raw booster then wrap
            booster = xgb.Booster()
            booster.load_model(model_path)

            model = xgb.XGBRegressor()
            model._Booster = booster
            return model
        except Exception as e:
            # Re-raise for debugging during tests, or at least print
            logger.error("FAILED_TO_LOAD_MODEL", context={"version": version, "error": str(e)})
            return None

    def get_best_model(
        self, metric: str = "mape", lower_is_better: bool = True
    ) -> xgb.XGBRegressor | None:
        """Retrieves the best performing model based on a metric."""
        models = self.list_models()
        if not models:
            return None

        # Filter models that have the metric and it is not None
        valid_models = [m for m in models if metric in m.metrics and m.metrics[metric] is not None]
        if not valid_models:
            logger.warning("NO_MODELS_WITH_METRIC", context={"metric": metric})
            return None

        # Sort based on metric
        valid_models.sort(key=lambda x: cast(float, x.metrics[metric]), reverse=not lower_is_better)
        best_version = valid_models[0].version

        logger.info(
            "LOADING_BEST_MODEL",
            context={
                "version": best_version,
                "metric": metric,
                "value": valid_models[0].metrics[metric],
            },
        )
        return self.load_model(best_version)

    def delete_model(self, version: str) -> bool:
        """Deletes a model version."""
        version_path = self._get_version_path(version)
        if os.path.exists(version_path):
            shutil.rmtree(version_path)
            logger.info("MODEL_DELETED", context={"version": version})
            return True
        return False
