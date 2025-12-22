from datetime import datetime, timedelta
from typing import Any

from domain.enums import LeadStatus
from domain.ports import CalendarPort, DatabasePort, DocumentPort, MessagingPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class JourneyManager:
    def __init__(
        self, 
        db: DatabasePort, 
        calendar: CalendarPort, 
        doc_gen: DocumentPort,
        msg: MessagingPort
    ):
        self.db = db
        self.calendar = calendar
        self.doc_gen = doc_gen
        self.msg = msg

    def transition_to(self, phone: str, target_state: LeadStatus, context: dict[str, Any] = None) -> None:
        logger.info("JOURNEY_TRANSITION", context={"phone": phone, "to": target_state})
        
        lead = self.db.get_lead(phone)
        if not lead:
             return

        # Execute side effects
        if target_state == LeadStatus.SCHEDULED:
            self._handle_scheduling(lead, context)
        elif target_state == LeadStatus.CONTRACT_PENDING:
            self._handle_contract_generation(lead, context)

        # Update DB
        self.db.update_lead(phone, {
            "status": target_state,
            "journey_state": target_state,
            "updated_at": datetime.now().isoformat()
        })

    def _handle_scheduling(self, lead: dict[str, Any], context: dict[str, Any]) -> None:
        start_time = context.get("start_time")
        if not start_time:
            return

        end_time = start_time + timedelta(hours=1)
        summary = f"Visita Immobile - {lead.get('customer_name')}"
        attendees = [lead.get('customer_phone') + "@wa.me"] # Placeholder email logic
        
        link = self.calendar.create_event(summary, start_time, end_time, attendees)
        if link:
            self.msg.send_message(
                lead.get('customer_phone'), 
                f"Perfetto! Visita confermata. Ecco il link al calendario: {link}"
            )

    def _handle_contract_generation(self, lead: dict[str, Any], context: dict[str, Any]) -> None:
        data = {
            "customer_name": lead.get("customer_name"),
            "customer_phone": lead.get("customer_phone"),
            "offered_price": context.get("offered_price")
        }
        pdf_path = self.doc_gen.generate_pdf("proposta", data)
        if pdf_path:
             self.msg.send_message(
                lead.get('customer_phone'), 
                "Ho generato la proposta d'acquisto per te. Una copia è stata salvata nel nostro sistema."
            )
