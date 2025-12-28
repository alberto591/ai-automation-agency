from datetime import UTC, datetime
from typing import Any, cast

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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def save_lead(self, lead_data: dict[str, Any]) -> None:
        try:
            # 1. Separate Lead Profile vs Messages
            # We must COPY lead_data to avoid modifying it in place which might affect caller
            lead_profile = lead_data.copy()
            messages = lead_profile.pop("messages", [])

            # Remove keys that shouldn't be in LEADS table if present
            lead_profile.pop("last_message", None)  # Computed or stored elsewhere usually

            # 2. Upsert Lead Profile
            # Ensure metadata is handled if provided
            if "metadata" in lead_profile and isinstance(lead_profile["metadata"], (dict, list)):
                # metadata is JSONB, serializable by supabase-py
                pass

            res = (
                self.client.table("leads")
                .upsert(lead_profile, on_conflict="customer_phone")
                .execute()
            )
            if not res.data:
                raise DatabaseError("Failed to save lead profile")

            data = cast(list[dict[str, Any]], res.data)
            lead_id = data[0]["id"]

            # 3. Insert Messages
            # Only if we have explicit new messages structure.
            # Domain often sends [{"role": "user", "content": ...}]
            if messages:
                for msg in messages:
                    # Check if message already likely exists?
                    # For MVP Phase 2, we might just append if it's a new flow.
                    # But simple append is safest for now.
                    msg_data = {
                        "lead_id": lead_id,
                        "role": msg.get("role"),
                        "content": msg.get("content"),
                        "created_at": msg.get("timestamp") or datetime.now(UTC).isoformat(),
                    }
                    self.client.table("messages").insert(msg_data).execute()

        except Exception as e:
            logger.error(
                "SAVE_LEAD_FAILED",
                context={"phone": lead_data.get("customer_phone"), "error": str(e)},
            )
            raise DatabaseError("Failed to save lead", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_lead(self, phone: str) -> dict[str, Any] | None:
        try:
            # 1. Fetch Lead
            res_lead = (
                self.client.table("leads")
                .select("*")
                .eq("customer_phone", phone)
                .limit(1)
                .execute()
            )
            if not res_lead.data:
                return None

            data = cast(list[dict[str, Any]], res_lead.data)
            lead = data[0]

            # 2. Fetch Messages
            res_msgs = (
                self.client.table("messages")
                .select("*")
                .eq("lead_id", lead["id"])
                .order("created_at")
                .execute()
            )

            # 3. Assemble
            lead["messages"] = res_msgs.data if res_msgs.data else []
            return lead

        except Exception as e:
            logger.error("GET_LEAD_FAILED", context={"phone": phone, "error": str(e)})
            raise DatabaseError("Failed to retrieve lead", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_properties(
        self,
        query: str,
        limit: int = 3,
        use_mock_table: bool = False,
        embedding: list[float] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            table = "mock_properties" if use_mock_table else "properties"

            # Hybrid Search if embedding is provided
            if embedding:
                rpc_name = "match_mock_properties" if use_mock_table else "match_properties"
                # Prepare filters for RPC
                rpc_params = {
                    "p_query_embedding": embedding,
                    "match_threshold": 0.5,  # Default threshold
                    "match_count": limit,
                }
                if filters:
                    if "min_price" in filters:
                        rpc_params["min_price"] = filters["min_price"]
                    if "max_price" in filters:
                        rpc_params["max_price"] = filters["max_price"]

                result = self.client.rpc(rpc_name, rpc_params).execute()
                data = cast(list[dict[str, Any]], result.data)
                return data if data else []

            # Fallback to ilike (Legacy)
            result = cast(
                Any,
                (
                    self.client.table(table)
                    .select("*")
                    .ilike("description", f"%{query}%")
                    .limit(limit)
                    .execute()
                ),
            )
            data = cast(list[dict[str, Any]], result.data)
            return data if data else []
        except Exception as e:
            logger.error("GET_PROPERTIES_FAILED", context={"query": query, "error": str(e)})
            raise DatabaseError("Failed to retrieve properties", cause=str(e)) from e

    def update_lead(self, phone: str, data: dict[str, Any]) -> None:
        try:
            self.client.table("leads").update(data).eq("customer_phone", phone).execute()
        except Exception as e:
            logger.error("UPDATE_LEAD_FAILED", context={"phone": phone, "error": str(e)})
            raise DatabaseError("Failed to update lead", cause=str(e)) from e

    def update_lead_status(self, phone: str, status: str) -> None:
        self.update_lead(phone, {"status": status})

    def update_property(self, property_id: str, data: dict[str, Any]) -> None:
        try:
            self.client.table("properties").update(data).eq("id", property_id).execute()
        except Exception as e:
            logger.error("UPDATE_PROPERTY_FAILED", context={"id": property_id, "error": str(e)})
            raise DatabaseError("Failed to update property", cause=str(e)) from e

    def get_cached_response(self, embedding: list[float], threshold: float = 0.9) -> str | None:
        try:
            res = self.client.rpc(
                "match_cache",
                {"p_query_embedding": embedding, "match_threshold": threshold, "match_count": 1},
            ).execute()
            data = cast(list[dict[str, Any]], res.data)
            if data:
                return str(data[0]["response_text"])
            return None
        except Exception as e:
            logger.error("GET_CACHE_FAILED", context={"error": str(e)})
            return None

    def save_to_cache(self, query: str, embedding: list[float], response: str) -> None:
        try:
            self.client.table("semantic_cache").upsert(
                {
                    "query_text": query,
                    "query_embedding": embedding,
                    "response_text": response,
                    "updated_at": datetime.now(UTC).isoformat(),
                },
                on_conflict="query_text",
            ).execute()
        except Exception as e:
            logger.error("SAVE_CACHE_FAILED", context={"error": str(e)})

    def get_market_stats(self, zone: str) -> dict[str, Any]:
        """
        Fetches competitive market stats for a given zone.
        """
        try:
            # We fetch all listings in the zone to calculate accurate stats
            # In a larger DB, we'd use a postgres function (RPC) for this.
            res = (
                self.client.table("market_data")
                .select("price, sqm, price_per_mq")
                .ilike("zone", f"%{zone}%")
                .execute()
            )
            data = cast(list[dict[str, Any]], res.data)

            if not data:
                return {}

            total_listings = len(data)
            prices_per_mq = [d["price_per_mq"] for d in data if d.get("price_per_mq")]

            avg_price_mq = sum(prices_per_mq) / len(prices_per_mq) if prices_per_mq else 0

            return {
                "zone": zone,
                "avg_price_sqm": round(avg_price_mq, 2),
                "listings_count": total_listings,
                "sample_size": len(prices_per_mq),
            }
        except Exception as e:
            logger.error("GET_MARKET_STATS_FAILED", context={"zone": zone, "error": str(e)})
            return {}
