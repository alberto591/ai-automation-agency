import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def main():
    logger.info("EMAIL_POLLING_STARTED")
    try:
        service = container.email_ingestion
        leads = service.parse_and_process()

        logger.info(f"EMAIL_POLLING_COMPLETE: Found {len(leads)} valid leads.")

        for lead in leads:
            try:
                # Inject into Lead Processor
                container.lead_processor.process_lead(
                    phone=lead["phone"],
                    name=lead["name"],
                    query=f"Source: {lead['agency']}. {lead['properties']}",
                    postcode=None,
                )
                logger.info("LEAD_INJECTED_FROM_EMAIL", context={"phone": lead["phone"]})
            except Exception as e:
                logger.error(
                    "LEAD_INJECTION_FAILED", context={"phone": lead["phone"], "error": str(e)}
                )

    except Exception as e:
        logger.error("EMAIL_POLLING_CRASHED", context={"error": str(e)})


if __name__ == "__main__":
    main()
