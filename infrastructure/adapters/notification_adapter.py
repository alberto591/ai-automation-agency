import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import settings
from domain.handoff import HandoffRequest
from domain.ports import NotificationPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class NotificationAdapter(NotificationPort):
    def notify_agency(self, request: HandoffRequest) -> bool:
        """
        Sends an email notification to the agency about the handoff.
        """
        try:
            subject = (
                f"🚨 Human Handoff Request: {request.reason.value} ({request.priority.upper()})"
            )

            # Construct body
            body = f"""
            <h2>Human Intervention Required</h2>
            <p><strong>Reason:</strong> {request.reason.value}</p>
            <p><strong>Lead ID:</strong> {request.lead_id}</p>
            <p><strong>Priority:</strong> {request.priority}</p>
            <hr>
            <h3>Context</h3>
            <p><strong>User Message:</strong> {request.user_message or "N/A"}</p>
            <p><strong>AI Analysis:</strong> {request.ai_analysis or "N/A"}</p>
            <hr>
            <h3>Metadata</h3>
            <pre>{request.metadata}</pre>
            <br>
            <a href="{settings.SUPABASE_URL}/dashboard/leads/{request.lead_id}">View Lead in Dashboard</a>
            """

            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_USER
            msg["To"] = settings.AGENCY_OWNER_EMAIL
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                logger.warning("SMTP_NOT_CONFIGURED", context={"reason": "Missing credentials"})
                return False

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(
                "AGENCY_NOTIFIED", context={"lead_id": request.lead_id, "reason": request.reason}
            )
            return True

        except Exception as e:
            logger.error(
                "NOTIFICATION_FAILED", context={"error": str(e), "lead_id": request.lead_id}
            )
            return False
