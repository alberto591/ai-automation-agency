import re
from typing import Any

from domain.ports import EmailPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class EmailParserService:
    def __init__(self, email_port: EmailPort) -> None:
        self.email_port = email_port

    def parse_and_process(self) -> list[dict[str, Any]]:
        """
        Fetches unread emails, parses them, and returns structured lead data.
        """
        raw_emails = self.email_port.fetch_unread_emails()
        leads = []

        for email in raw_emails:
            sender = email.get("sender", "").lower()
            subject = email.get("subject", "").lower()
            body = email.get("body", "")

            parsed_lead = None

            # 1. Idealista
            if "idealista" in sender:
                parsed_lead = self._parse_idealista(body)
            # 2. Immobiliare.it
            elif "immobiliare" in sender:
                parsed_lead = self._parse_immobiliare(body)
            # 3. Generic/Manual
            elif "nuovo contatto" in subject:  # Fallback
                parsed_lead = self._parse_generic(body)

            if parsed_lead:
                logger.info(
                    "EMAIL_PARSED_SUCCESS", context={"source": sender, "lead": parsed_lead["name"]}
                )
                leads.append(parsed_lead)
                self.email_port.mark_as_processed(email["id"])
            else:
                logger.warning("EMAIL_PARSE_FAILED_OR_IGNORED", context={"subject": subject})

        return leads

    def _parse_idealista(self, html: str) -> dict[str, Any] | None:
        """
        Extracts lead from Idealista HTML.
        Uses Regex heavily as HTML structure varies.
        """
        try:
            # Regex heuristics (Mock implementation for now)
            # Name: often after "Nome:" or inside specific spans
            name_match = re.search(r"Nome:?\s*<strong>(.*?)</strong>", html, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "Unknown Lead"

            # Phone
            phone_match = re.search(r"(\+?39\s?[0-9]{3}\s?[0-9]{6,7})", html)
            phone = phone_match.group(1).replace(" ", "") if phone_match else None

            # Property Ref
            ref_match = re.search(r"Rif\.?\s*([A-Z0-9-]+)", html, re.IGNORECASE)
            prop_ref = ref_match.group(1) if ref_match else None

            if phone:
                return {
                    "name": name,
                    "phone": phone,
                    "agency": "Idealista",
                    "properties": f"Ref: {prop_ref}" if prop_ref else "Interested in property",
                }
        except Exception as e:
            logger.error("IDEALISTA_PARSE_ERROR", context={"error": str(e)})
        return None

    def _parse_immobiliare(self, html: str) -> dict[str, Any] | None:
        """
        Extracts lead from Immobiliare.it HTML.
        """
        try:
            # Heuristics
            name_match = re.search(r"Richiesta da\s*<b>(.*?)</b>", html, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "Unknown Lead"

            phone_match = re.search(r"tel:(\+?39[0-9]+)", html)
            phone = phone_match.group(1) if phone_match else None

            if not phone:
                # Try raw text
                phone_match = re.search(r"(\+?39\s?[0-9]{3}\s?[0-9]{6,7})", html)
                phone = phone_match.group(1).replace(" ", "") if phone_match else None

            if phone:
                return {
                    "name": name,
                    "phone": phone,
                    "agency": "Immobiliare.it",
                    "properties": "Interested in property",
                }
        except Exception:
            pass
        return None

    def _parse_generic(self, html: str) -> dict[str, Any] | None:
        # Very basic fallback
        phone_match = re.search(r"(\+?39\s?[0-9]{3}\s?[0-9]{6,7})", html)
        if phone_match:
            return {
                "name": "Web Lead",
                "phone": phone_match.group(1).replace(" ", ""),
                "agency": "Direct Email",
                "properties": "Contact via Email",
            }
        return None
