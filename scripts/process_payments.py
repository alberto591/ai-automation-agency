#!/usr/bin/env python3
"""
Daily Cron Job for processing payment reminders.
Usage: python scripts/process_payments.py
"""
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from config.container import Container
from infrastructure.logging import get_logger

logger = get_logger("cron.payments")


def main():
    logger.info("STARTING_PAYMENT_PROCESSORT")
    try:
        container = Container()
        stats = container.payment_service.process_daily_reminders()
        logger.info("PAYMENT_PROCESSOR_COMPLETED", context=stats)
    except Exception as e:
        logger.error("PAYMENT_PROCESSOR_CRASHED", context={"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
