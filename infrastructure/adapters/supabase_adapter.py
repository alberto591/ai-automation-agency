from typing import Any

from supabase import create_client
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from domain.errors import DatabaseError
from domain.ports import DatabasePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class SupabaseAdapter(DatabasePort):
    def __init__(self) -> None:
        try:
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
            self.client = create_client(settings.SUPABASE_URL, key)
        except Exception as e:
            logger.error("FAILED_TO_INIT_SUPABASE", context={"error": str(e)})
            raise DatabaseError("Supabase client initialization failed", cause=str(e)) from e

    def save_lead(self, lead_data: dict[str, Any]) -> Any:
        try:
            return (
                self.client.table("lead_conversations")
                .upsert(lead_data, on_conflict="customer_phone")
                .execute()
            )
        except Exception as e:
            logger.error(
                "SAVE_LEAD_FAILED",
                context={"phone": lead_data.get("customer_phone"), "error": str(e)},
            )
            raise DatabaseError("Failed to save lead", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_lead(self, phone: str) -> dict[str, Any] | None:
        try:
            result = (
                self.client.table("lead_conversations")
                .select("*")
                .eq("customer_phone", phone)
                .execute()
            )
            return dict(result.data[0]) if result.data else None  # type: ignore
        except Exception as e:
            logger.error("GET_LEAD_FAILED", context={"phone": phone, "error": str(e)})
            raise DatabaseError("Failed to retrieve lead", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_properties(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        try:
            result = (
                self.client.table("properties")
                .select("*")
                .ilike("description", f"%{query}%")
                .limit(limit)
                .execute()
            )
            return list(result.data)  # type: ignore
        except Exception as e:
            logger.error("GET_PROPERTIES_FAILED", context={"query": query, "error": str(e)})
            raise DatabaseError("Failed to retrieve properties", cause=str(e)) from e

    def update_lead_status(self, phone: str, status: str) -> None:
        try:
            self.client.table("lead_conversations").update({"status": status}).eq(
                "customer_phone", phone
            ).execute()
        except Exception as e:
            logger.error("UPDATE_LEAD_STATUS_FAILED", context={"phone": phone, "error": str(e)})
            raise DatabaseError("Failed to update lead status", cause=str(e)) from e

    def update_property(self, property_id: str, data: dict[str, Any]) -> None:
        try:
            self.client.table("properties").update(data).eq("id", property_id).execute()
        except Exception as e:
            logger.error("UPDATE_PROPERTY_FAILED", context={"id": property_id, "error": str(e)})
            raise DatabaseError("Failed to update property", cause=str(e)) from e
