from datetime import datetime, timedelta
from typing import Any

from domain.enums import LeadStatus
from domain.ports import CalendarPort, DatabasePort, DocumentPort, MessagingPort
from domain.services.logging import get_logger

logger = get_logger(__name__)


class JourneyManager:
    def __init__(
        self, db: DatabasePort, calendar: CalendarPort, doc_gen: DocumentPort, msg: MessagingPort
    ):
        self.db = db
        self.calendar = calendar
        self.doc_gen = doc_gen
        self.msg = msg

    def transition_to(
        self, phone: str, target_state: LeadStatus, context: dict[str, Any] | None = None
    ) -> None:
        logger.info("JOURNEY_TRANSITION", context={"phone": phone, "to": target_state})

        lead = self.db.get_lead(phone)
        if not lead:
            return

        # Execute side effects
        if target_state == LeadStatus.SCHEDULED and context is not None:
            self._handle_scheduling(lead, context)
        elif target_state == LeadStatus.CONTRACT_PENDING and context is not None:
            self._handle_contract_generation(lead, context)

        # Update DB
        self.db.update_lead(
            phone,
            {
                "status": target_state,
                "journey_state": target_state,
                "updated_at": datetime.now().isoformat(),
            },
        )

    def _handle_scheduling(self, lead: dict[str, Any], context: dict[str, Any]) -> None:
        start_time = context.get("start_time")
        if not start_time:
            return

        end_time = start_time + timedelta(hours=1)
        summary = f"Visita Immobile - {lead.get('customer_name')}"
        addr = str(lead.get("customer_phone") or "")
        attendees = [addr + "@wa.me"]  # Placeholder email logic

        link = self.calendar.create_event(summary, start_time, end_time, attendees)
        if link:
            phone = str(lead.get("customer_phone") or "")
            self.msg.send_message(
                phone,
                f"Perfetto! Visita confermata. Ecco il link al calendario: {link}",
            )

    def _handle_contract_generation(self, lead: dict[str, Any], context: dict[str, Any]) -> None:
        data = {
            "customer_name": lead.get("customer_name"),
            "customer_phone": lead.get("customer_phone"),
            "offered_price": context.get("offered_price"),
        }
        pdf_path = self.doc_gen.generate_pdf("proposta", data)
        if pdf_path:
            phone = str(lead.get("customer_phone") or "")
            self.msg.send_message(
                phone,
                "Ho generato la proposta d'acquisto per te. Una copia è stata salvata nel nostro sistema.",
            )

    def send_property_brochure(self, phone: str, property_data: dict[str, Any]) -> str:
        """
        Generates a professional brochure and sends it to the lead.
        Note: In production, the PDF should be uploaded to Supabase Storage
        and the public URL passed as media_url to WhatsApp.
        """
        logger.info(
            "SENDING_PROPERTY_BROCHURE",
            context={"phone": phone, "property": property_data.get("id")},
        )

        pdf_path = self.doc_gen.generate_pdf("brochure", property_data)

        if pdf_path:
            # For now, we send the text and inform that the PDF is ready
            # In a live environment with Supabase Storage, we would pass media_url
            msg_body = f"Ti ho preparato una scheda dettagliata per: {property_data.get('title')}. Spero ti sia utile!"

            # Placeholder for public URL (if we had storage implementation ready)
            # media_url = f"https://your-storage.com/{os.path.basename(pdf_path)}"
            media_url = None

            self.msg.send_message(phone, msg_body, media_url=media_url)

            # Record interest in DB
            lead_data = self.db.get_lead(phone)
            if lead_data:
                metadata = lead_data.get("metadata") or {}
                if not isinstance(metadata, dict):
                    metadata = {}

                interests = metadata.get("interested_property_ids", [])
                if not isinstance(interests, list):
                    interests = []

                prop_id = property_data.get("id")
                if prop_id and prop_id not in interests:
                    interests.append(prop_id)
                    metadata["interested_property_ids"] = interests
                    self.db.update_lead(phone, {"metadata": metadata})

            return pdf_path
        return ""
