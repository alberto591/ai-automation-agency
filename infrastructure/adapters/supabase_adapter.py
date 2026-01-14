from datetime import UTC, datetime
from typing import Any, cast

from supabase import create_client
from tenacity import retry, stop_after_attempt, wait_exponential

from domain.errors import DatabaseError
from domain.ports import DatabasePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class SupabaseAdapter(DatabasePort):
    def __init__(self) -> None:
        from config.settings import settings

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
            # We must COPY lead_data to avoid modifying it in place
            lead_profile = lead_data.copy()
            messages = lead_profile.pop("messages", [])

            # Remove keys that shouldn't be in LEADS table if present
            lead_profile.pop("last_message", None)

            # 2. Upsert Lead Profile
            res = (
                self.client.table("leads")
                .upsert(lead_profile, on_conflict="customer_phone")
                .execute()
            )
            if not res.data:
                raise DatabaseError("Failed to save lead profile")

            data = cast(list[dict[str, Any]], res.data)
            lead_id = data[0]["id"]

            # 3. Handle Messages (if provided, but we prefer save_message now)
            # Legacy support: if messages are passed, save them one by one if they are new
            # However, for pure cleanup, we might want to encourage save_message.
            if messages:
                for msg in messages:
                    # If message doesn't have an ID, it's likely new
                    if not msg.get("id"):
                        self.save_message(lead_id, msg)

        except Exception as e:
            logger.error(
                "SAVE_LEAD_FAILED",
                context={"phone": lead_data.get("customer_phone"), "error": str(e)},
            )
            raise DatabaseError("Failed to save lead", cause=str(e)) from e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def save_message(self, lead_id: str, msg: dict[str, Any]) -> None:
        try:
            msg_data = {
                "lead_id": lead_id,
                "role": msg.get("role"),
                "content": msg.get("content"),
                "sid": msg.get("sid"),
                "status": msg.get("status", "sent"),
                "media_url": msg.get("media_url"),
                "channel": msg.get("channel", "whatsapp"),
                "created_at": msg.get("timestamp")
                or msg.get("created_at")
                or datetime.now(UTC).isoformat(),
                "metadata": msg.get("metadata", {}),
            }
            self.client.table("messages").insert(msg_data).execute()
        except Exception as e:
            logger.error("SAVE_MESSAGE_FAILED", context={"lead_id": lead_id, "error": str(e)})
            raise DatabaseError("Failed to save message", cause=str(e)) from e

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

    def update_message_status(self, sid: str, status: str) -> None:
        try:
            self.client.table("messages").update({"status": status}).eq("sid", sid).execute()
            logger.info("MESSAGE_STATUS_UPDATED", context={"sid": sid, "status": status})
        except Exception as e:
            logger.error("UPDATE_MESSAGE_STATUS_FAILED", context={"sid": sid, "error": str(e)})
            raise DatabaseError("Failed to update message status", cause=str(e)) from e

    def save_payment_schedule(self, schedule: dict[str, Any]) -> str:
        try:
            # Upsert schedule
            res = self.client.table("payment_schedules").upsert(schedule).execute()

            if not res.data:
                raise DatabaseError("Failed to save payment schedule")

            data = cast(list[dict[str, Any]], res.data)
            return str(data[0]["id"])
        except Exception as e:
            logger.error("SAVE_PAYMENT_FAILED", context={"error": str(e)})
            raise DatabaseError("Failed to save payment schedule", cause=str(e)) from e

    def get_due_payments(self, date_limit: datetime) -> list[dict[str, Any]]:
        try:
            # Fetch payments due <= date_limit, join with leads to get phone
            res = (
                self.client.table("payment_schedules")
                .select("*, leads(customer_phone)")
                .lte("due_date", date_limit.isoformat())
                .in_(
                    "status", ["active", "paused"]
                )  # Include paused? Maybe not. defaulting to active.
                .execute()
            )

            data = cast(list[dict[str, Any]], res.data)
            results = []
            for item in data:
                # Flatten lead phone
                lead = item.get("leads") or {}
                # Supabase join returns dict or list depending on relation, usually dict for 1:1 or N:1
                phone = lead.get("customer_phone")

                payment = item.copy()
                payment["lead_phone"] = phone
                if "leads" in payment:
                    del payment["leads"]
                results.append(payment)

            return results
        except Exception as e:
            logger.error("GET_DUE_PAYMENTS_FAILED", context={"error": str(e)})
            raise DatabaseError("Failed to fetch due payments", cause=str(e)) from e

    def get_active_agents(self) -> list[dict[str, Any]]:
        try:
            res = (
                self.client.table("users")
                .select("id, email, full_name, role, zones")
                .eq("is_active", True)
                .eq("role", "agent")
                .execute()
            )
            return cast(list[dict[str, Any]], res.data)
        except Exception as e:
            logger.error("GET_ACTIVE_AGENTS_FAILED", context={"error": str(e)})
            # Return empty list instead of crashing, to allow fail-open
            return []

    def assign_lead_to_agent(self, lead_id: str, agent_id: str) -> None:
        try:
            self.client.table("leads").update({"assigned_agent_id": agent_id}).eq(
                "id", lead_id
            ).execute()
            logger.info("LEAD_ASSIGNED", context={"lead_id": lead_id, "agent_id": agent_id})
        except Exception as e:
            logger.error(
                "LEAD_ASSIGNMENT_FAILED",
                context={"lead_id": lead_id, "agent_id": agent_id, "error": str(e)},
            )
            raise DatabaseError("Failed to assign lead", cause=str(e)) from e

    def save_appointment(self, appointment_data: dict[str, Any]) -> str:
        try:
            res = self.client.table("appointments").insert(appointment_data).execute()
            if not res.data:
                raise DatabaseError("Failed to save appointment")
            # mypy thinks res.data is JSON? but it is a list of dicts here
            data: list[dict[str, Any]] = res.data
            return str(data[0]["id"])
        except Exception as e:
            logger.error("SAVE_APPOINTMENT_FAILED", context={"error": str(e)})
            raise DatabaseError("Failed to save appointment", cause=str(e)) from e

    def update_appointment_status(self, booking_id: str, status: str) -> None:
        try:
            self.client.table("appointments").update({"status": status}).eq(
                "external_booking_id", booking_id
            ).execute()
            logger.info(
                "APPOINTMENT_STATUS_UPDATED", context={"booking_id": booking_id, "status": status}
            )
        except Exception as e:
            logger.error(
                "UPDATE_APPOINTMENT_STATUS_FAILED",
                context={"booking_id": booking_id, "error": str(e)},
            )
            raise DatabaseError("Failed to update appointment status", cause=str(e)) from e

    def get_appointment_by_external_id(self, booking_id: str) -> dict[str, Any] | None:
        try:
            res = (
                self.client.table("appointments")
                .select("*")
                .eq("external_booking_id", booking_id)
                .limit(1)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(
                "GET_APPOINTMENT_FAILED",
                context={"booking_id": booking_id, "error": str(e)},
            )
            raise DatabaseError("Failed to retrieve appointment", cause=str(e)) from e
