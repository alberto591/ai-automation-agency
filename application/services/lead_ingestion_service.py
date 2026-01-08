from typing import Any

from application.services.lead_processor import LeadProcessor
from domain.errors import BaseAppError
from domain.lead_sources import LeadSourceType
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class LeadIngestionService:
    def __init__(self, lead_processor: LeadProcessor):
        self.lead_processor = lead_processor

    def process_facebook_webhook(self, body: dict[str, Any]) -> int:
        """
        Processes a Facebook Webhook payload.
        Returns the number of leads processed.
        Structure: body['entry'][x]['changes'][y]['value'] -> { form_id, leadgen_id, ... }
        Note: The actual lead data (name, phone) is NOT in the webhook.
        The webhook only gives a leadgen_id. We must fetch the lead details from Graph API.

        HOWEVER, for Sprint 1/2, manual testing or Zapier is often easier than implementing full Graph API fetch
        unless we have a valid Page Access Token.

        Optimization: We will assume for this MVP that we might receive the FULL data via a custom webhook (Zapier/Make)
        that formats it as 'facebook' source, OR we implement the retrieval.

        Given the constraints (no FB App setup), we will implement a 'Generic' handler that CAN handle FB-like structures
        if pushed via Zapier, or a true FB handler structure that logs the ID and TODOs the fetch.
        """
        count = 0
        try:
            entries = body.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    # In real FB Lead Ads, we get leadgen_id.
                    # We would need to: requests.get(f"https://graph.facebook.com/v18.0/{leadgen_id}", params={"access_token": ...})
                    lead_id = value.get("leadgen_id")
                    form_id = value.get("form_id")

                    if lead_id:
                        logger.info(
                            "FB_LEAD_DETECTED", context={"lead_id": lead_id, "form_id": form_id}
                        )
                        # TODO: Implement Graph API fetch.
                        # For now, we log it. If we can't fetch details, we can't create a lead.
                        # This creates a blocker for "Direct" FB integration without a Token.
                        pass

            return count
        except Exception as e:
            logger.error("FB_WEBHOOK_ERROR", context={"error": str(e)})
            raise

    def process_generic_payload(self, data: dict[str, Any], source: str = "generic") -> str:
        """
        Ingests a lead from a generic JSON payload (e.g. Zapier, Typeform).
        Expected fields: name, phone (required). Optional: email, budget, notes.
        """
        try:
            name = data.get("name") or data.get("full_name")
            phone = data.get("phone") or data.get("phone_number")
            email = data.get("email")
            notes = data.get("notes") or data.get("message")
            budget = data.get("budget")

            if not phone:
                raise BaseAppError("Missing phone number in payload")

            # Normalize source
            src_enum = LeadSourceType.MANUAL
            if source.lower() == "facebook":
                src_enum = LeadSourceType.FACEBOOK
            elif source.lower() == "google":
                src_enum = LeadSourceType.GOOGLE
            elif source.lower() == "zapier":
                src_enum = LeadSourceType.ZAPIER

            # Process
            query = f"Source: {source}. Notes: {notes}"
            if budget:
                query += f" Budget: {budget}"

            lead_id = self.lead_processor.process_lead(
                phone=str(phone),
                name=str(name) if name else "Lead Webhook",
                query=query,
                postcode=data.get("postcode"),
            )

            logger.info("GENERIC_LEAD_INGESTED", context={"id": lead_id, "source": source})
            return lead_id

        except Exception as e:
            logger.error("GENERIC_INGEST_FAILED", context={"error": str(e)})
            raise BaseAppError("Failed to ingest lead", cause=str(e)) from e
