"""Cal.com webhook handler for appointment events.

Handles webhook events from Cal.com for booking lifecycle:
- booking.created: New appointment scheduled
- booking.cancelled: Appointment cancelled
- booking.rescheduled: Appointment time changed
"""

import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from config.container import container
from config.settings import settings
from domain.enums import LeadStatus
from domain.services.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhooks/calcom")
async def calcom_webhook(
    request: Request, x_cal_signature_256: str | None = Header(None)
) -> dict[str, str]:
    """
    Handle Cal.com webhook events.

    Cal.com sends webhooks for booking events with HMAC signature verification.
    """
    body = await request.body()

    # Verify webhook signature if secret is configured
    if settings.CALCOM_WEBHOOK_SECRET:
        if not x_cal_signature_256:
            logger.warning("CALCOM_WEBHOOK_MISSING_SIGNATURE")
            raise HTTPException(status_code=401, detail="Missing signature")

        # Cal.com uses HMAC-SHA256
        expected_sig = hmac.new(
            settings.CALCOM_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(f"sha256={expected_sig}", x_cal_signature_256):
            logger.warning("CALCOM_WEBHOOK_INVALID_SIGNATURE")
            raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        data: dict[str, Any] = await request.json()
        logger.info("CALCOM_WEBHOOK_RECEIVED", context={"event": data.get("triggerEvent")})

        event_type = data.get("triggerEvent")  # e.g., "BOOKING_CREATED"
        payload = data.get("payload", {})

        # Extract booking details
        booking = payload.get("booking", {})
        attendees = booking.get("attendees", [])

        if not attendees:
            logger.warning("CALCOM_WEBHOOK_NO_ATTENDEES")
            return {"status": "ok", "message": "No attendees found"}

        # Get phone from attendee metadata or responses
        phone = None
        for attendee in attendees:
            # Check metadata first
            metadata = attendee.get("metadata", {})
            phone = metadata.get("phone") or attendee.get("phoneNumber")
            if phone:
                break

        if not phone:
            logger.warning("CALCOM_WEBHOOK_MISSING_PHONE")
            return {"status": "ok", "message": "No phone number found"}

        if event_type == "BOOKING_CREATED":
            container.db.update_lead_status(phone, LeadStatus.SCHEDULED)
            # Register booking in appointments table
            await container.appointment_service.register_booking(
                phone,
                {
                    "bookingId": booking.get("id"),
                    "startTime": booking.get("startTime"),
                    "endTime": booking.get("endTime"),
                },
            )
            logger.info(
                "LEAD_STATUS_UPDATED_BY_CALCOM", context={"phone": phone, "status": "SCHEDULED"}
            )

        elif event_type == "BOOKING_CANCELLED":
            container.db.update_lead_status(phone, LeadStatus.QUALIFIED)
            await container.appointment_service.cancel_booking(booking.get("id"))
            logger.info(
                "LEAD_STATUS_UPDATED_BY_CALCOM", context={"phone": phone, "status": "QUALIFIED"}
            )

        elif event_type == "BOOKING_RESCHEDULED":
            # Keep as SCHEDULED, update booking times
            await container.appointment_service.reschedule_booking(
                booking.get("id"),
                {
                    "startTime": booking.get("startTime"),
                    "endTime": booking.get("endTime"),
                },
            )
            logger.info("BOOKING_RESCHEDULED", context={"phone": phone})

        return {"status": "ok"}

    except Exception as e:
        logger.error("CALCOM_WEBHOOK_FAILED", context={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed") from e
