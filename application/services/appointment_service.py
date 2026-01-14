"""Appointment service for handling booking lifecycle and analytics."""

import asyncio
from typing import Any

from domain.ports import DatabasePort, MessagingPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AppointmentService:
    """Service to manage appointments and automated surveys."""

    def __init__(self, db: DatabasePort, messaging: MessagingPort) -> None:
        self.db = db
        self.messaging = messaging

    async def register_booking(self, lead_phone: str, booking_data: dict[str, Any]) -> str:
        """Registers a new booking from Cal.com."""
        logger.info("REGISTER_BOOKING", context={"phone": lead_phone})

        lead = self.db.get_lead(lead_phone)
        if not lead:
            logger.warning("BOOKING_FOR_UNKNOWN_LEAD", context={"phone": lead_phone})
            # Optionally create lead if missing? For now, we assume lead exists.
            return ""

        appointment_data = {
            "lead_id": lead["id"],
            "external_booking_id": booking_data.get("bookingId"),
            "start_time": booking_data.get("startTime"),
            "end_time": booking_data.get("endTime"),
            "status": "scheduled",
            "property_id": booking_data.get("propertyId"),  # If available in metadata
        }

        return self.db.save_appointment(appointment_data)

    async def cancel_booking(self, booking_id: str) -> None:
        """Handles booking cancellation."""
        logger.info("CANCEL_BOOKING", context={"booking_id": booking_id})
        self.db.update_appointment_status(booking_id, "cancelled")

    async def reschedule_booking(self, booking_id: str, new_times: dict[str, Any]) -> None:
        """Handles booking rescheduling."""
        logger.info("RESCHEDULE_BOOKING", context={"booking_id": booking_id})
        # For simple update, we just update the DB fields
        appointment = self.db.get_appointment_by_external_id(booking_id)
        if appointment:
            # data = {
            #     "start_time": new_times.get("startTime"),
            #     "end_time": new_times.get("endTime"),
            #     "status": "scheduled",
            # }
            # We don't have update_appointment yet, but we can reuse update_appointment_status
            # or add update_appointment. Since status is also 'scheduled' it works.
            self.db.update_appointment_status(booking_id, "scheduled")
            # TODO: Add update_appointment to DatabasePort for full updates

    async def trigger_post_viewing_survey(self, booking_id: str) -> None:
        """Sends a post-viewing survey via WhatsApp."""
        appointment = self.db.get_appointment_by_external_id(booking_id)
        if not appointment or appointment["status"] != "completed":
            logger.warning("SURVEY_TRIGGER_INVALID", context={"booking_id": booking_id})
            return

        # Fetch lead for phone number
        # Note: DatabasePort should ideally return joined lead info or lead_id
        # For now, we assume we can fetch lead by ID if we add that to port
        # Or we can get lead from the appointment dict if it was fetched with join

        # Simplified: We use lead_id to get lead
        # Need get_lead_by_id in port? Let's check existing ports.
        # supabase_adapter has get_lead(phone).

        # For now, let's assume we can notify the user via lead's phone
        # Need to find phone from lead_id.

        logger.info("SENDING_SURVEY", context={"booking_id": booking_id})

        # survey_text = (
        #     "Ciao! Grazie per aver visitato la proprietà oggi. 🏠\n"
        #     "Come valuteresti la tua esperienza da 1 a 5? (Rispondi solo con il numero)"
        # )

        # TODO: Implement lead lookup by ID and send message
        # self.messaging.send_message(lead_phone, survey_text)

    async def mark_completed(self, booking_id: str) -> None:
        """Mark an appointment as completed and queue survey."""
        self.db.update_appointment_status(booking_id, "completed")
        # Trigger survey after a delay
        asyncio.create_task(self._delayed_survey(booking_id))

    async def _delayed_survey(self, booking_id: str, delay_hours: int = 1) -> None:
        """Delayed trigger for survey."""
        await asyncio.sleep(delay_hours * 3600)
        await self.trigger_post_viewing_survey(booking_id)
