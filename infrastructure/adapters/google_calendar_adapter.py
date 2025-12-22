import json
from datetime import datetime
from typing import Any

from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests

from config.settings import settings
from domain.ports import CalendarPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class GoogleCalendarAdapter(CalendarPort):
    def __init__(self):
        self.calendar_id = settings.GOOGLE_CALENDAR_ID
        self.service = self._init_service()

    def _init_service(self) -> Any:
        if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
            logger.warning("GOOGLE_CALENDAR_DISABLED", context={"reason": "Missing credentials"})
            return None
        
        try:
            creds_dict = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, 
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            return creds
        except Exception as e:
            logger.error("GOOGLE_CALENDAR_INIT_FAILED", context={"error": str(e)})
            return None

    def create_event(
        self, 
        summary: str, 
        start_time: datetime, 
        end_time: datetime, 
        attendees: list[str]
    ) -> str:
        if not self.service:
            logger.error("CALENDAR_EVENT_FAILED", context={"reason": "Service not initialized"})
            return ""

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees],
        }

        try:
            # Refresh token if needed
            if self.service.expired:
                self.service.refresh(Request())
            
            headers = {
                "Authorization": f"Bearer {self.service.token}",
                "Content-Type": "application/json"
            }
            
            url = f"https://www.googleapis.com/calendar/v3/calendars/{self.calendar_id}/events"
            
            response = requests.post(url, headers=headers, json=event)
            response.raise_for_status()
            event_result = response.json()
            logger.info("CALENDAR_EVENT_CREATED", context={"id": event_result.get('id')})
            return event_result.get('htmlLink', "")
        except Exception as e:
            logger.error("CALENDAR_EVENT_FAILED", context={"error": str(e)})
            return ""
