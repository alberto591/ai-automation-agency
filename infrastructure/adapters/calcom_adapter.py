"""Cal.com adapter for appointment scheduling.

Implements the CalendarPort interface using Cal.com's API v2.
Provides booking creation and availability checking functionality.
"""

from datetime import datetime
from typing import cast

import requests

from domain.ports import CalendarPort
from domain.services.logging import get_logger

logger = get_logger(__name__)


class CalComAdapter(CalendarPort):
    """Cal.com API adapter for calendar operations."""

    def __init__(self) -> None:
        from config.settings import settings

        self.api_key = settings.CALCOM_API_KEY
        self.event_type_id = settings.CALCOM_EVENT_TYPE_ID
        self.booking_link = settings.CALCOM_BOOKING_LINK
        self.base_url = "https://api.cal.com/v2"

    def _get_headers(self) -> dict[str, str]:
        """Get API request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13",  # API version
        }

    def get_availability(self, staff_id: str, date: str) -> list[str]:
        """
        Fetch available time slots for a specific date.

        Args:
            staff_id: Not used for Cal.com (uses event_type_id instead)
            date: Date in YYYY-MM-DD format

        Returns:
            List of available time slots in ISO format
        """
        if not self.api_key or not self.event_type_id:
            logger.warning("CALCOM_API_DISABLED", context={"reason": "Missing API credentials"})
            return []

        url = f"{self.base_url}/slots"

        # Cal.com requires startTime and endTime for the range
        start_time = f"{date}T00:00:00Z"
        end_time = f"{date}T23:59:59Z"

        params = {
            "apiKey": self.api_key,
            "eventTypeId": self.event_type_id,
            "startTime": start_time,
            "endTime": end_time,
            "timeZone": "Europe/Rome",  # Italian timezone
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cal.com returns slots in data.slots array
            slots = data.get("data", {}).get("slots", [])
            logger.info("CALCOM_SLOTS_FETCHED", context={"count": len(slots), "date": date})
            return cast(list[str], slots)

        except requests.exceptions.RequestException as e:
            logger.error("CALCOM_AVAILABILITY_FAILED", context={"error": str(e)})
            return []

    def create_event(
        self, summary: str, start_time: datetime, end_time: datetime, attendees: list[str]
    ) -> str:
        """
        Create a booking in Cal.com.

        Args:
            summary: Booking title/description
            start_time: Start datetime
            end_time: End datetime
            attendees: List of attendee emails

        Returns:
            Booking confirmation link or empty string on failure
        """
        if not self.api_key or not self.event_type_id:
            logger.warning("CALCOM_API_DISABLED", context={"reason": "Missing API credentials"})
            return self.booking_link  # Return public booking link as fallback

        url = f"{self.base_url}/bookings"

        # Extract attendee info
        attendee_email = attendees[0] if attendees else "noreply@anzevino.ai"
        attendee_name = summary.split("-")[0].strip() if "-" in summary else "Client"

        payload = {
            "eventTypeId": self.event_type_id,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "responses": {
                "name": attendee_name,
                "email": attendee_email,
                "notes": summary,
            },
            "timeZone": "Europe/Rome",
            "language": "it",
        }

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                params={"apiKey": self.api_key},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            # Cal.com returns booking details with confirmation link
            booking_id = data.get("data", {}).get("id")
            logger.info("CALCOM_BOOKING_CREATED", context={"booking_id": booking_id})

            # Return the public booking link (user can reschedule via this)
            return self.booking_link

        except requests.exceptions.RequestException as e:
            logger.error("CALCOM_BOOKING_FAILED", context={"error": str(e)})
            # Return public booking link as fallback
            return self.booking_link
