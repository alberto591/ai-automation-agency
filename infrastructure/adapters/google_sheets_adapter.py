"""Google Sheets adapter for syncing lead data.

This adapter handles synchronization of lead data to a Google Sheet
using the gspread library and Service Account authentication.
"""

import json
from datetime import datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings
from domain.services.logging import get_logger

logger = get_logger(__name__)


class GoogleSheetsAdapter:
    """Adapter for interacting with Google Sheets."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self) -> None:
        """Initialize the Google Sheets client."""
        self.client: gspread.Client | None = None
        self.sheet: gspread.Worksheet | None = None
        self.is_connected = False

        if settings.GOOGLE_SHEETS_CREDENTIALS_JSON and settings.GOOGLE_SHEET_ID:
            self._connect()
        else:
            logger.warning("GOOGLE_SHEETS_NOT_CONFIGURED")

    def _connect(self) -> None:
        """Connect to Google Sheets API."""
        try:
            if not settings.GOOGLE_SHEETS_CREDENTIALS_JSON:
                return

            # Parse credentials from JSON string
            creds_dict = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)

            self.client = gspread.authorize(credentials)

            # Open the sheet
            if settings.GOOGLE_SHEET_ID:
                try:
                    spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
                    # Get the first worksheet
                    self.sheet = spreadsheet.sheet1
                    self.is_connected = True
                    logger.info(
                        "GOOGLE_SHEETS_CONNECTED", context={"sheet_id": settings.GOOGLE_SHEET_ID}
                    )

                    # Initialize headers if empty
                    self._ensure_headers()
                except Exception as e:
                    logger.error("GOOGLE_SHEET_OPEN_ERROR", context={"error": str(e)})

        except Exception as e:
            logger.error("GOOGLE_SHEETS_AUTH_ERROR", context={"error": str(e)})

    def _ensure_headers(self) -> None:
        """Ensure the sheet has the correct headers."""
        if not self.sheet:
            return

        headers = [
            "Phone",
            "Name",
            "Status",
            "Intent",
            "Budget",
            "Zones",
            "Last Contact",
            "Messages Count",
            "Link",
        ]

        try:
            # Check if first row is empty
            first_row = self.sheet.row_values(1)
            if not first_row:
                self.sheet.append_row(headers)
                logger.info("GOOGLE_SHEETS_HEADERS_CREATED")
        except Exception as e:
            logger.error("GOOGLE_SHEETS_HEADER_CHECK_FAILED", context={"error": str(e)})

    def sync_lead(self, lead_data: dict[str, Any]) -> bool:
        """
        Sync a lead to the spreadsheet.
        Updates existing row if phone matches, otherwise appends.

        Args:
            lead_data: Dictionary containing lead information
        """
        if not self.is_connected or not self.sheet:
            logger.warning("GOOGLE_SHEETS_SYNC_SKIPPED", context={"reason": "Not connected"})
            return False

        try:
            phone = lead_data.get("phone")
            if not phone:
                logger.warning("GOOGLE_SHEETS_SYNC_FAILED", context={"reason": "No phone number"})
                return False

            # Format data for row
            row_data = [
                phone,
                lead_data.get("name", ""),
                lead_data.get("status", ""),
                lead_data.get("intent", ""),
                str(lead_data.get("budget", "")),
                ", ".join(lead_data.get("zones", [])),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(lead_data.get("message_count", 0)),
                f"https://dashboard-henna-rho-50.vercel.app/leads/{phone.replace('+', '')}",
            ]

            # Find if lead exists (search in first column)
            try:
                cell = self.sheet.find(phone, in_column=1)
                if cell:
                    # Update existing row
                    # cell.row gives the row number
                    # We update columns A-I (1-9)
                    range_name = f"A{cell.row}:I{cell.row}"
                    self.sheet.update(range_name=range_name, values=[row_data])
                    logger.info(
                        "GOOGLE_SHEETS_ROW_UPDATED", context={"phone": phone, "row": cell.row}
                    )
                else:
                    # Append new row
                    self.sheet.append_row(row_data)
                    logger.info("GOOGLE_SHEETS_ROW_APPENDED", context={"phone": phone})

                return True

            except gspread.exceptions.APIError as e:
                logger.error("GOOGLE_SHEETS_API_ERROR", context={"error": str(e)})
                return False

        except Exception as e:
            logger.error("GOOGLE_SHEETS_SYNC_ERROR", context={"error": str(e)}, exc_info=True)
            return False

    def sync_review(self, review_data: dict[str, Any]) -> bool:
        """
        Sync a review to the 'Reviews' worksheet.
        """
        if not self.is_connected or not self.client:
            logger.warning("GOOGLE_SHEETS_REVIEW_SYNC_SKIPPED", context={"reason": "Not connected"})
            return False

        try:
            # Get or create 'Reviews' worksheet
            try:
                worksheet = self.client.worksheet("Reviews")
            except gspread.WorksheetNotFound:
                worksheet = self.client.add_worksheet(title="Reviews", rows=1000, cols=10)
                # Add headers
                headers = [
                    "Date",
                    "Phone",  # Appraisal Phone
                    "Email",
                    "Overall Rating",
                    "Speed",
                    "Accuracy",
                    "Comments",
                ]
                worksheet.append_row(headers)

            # Format data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                review_data.get("appraisal_phone", ""),
                review_data.get("appraisal_email", ""),
                review_data.get("overall_rating", 0),
                review_data.get("speed_rating", 0),
                review_data.get("accuracy_rating", 0),
                review_data.get("feedback_text", ""),
            ]

            worksheet.append_row(row_data)
            logger.info("GOOGLE_SHEETS_REVIEW_APPENDED")
            return True

        except Exception as e:
            logger.error("GOOGLE_SHEETS_REVIEW_SYNC_ERROR", context={"error": str(e)}, exc_info=True)
            return False
