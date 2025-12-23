from datetime import datetime
from typing import cast

import requests

from config.settings import settings
from domain.ports import CalendarPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class SetmoreAdapter(CalendarPort):
    def __init__(self) -> None:
        self.api_key = settings.SETMORE_API_KEY
        self.staff_id = settings.SETMORE_STAFF_ID
        self.base_url = "https://developer.setmore.com/api/v1"

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def get_availability(self, staff_id: str, date: str) -> list[str]:
        """
        Fetches availability for a specific staff member on a specific date.
        API Docs refer to: /bookingapi/slots
        """
        if not self.api_key:
            logger.warning("SETMORE_API_DISABLED", context={"reason": "Missing API Key"})
            return []

        url = f"{self.base_url}/bookingapi/slots"
        params = {
            "staff_key": staff_id or self.staff_id,
            "selected_date": date,  # Format: DD-MM-YYYY
            "service_key": "default",  # This might need to be configurable
        }

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            data = response.json()
            # Standard Setmore response format for slots
            slots = data.get("data", {}).get("slots", [])
            return cast(list[str], slots)
        except Exception as e:
            logger.error("SETMORE_AVAILABILITY_FAILED", context={"error": str(e)})
            return []

    def create_event(
        self, summary: str, start_time: datetime, end_time: datetime, attendees: list[str]
    ) -> str:
        """
        Creates an appointment in Setmore.
        API Docs refer to: /bookingapi/appointment/create
        """
        if not self.api_key:
            logger.warning("SETMORE_API_DISABLED", context={"reason": "Missing API Key"})
            return ""

        url = f"{self.base_url}/bookingapi/appointment/create"
        payload = {
            "staff_key": self.staff_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "customer_email": attendees[0] if attendees else "",
            "label": summary,
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            logger.info("SETMORE_APPOINTMENT_CREATED")
            return settings.SETMORE_LINK
        except Exception as e:
            logger.error("SETMORE_BOOKING_FAILED", context={"error": str(e)})
            return ""
