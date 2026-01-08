from datetime import datetime, timedelta

from domain.models import PaymentSchedule
from domain.ports import DatabasePort, MessagingPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PaymentService:
    def __init__(self, db: DatabasePort, msg: MessagingPort):
        self.db = db
        self.msg = msg

    def create_payment_schedule(self, schedule: PaymentSchedule) -> str:
        """Creates or updates a payment schedule."""
        data = {
            "lead_id": schedule.lead_id,
            "amount": schedule.amount,
            "due_date": schedule.due_date.isoformat(),
            "description": schedule.description,
            "currency": schedule.currency,
            "recurrence": schedule.recurrence,
            "reminder_days": schedule.reminder_days,
            "status": schedule.status,
            "stripe_link": schedule.stripe_link,
            "metadata": schedule.metadata,
        }
        if schedule.id:
            data["id"] = schedule.id

        schedule_id = self.db.save_payment_schedule(data)
        logger.info(
            "PAYMENT_SCHEDULE_CREATED", context={"id": schedule_id, "lead_id": schedule.lead_id}
        )
        return schedule_id

    def process_daily_reminders(self) -> dict[str, int]:
        """Checks for due payments and sends reminders."""
        today = datetime.now().date()
        # Look ahead 14 days to catch upcoming reminders (max reminder day usually 7, be safe)
        lookahead = datetime.now() + timedelta(days=14)

        candidates = self.db.get_due_payments(lookahead)
        stats = {"upcoming": 0, "sent": 0, "errors": 0}

        for payment in candidates:
            try:
                due_date = datetime.fromisoformat(str(payment["due_date"])).date()
                days_until_due = (due_date - today).days

                # Determine if we should send a reminder today
                reminder_days = payment.get("reminder_days", [7, 3, 0])

                should_send = False
                template = ""

                if days_until_due in reminder_days:
                    should_send = True
                    if days_until_due == 0:
                        template = "⚠️ *Promemoria Scadenza*\n\nIl pagamento di €{amount} per {desc} scade OGGI ({date}).\n\nPaga qui: {link}"
                    elif days_until_due > 0:
                        template = "📅 *Avviso Scadenza*\n\nIl pagamento di €{amount} per {desc} scadrà il {date} (tra {days} giorni).\n\nPaga qui: {link}"
                elif days_until_due < 0 and days_until_due > -7:  # Overdue within last week
                    # Simple logic: ensure we haven't already sent "overdue" today (tracking processed is needed, simplified here)
                    # For now, let's skip overdue spam logic unless explicitly requested
                    pass

                if should_send:
                    # Fetch lead to get phone
                    # Note: get_due_payments could generic join lead, but we use port
                    # Assuming we have to fetch lead separately
                    # Optimization: db.get_lead_by_id(lead_id) - but port only has get_lead(phone)
                    # We need get_lead_by_id in port or we assume get_due_payments returns phone?
                    # Let's assume get_due_payments returns lead_phone for efficiency or we fail.

                    phone = payment.get("lead_phone")
                    if not phone:
                        logger.warning("PAYMENT_NO_PHONE", context={"payment_id": payment["id"]})
                        continue

                    msg_body = template.format(
                        amount=payment["amount"],
                        desc=payment.get("description", "Servizio"),
                        date=due_date.strftime("%d/%m/%Y"),
                        days=days_until_due,
                        link=payment.get("stripe_link", "#"),
                    )

                    self.msg.send_message(phone, msg_body)
                    stats["sent"] += 1
                    logger.info(
                        "PAYMENT_REMINDER_SENT",
                        context={"payment_id": payment["id"], "phone": phone},
                    )
            except Exception as e:
                logger.error(
                    "PAYMENT_PROCESS_ERROR",
                    context={"payment_id": payment.get("id"), "error": str(e)},
                )
                stats["errors"] += 1

        return stats
