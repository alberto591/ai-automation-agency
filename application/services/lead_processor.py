import re
from datetime import UTC, datetime
from typing import Any, cast

from domain.enums import LeadStatus
from domain.ports import (
    AIPort,
    CalendarPort,
    DatabasePort,
    EmailPort,
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
        email: EmailPort | None = None,
        validation: Any = None,
        routing: Any = None,
    ):
        self.db = db
        from application.workflows.agents import create_lead_processing_graph

        self.ai = ai
        self.msg = msg
        self.scorer = scorer
        self.journey = journey
        self.scraper = scraper
        self.market = market
        self.calendar = calendar
        self.email = email
        self.validation = validation
        self.routing = routing

        # The graph creation expects the ports
        self.graph = create_lead_processing_graph(
            db, ai, msg, journey, scraper, market, calendar, validation
        )

    SIMILARITY_THRESHOLD = 0.78

    def process_lead(
        self,
        phone: str,
        name: str,
        query: str,
        postcode: str | None = None,
        language: str | None = None,
    ) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        logger.info("PROCESSING_LEAD", context={"phone": phone, "name": name, "language": language})

        # Use LangGraph - pass language directly, not as preferred_language
        inputs = {
            "phone": phone,
            "user_input": query,
            "name": name,
            "postcode": postcode,
            "language": language,
            "context_data": {},  # Ensure fresh context
            "history": [], # Ensure fresh history
            "history_text": "", 
            "source": "WHATSAPP", # Default, will be updated by ingest
        }

        try:
            result = self.graph.invoke(inputs)

            # Routing: Assign to agent if configured
            if self.routing:
                try:
                    lead_data = self.db.get_lead(phone)
                    if lead_data and not lead_data.get("assigned_agent_id"):
                        from domain.models import Lead

                        lead_obj = Lead(
                            id=lead_data["id"],
                            phone=phone,
                            postcode=postcode or lead_data.get("postcode"),
                        )
                        agent_id = self.routing.assign_lead(lead_obj)
                        if agent_id:
                            self.db.assign_lead_to_agent(lead_data["id"], agent_id)
                except Exception as ex:
                    logger.error("ROUTING_STEP_FAILED", context={"phone": phone, "error": str(ex)})

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

    def send_manual_message(self, phone: str, message: str, skip_history: bool = False) -> str:
        phone = re.sub(r"\s+", "", phone)
        logger.info(
            "SENDING_MANUAL_MESSAGE", context={"phone": phone, "skip_history": skip_history}
        )
        # 1. Send via messaging port
        sid = self.msg.send_message(phone, message)

        # 2. Update history (optional, can be done in background)
        if not skip_history:
            try:
                self.add_message_history(
                    phone,
                    "assistant",
                    message,
                    sid=sid,
                    status="sent",
                    metadata={"by": "human_agent"},
                )
            except Exception as e:
                logger.error(
                    "MANUAL_MESSAGE_HISTORY_FAILED", context={"phone": phone, "error": str(e)}
                )
        return sid

    def add_message_history(
        self,
        phone: str,
        role: str,
        content: str,
        sid: str | None = None,
        status: str | None = None,
        media_url: str | None = None,
        channel: str = "whatsapp",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        lead = self.db.get_lead(phone)
        if not lead:
            return

        new_msg: dict[str, Any] = {
            "role": role,
            "content": content,
            "sid": sid,
            "status": status or "sent",
            "media_url": media_url,
            "channel": channel,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if metadata:
            new_msg["metadata"] = metadata

        self.db.save_message(lead["id"], new_msg)

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

    def process_appraisal_signal(
        self, phone: str, estimated_value: float, comparables_count: int
    ) -> None:
        """
        Updates lead score and tags based on appraisal results.
        High value properties (>500k) get boosted scores and tags.
        """
        phone = re.sub(r"\s+", "", phone)
        logger.info(
            "PROCESSING_APPRAISAL_SIGNAL", context={"phone": phone, "value": estimated_value}
        )

        # Calculate score boost
        score_boost = 0
        is_high_value = estimated_value > 500000

        if is_high_value:
            score_boost += 25  # Immediate WARM/HOT status potential
        if estimated_value > 1000000:
            score_boost += 15  # Luxury bonus

        tags = []
        if is_high_value:
            tags.append("HIGH_VALUE")
        if estimated_value > 1000000:
            tags.append("LUXURY")

        # Update lead
        try:
            lead = self.db.get_lead(phone)
            if lead:
                current_score = lead.get("lead_score_raw", 0)
                new_score = current_score + score_boost

                # Update tags
                current_tags = lead.get("tags", []) or []
                updated_tags = list(set(current_tags + tags))

                self.db.save_lead(
                    {
                        "customer_phone": phone,
                        "lead_score_raw": new_score,
                        "tags": updated_tags,
                        "estimated_property_value": estimated_value,
                        "updated_at": datetime.now(UTC).isoformat(),
                    }
                )
                logger.info(
                    "LEAD_SCORED_FROM_APPRAISAL", context={"phone": phone, "new_score": new_score}
                )
        except Exception as e:
            logger.error("APPRAISAL_SIGNAL_FAILED", context={"phone": phone, "error": str(e)})

    def process_incoming_message(
        self,
        phone: str,
        text: str,
        source: str | None = None,
        media_url: str | None = None,
        channel: str = "whatsapp",
        context: dict[str, Any] | None = None,
    ) -> str:
        # Clean phone
        phone = re.sub(r"\s+", "", phone)
        if phone.startswith("whatsapp:"):
            phone = phone.replace("whatsapp:", "")

        logger.info("INCOMING_MESSAGE", context={"phone": phone, "text": text, "media": media_url})

        # Logic delegated to LangGraph
        # Graph handles: ingest, intent, preferences, sentiment, retrieval, generation, and finalize (persistence)
        inputs: dict[str, Any] = {"phone": phone, "user_input": text}
        if source:
            inputs["source"] = source
        if context:
            inputs["context_data"] = context

        try:
            # Pre-save message to history if it has media, even before graph runs
            # This ensures it shows up in dashboard immediately
            if media_url:
                self.add_message_history(
                    phone, "user", text or "Media received", media_url=media_url, channel=channel
                )

            result = self.graph.invoke(inputs)
            # 3. Handle Side Effects (like sending brochures)
            self.send_brochure_if_interested(phone, text)
            return str(result.get("ai_response", ""))
        except Exception as e:
            logger.error("GRAPH_INVOCATION_FAILED", context={"phone": phone, "error": str(e)})
            return ""

    def summarize_lead(self, phone: str) -> dict[str, Any]:
        """
        Generates a summary of the conversation history for a given lead.
        """
        phone = re.sub(r"\s+", "", phone)
        lead = self.db.get_lead(phone)
        if not lead or not lead.get("messages"):
            return {
                "summary": "No active conversation found.",
                "sentiment": "NEUTRAL",
                "suggested_action": "Initiate contact",
            }

        # Format history
        history_text = ""
        for msg in lead["messages"]:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        prompt = (
            f"Summarize the following conversation in Italian. "
            f"Identify the client's sentiment (POSITIVE, NEUTRAL, NEGATIVE) and suggest the next best action.\n\n"
            f"Conversation:\n{history_text}\n\n"
            f"Output JSON format: {{'summary': '...', 'sentiment': '...', 'suggested_action': '...'}}"
        )

        try:
            response = self.ai.generate_response(prompt)
            # Try to parse JSON from AI response if it's raw text
            # using a robust parser or expecting the dict if the adapter handles it.
            # For now, let's assume text and we might need to parse it or return it.
            # To be safe, we'll return the raw text if parsing fails, but wrapping in the struct.

            # Simple heuristic cleaning if AI returns markdown json
            clean_res = response.replace("```json", "").replace("```", "").strip()

            import json

            try:
                return cast(dict[str, Any], json.loads(clean_res))
            except json.JSONDecodeError:
                return {
                    "summary": response,
                    "sentiment": "UNKNOWN",
                    "suggested_action": "Review conversation",
                }

        except Exception as e:
            logger.error("SUMMARIZATION_FAILED", context={"phone": phone, "error": str(e)})
            return {
                "summary": "Failed to generate summary.",
                "sentiment": "UNKNOWN",
                "suggested_action": "Check logs",
            }

    def process_new_emails(self) -> int:
        """
        Fetches unread emails and processes them as leads.
        Returns the number of emails processed.
        """
        if not self.email:
            logger.warning("EMAIL_PROCESSING_SKIPPED_NO_ADAPTER")
            return 0

        try:
            emails = self.email.fetch_unread_emails()
            count = 0

            for email_data in emails:
                subject = email_data.get("subject", "No Subject")
                body = email_data.get("body", "")

                # Basic email parsing to extract phone if possible, else use email as identifier key
                # For now, we'll try to find a phone number in the body, otherwise use email
                # Note: Our generic process_lead currently expects a phone.
                # We might need to handle email-only leads soon, but for MVP let's look for phone or use a placeholder.

                # Heuristic: Find first phone-like string
                phone_match = re.search(r"(\+39|3[0-9]{2})\s?([\d\s]{6,8})", body + " " + subject)
                if phone_match:
                    phone = phone_match.group(0).replace(" ", "")
                else:
                    # Fallback: create a pseudo-phone from email for now or log warning
                    # Ideally we update the system to handle email primary keys.
                    # For this pass, we'll just log and skip if no phone found to avoid junk data
                    logger.info("EMAIL_SKIPPED_NO_PHONE", context={"subject": subject})
                    continue

                logger.info("PROCESSING_EMAIL_LEAD", context={"phone": phone, "subject": subject})

                # Construct message text
                text = f"[EMAIL] Subject: {subject}\n\n{body[:1000]}"

                self.process_incoming_message(phone, text, source="email", channel="email")

                # Mark as processed
                if "id" in email_data:
                    self.email.mark_as_processed(email_data["id"])

                count += 1

            return count

        except Exception as e:
            logger.error("EMAIL_POLLING_FAILED", context={"error": str(e)})
            return 0
