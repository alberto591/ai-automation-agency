from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential
from twilio.rest import Client

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import MessagingPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class TwilioAdapter(MessagingPort):
    def __init__(self) -> None:
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_message(self, to: str, body: str, media_url: str | None = None) -> str:
        # 1. Clean numbers
        clean_to = "".join(to.split())
        from_number = settings.TWILIO_PHONE_NUMBER

        # 2. Add whatsapp prefix safely
        final_to = f"whatsapp:{clean_to}" if not clean_to.startswith("whatsapp:") else clean_to
        final_from = (
            f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
        )

        if final_to == final_from:
            logger.warning("SKIPPING_SELF_MESSAGE", context={"to": final_to, "from": final_from})
            return "skipped_self_send"

        try:
            params: dict[str, Any] = {"from_": final_from, "to": final_to, "body": body}
            if media_url:
                params["media_url"] = [media_url]

            message = self.client.messages.create(**params)
            logger.info(
                "MESSAGE_SENT",
                context={"to": final_to, "sid": message.sid, "has_media": bool(media_url)},
            )
            return str(message.sid)
        except Exception as e:
            logger.error("TWILIO_SEND_FAILED", context={"to": to, "error": str(e)})
            raise ExternalServiceError("Failed to send WhatsApp message", cause=str(e)) from e
