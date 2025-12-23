import re
from datetime import UTC, datetime
from typing import Any, cast

from application.workflows.agents import create_lead_processing_graph
from domain.enums import LeadStatus
from domain.ports import (
    AIPort,
    CalendarPort,
    DatabasePort,
    MarketDataPort,
    MessagingPort,
    ScraperPort,
)
from domain.services.logging import get_logger

logger = get_logger(__name__)


class LeadScorer:
    SCORING_SIGNALS = {
        "visita": 30,
        "visitare": 30,
        "vedere": 25,
        "appuntamento": 30,
        "urgente": 25,
        "subito": 20,
        "oggi": 20,
        "domani": 15,
        "budget": 20,
        "contanti": 20,
        "mutuo": 15,
        "finanziamento": 15,
        "camera": 10,
        "bagno": 10,
        "terrazza": 15,
        "giardino": 15,
        "garage": 10,
        "piscina": 15,
        "trattabile": 5,
        "sconto": 5,
    }

    def calculate_score(self, text: str) -> int:
        score = 0
        message_lower = text.lower()
        for signal, points in self.SCORING_SIGNALS.items():
            if signal in message_lower:
                score += points
        return min(score, 100)


from application.services.journey_manager import JourneyManager


class LeadProcessor:
    def __init__(
        self,
        db: DatabasePort,
        ai: AIPort,
        msg: MessagingPort,
        scorer: LeadScorer,
        journey: JourneyManager | None = None,
        scraper: ScraperPort | None = None,
        market: MarketDataPort | None = None,
        calendar: CalendarPort | None = None,
    ):
        self.db = db
        self.ai = ai
        self.msg = msg
        self.scorer = scorer
        self.journey = journey
        self.scraper = scraper
        self.market = market
        self.calendar = calendar

        # The graph creation expects the ports
        self.graph = create_lead_processing_graph(db, ai, msg, journey, scraper, market, calendar)

    SIMILARITY_THRESHOLD = 0.78

    def process_lead(self, phone: str, name: str, query: str, postcode: str | None = None) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        logger.info("PROCESSING_LEAD", context={"phone": phone, "name": name})

        # Use LangGraph
        inputs = {"phone": phone, "user_input": query, "name": name, "postcode": postcode}

        try:
            result = self.graph.invoke(inputs)
            # Side effects (messaging, persistence) are handled by finalize_node in agents.py
            return cast(str, result.get("ai_response", ""))
        except Exception as e:
            logger.error("PROCESS_LEAD_GRAPH_FAILED", context={"phone": phone, "error": str(e)})
            return (
                "Mi dispiace, si è verificato un errore durante l'elaborazione della tua richiesta."
            )

    def takeover(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_TAKEOVER", context={"phone": phone})
        # self.db.update_lead_status(phone, "human_mode")
        self.db.save_lead(
            {
                "customer_phone": phone,
                "status": LeadStatus.HUMAN_MODE,
                "is_ai_active": False,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        )

    def resume(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_RESUME", context={"phone": phone})
        # self.db.update_lead_status(phone, "active")
        self.db.save_lead(
            {
                "customer_phone": phone,
                "status": LeadStatus.ACTIVE,
                "is_ai_active": True,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        )

    def update_lead_details(
        self,
        phone: str,
        name: str | None = None,
        budget: int | None = None,
        zones: list[str] | None = None,
        status: str | None = None,
        journey_state: str | None = None,
        scheduled_at: str | None = None,
    ) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("UPDATING_LEAD_DETAILS", context={"phone": phone})

        lead_data = {"customer_phone": phone}
        if name:
            lead_data["customer_name"] = name
        if budget:
            lead_data["budget_max"] = str(budget)
        if zones:
            lead_data["zones"] = ",".join(zones)
        if status:
            lead_data["status"] = status
        if journey_state:
            lead_data["journey_state"] = journey_state
        if scheduled_at:
            lead_data["scheduled_at"] = scheduled_at

        lead_data["updated_at"] = datetime.now(UTC).isoformat()
        self.db.save_lead(lead_data)

    def send_manual_message(self, phone: str, message: str, skip_history: bool = False) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info(
            "SENDING_MANUAL_MESSAGE", context={"phone": phone, "skip_history": skip_history}
        )
        # 1. Send via messaging port
        self.msg.send_message(phone, message)

        # 2. Update history (optional, can be done in background)
        if not skip_history:
            try:
                self.add_message_history(
                    phone, "assistant", message, metadata={"by": "human_agent"}
                )
            except Exception as e:
                logger.error(
                    "MANUAL_MESSAGE_HISTORY_FAILED", context={"phone": phone, "error": str(e)}
                )

    def add_message_history(
        self, phone: str, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        lead = self.db.get_lead(phone)
        if not lead:
            return

        messages: list[dict[str, Any]] = lead.get("messages") or []
        new_msg: dict[str, Any] = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if metadata:
            new_msg["metadata"] = metadata

        messages.append(new_msg)

        lead_data = {
            "customer_phone": phone,
            "messages": messages,
            "last_message": content,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.db.save_lead(lead_data)

    def send_brochure_if_interested(self, phone: str, query: str) -> None:
        """
        If the lead is asking for details, fetch the best matching property
        and send a professional PDF brochure.
        """
        if not self.journey:
            return

        # Simple heuristic: find properties if "scheda", "dettagli", or "foto" are mentioned
        keywords = ["scheda", "dettagli", "informazioni", "foto", "brochure", "info"]
        if not any(k in query.lower() for k in keywords):
            return

        logger.info("AUTO_BROCHURE_TRIGGERED", context={"phone": phone})

        # 1. Fetch relevant properties (using the query or lead context)
        properties = self.db.get_properties(query, limit=1)
        if properties:
            self.journey.send_property_brochure(phone, properties[0])
            logger.info(
                "BROCHURE_SENT_SUCCESS",
                context={"phone": phone, "property": properties[0].get("id")},
            )

    def process_incoming_message(
        self,
        phone: str,
        text: str,
        source: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        if phone.startswith("whatsapp:"):
            phone = phone.replace("whatsapp:", "")

        logger.info("INCOMING_MESSAGE", context={"phone": phone, "text": text})

        # Logic delegated to LangGraph
        # Graph handles: ingest, intent, preferences, sentiment, retrieval, generation, and finalize (persistence)
        inputs: dict[str, Any] = {"phone": phone, "user_input": text}
        if source:
            inputs["source"] = source
        if context:
            inputs["context_data"] = context

        try:
            result = self.graph.invoke(inputs)
            # 3. Handle Side Effects (like sending brochures)
            self.send_brochure_if_interested(phone, text)
            return str(result.get("ai_response", ""))
        except Exception as e:
            logger.error("GRAPH_INVOCATION_FAILED", context={"phone": phone, "error": str(e)})
            return ""
