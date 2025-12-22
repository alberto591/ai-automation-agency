import re
from datetime import UTC, datetime
from typing import Any

from config.settings import settings
from domain.enums import LeadStatus
from domain.ports import AIPort, DatabasePort, MessagingPort
from infrastructure.logging import get_logger

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
        journey: JourneyManager = None
    ):
        self.db = db
        self.ai = ai
        self.msg = msg
        self.scorer = scorer
        self.journey = journey

    SIMILARITY_THRESHOLD = 0.78

    def process_lead(self, phone: str, name: str, query: str, postcode: str | None = None) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        logger.info("PROCESSING_LEAD", context={"phone": phone, "name": name})

        # 1. Scoring & Extraction
        score = self.scorer.calculate_score(query)
        budget = self._extract_budget(query)

        # 2. Get Grounded Properties (Hybrid Search + Credulity Check ADR-004)
        valid_properties, status_msg = self._get_grounded_properties(query, budget)
        details = self._format_properties(valid_properties)

        # 3. AI Response
        msg_body = f"Identity: Anzevino AI. Goal: Respond professionaly to {name} about {query}. {status_msg}"
        prompt = f"{msg_body}\nAvailable Properties Data: {details}"
        ai_response = self.ai.generate_response(prompt)

        # 4. Notify
        self.msg.send_message(phone, ai_response)

        # 5. Persist
        # Note: We save the lead first if it doesn't exist, then add the messages
        lead_data = {
            "customer_name": name,
            "customer_phone": phone,
            "score": score,
            "budget_max": budget,
            "postcode": postcode,
            "status": LeadStatus.HOT if score >= 50 else LeadStatus.ACTIVE,
            "is_ai_active": True,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.db.save_lead(lead_data)

        # 6. History
        self.add_message_history(phone, "user", query)
        self.add_message_history(phone, "assistant", ai_response)

        return ai_response

    def takeover(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_TAKEOVER", context={"phone": phone})
        # self.db.update_lead_status(phone, "human_mode")
        self.db.save_lead({
            "customer_phone": phone,
            "status": LeadStatus.HUMAN_MODE,
            "is_ai_active": False,
            "updated_at": datetime.now(UTC).isoformat(),
        })

    def resume(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_RESUME", context={"phone": phone})
        # self.db.update_lead_status(phone, "active")
        self.db.save_lead({
            "customer_phone": phone,
            "status": LeadStatus.ACTIVE,
            "is_ai_active": True,
            "updated_at": datetime.now(UTC).isoformat(),
        })

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
            lead_data["budget_max"] = budget
        if zones:
            lead_data["zones"] = zones
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
        logger.info("SENDING_MANUAL_MESSAGE", context={"phone": phone, "skip_history": skip_history})
        # 1. Send via messaging port
        self.msg.send_message(phone, message)

        # 2. Update history (optional, can be done in background)
        if not skip_history:
            try:
                self.add_message_history(phone, "assistant", message, metadata={"by": "human_agent"})
            except Exception as e:
                logger.error(
                    "MANUAL_MESSAGE_HISTORY_FAILED",
                    context={"phone": phone, "error": str(e)}
                )

    def add_message_history(
        self, phone: str, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        lead = self.db.get_lead(phone)
        if not lead:
            return

        messages = lead.get("messages") or []
        new_msg = {
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

    def process_incoming_message(self, phone: str, text: str) -> None:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        if phone.startswith("whatsapp:"):
            phone = phone.replace("whatsapp:", "")
            
        logger.info("INCOMING_MESSAGE", context={"phone": phone, "text": text})

        # 1. Check/Get Lead
        lead = self.db.get_lead(phone)
        if not lead:
             logger.info("NEW_LEAD_DETECTED", context={"phone": phone})
             # Create basic lead
             lead_data = {
                "customer_phone": phone,
                "status": LeadStatus.ACTIVE,
                "journey_state": LeadStatus.ACTIVE,
                "is_ai_active": True,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
             }
             self.db.save_lead(lead_data)
             lead = self.db.get_lead(phone) or lead_data

        # 2. Save User Message
        self.add_message_history(phone, "user", text)
        
        # 3. Check AI Status
        if not lead.get("is_ai_active", True):
            logger.info("AI_SKIPPED_HUMAN_MODE", context={"phone": phone})
            return

        # 4. Intent Detection & Journey State (ADR-027)
        current_state = lead.get("journey_state") or LeadStatus.ACTIVE
        input_lower = text.lower()
        
        # Detection regex
        visit_intent = re.search(r"visit|veder|appuntament", input_lower)
        purchase_intent = re.search(r"compr|acquist|propost", input_lower)

        if self.journey and visit_intent:
            if current_state != LeadStatus.APPOINTMENT_REQUESTED:
                self.journey.transition_to(phone, LeadStatus.APPOINTMENT_REQUESTED)
                current_state = LeadStatus.APPOINTMENT_REQUESTED
        elif self.journey and purchase_intent:
             # For simulation/demo: auto-escalate to qualified if they talk about buying
             if current_state == LeadStatus.ACTIVE:
                 self.journey.transition_to(phone, LeadStatus.QUALIFIED)
                 current_state = LeadStatus.QUALIFIED

        # 5. History Context (ADR-023)
        history = lead.get("messages", [])
        # Truncate to sliding window
        truncated_history = history[-settings.MAX_CONTEXT_MESSAGES:]
        history_text = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in truncated_history])

        # 6. Semantic Cache Check (ADR-019)
        embedding = self.ai.get_embedding(text)
        cached_response = self.db.get_cached_response(embedding)
        if cached_response:
             logger.info("SEMANTIC_CACHE_HIT", context={"phone": phone})
             self.msg.send_message(phone, cached_response)
             self.add_message_history(phone, "assistant", cached_response, metadata={"by": "ai", "cache": "hit"})
             return

        # 7. Generate Grounded AI Response (ADR-004 + ADR-027 Context)
        valid_properties, status_msg = self._get_grounded_properties(text, lead.get("budget_max"), embedding=embedding)
        details = self._format_properties(valid_properties)
        
        nm = lead.get("customer_name", "Cliente")
        prompt = (
            f"Identity: Anzevino AI. Goal: Respond helpfully to {nm}.\n"
            f"Current Journey Stage: {current_state}\n"
            f"Context History:\n{history_text}\n"
            f"User Latest: {text}. {status_msg}"
            f"\nAvailable Properties Data: {details}"
            "\nKeep it native for WhatsApp (short, friendly)."
        )
        
        try:
            ai_response = self.ai.generate_response(prompt)
            
            # 8. Send & Save
            self.msg.send_message(phone, ai_response)
            self.add_message_history(phone, "assistant", ai_response, metadata={"by": "ai", "cache": "miss"})
            
            # 9. Update Cache (ADR-019)
            self.db.save_to_cache(text, embedding, ai_response)
        except Exception as e:
            logger.error("AI_RESPONSE_FAILED", context={"error": str(e)})

    def _get_grounded_properties(
        self, query: str, budget: int | None = None, embedding: list[float] | None = None
    ) -> tuple[list[dict[str, Any]], str]:
        # 1. Fetch
        if not embedding:
            embedding = self.ai.get_embedding(query)
        filters = {"max_price": budget} if budget else {}
        properties = self.db.get_properties(query, embedding=embedding, filters=filters)
        
        # 2. Filter (ADR-004)
        valid_properties = [p for p in properties if p.get("similarity", 0) >= self.SIMILARITY_THRESHOLD]
        
        # 3. Feedback for AI
        status_msg = ""
        if not valid_properties:
             status_msg = "IMPORTANT: No exact matches found above 0.78 threshold. You MUST admit that you couldn't find a perfect match right now, but you are available to help."
        
        return valid_properties, status_msg

    def _extract_budget(self, text: str) -> int | None:
        budget_matches = re.findall(
            r"(\d+(?:\.\d+)?)[\s]?(m(?:ln|ilioni)?)|(\d+)[\s]?k|(\d{5,})", text.lower()
        )
        if budget_matches:
            found_budgets = []
            for m_val, _m_unit, k_val, raw_val in budget_matches:
                if m_val:
                    val = int(float(m_val) * 1000000)
                elif k_val:
                    val = int(k_val) * 1000
                else:
                    val = int(raw_val)
                found_budgets.append(val)
            return max(found_budgets)
        return None

    def _format_properties(self, properties: list[dict[str, Any]]) -> str:
        if not properties:
            return "Nessun immobile trovato."
        res = "Opzioni trovate:\n"
        for p in properties:
            res += f"- {p.get('title')}: €{p.get('price'):,}\n"
        return res
