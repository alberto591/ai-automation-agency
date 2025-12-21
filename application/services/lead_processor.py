import re
from datetime import UTC, datetime
from typing import Any

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


class LeadProcessor:
    def __init__(self, db: DatabasePort, ai: AIPort, msg: MessagingPort, scorer: LeadScorer):
        self.db = db
        self.ai = ai
        self.msg = msg
        self.scorer = scorer

    def process_lead(self, phone: str, name: str, query: str, postcode: str | None = None) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        logger.info("PROCESSING_LEAD", context={"phone": phone, "name": name})

        # 1. Scoring & Extraction
        score = self.scorer.calculate_score(query)
        budget = self._extract_budget(query)

        # 2. Get Properties
        properties = self.db.get_properties(query)
        details = self._format_properties(properties)

        # 3. AI Response
        msg_body = f"Identity: Anzevino AI. Goal: Respond professionaly to {name} about {query}."
        prompt = f"{msg_body} Data: {details}"
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
            "status": "HOT" if score >= 50 else "Active",  # noqa: PLR2004
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.db.save_lead(lead_data)

        # 6. History
        self._add_message(phone, "user", query)
        self._add_message(phone, "assistant", ai_response)

        return ai_response

    def takeover(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_TAKEOVER", context={"phone": phone})
        self.db.update_lead_status(phone, "human_mode")

    def resume(self, phone: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("LEAD_RESUME", context={"phone": phone})
        self.db.update_lead_status(phone, "active")

    def update_lead_details(
        self,
        phone: str,
        name: str | None = None,
        budget: int | None = None,
        zones: list[str] | None = None,
        status: str | None = None,
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
        
        lead_data["updated_at"] = datetime.now(UTC).isoformat()
        self.db.save_lead(lead_data)

    def send_manual_message(self, phone: str, message: str) -> None:
        phone = re.sub(r"\s+", "", phone)
        logger.info("SENDING_MANUAL_MESSAGE", context={"phone": phone})
        # 1. Send via messaging port
        self.msg.send_message(phone, message)

        # 2. Update history
        self._add_message(phone, "assistant", message, metadata={"by": "human_agent"})

    def _add_message(
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
