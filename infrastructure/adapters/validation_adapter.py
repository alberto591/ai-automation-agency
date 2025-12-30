from datetime import UTC, datetime
from typing import Any, cast

from domain.ports import ValidationPort
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PostgresValidationAdapter(ValidationPort, SupabaseAdapter):
    """
    Adapter for logging appraisal validations and detecting drift using Supabase (Postgres).
    Inherits from SupabaseAdapter to reuse client connection.
    """

    def log_validation(
        self,
        predicted_value: int,
        actual_value: int,
        metadata: dict[str, Any],
        uncertainty_score: float | None = None,
        lead_id: str | None = None,
        model_version: str = "xgboost_v1",
    ) -> None:
        """
        Logs a validation event (prediction vs actual) to the DB.
        """
        try:
            error_pct = (predicted_value - actual_value) / actual_value if actual_value else 0.0

            row = {
                "appraisal_date": datetime.now(UTC).isoformat(),
                "lead_id": lead_id,
                "model_version": model_version,
                "predicted_value_eur": predicted_value,
                "actual_sale_price_eur": actual_value,  # Assuming verify against Sale Price
                # If validating against Listing Price, map to actual_listing_price_eur?
                # For simplified shadow mode, we map 'actual' to what we have.
                # Let's check metadata for source type if needed, but for now map to sale price column if it's 'sold',
                # or we need to be flexible.
                # The schema has actual_listing_price_eur AND actual_sale_price_eur.
                # Let's prefer 'actual_sale_price_eur' for strict validation,
                # but if metadata says "listing", use that.
                "error_pct": round(error_pct, 4),
                "uncertainty_score": uncertainty_score,
                "zone": metadata.get("zone", "UNKNOWN"),
                "city": metadata.get("city", "UNKNOWN"),
                "fifi_status": metadata.get("fifi_status", "AUTO_APPROVED"),
                "alert_triggered": abs(error_pct) > 0.20,
            }

            # Contextual mapping
            if metadata.get("price_type") == "listing":
                row["actual_listing_price_eur"] = actual_value
            else:
                row["actual_sale_price_eur"] = actual_value

            self.client.table("appraisal_validations").insert(row).execute()

            if abs(error_pct) > 0.20:
                logger.warning(
                    "DRIFT_ALERT_TRIGGERED",
                    context={
                        "zone": row["zone"],
                        "error_pct": row["error_pct"],
                        "predicted": predicted_value,
                        "actual": actual_value,
                    },
                )

        except Exception as e:
            logger.error("LOG_VALIDATION_FAILED", context={"error": str(e)})
            # We don't raise here to avoid breaking the main flow if logging metrics fails

    def detect_drift(self, zone: str, threshold: float = 0.15) -> bool:
        """
        Checks if the Moving Average Percentage Error (MAPE) for a zone
        exceeds the threshold in the last 50 validations.
        """
        try:
            # We can't do complex aggregation easily via REST without an RPC.
            # So we fetch the last 50 rows for this zone.
            res = (
                self.client.table("appraisal_validations")
                .select("error_pct")
                .eq("zone", zone)
                .order("appraisal_date", desc=True)
                .limit(50)
                .execute()
            )
            data = cast(list[dict[str, Any]], res.data)

            if not data:
                return False

            errors = [abs(d["error_pct"]) for d in data if d["error_pct"] is not None]
            if not errors:
                return False

            mape = sum(errors) / len(errors)

            if mape > threshold:
                logger.warning("ZONE_DRIFT_DETECTED", context={"zone": zone, "mape": mape})
                return True

            return False

        except Exception as e:
            logger.error("DETECT_DRIFT_FAILED", context={"error": str(e)})
            return False
