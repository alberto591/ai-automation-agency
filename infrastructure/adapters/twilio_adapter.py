from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential
from twilio.rest import Client

from domain.errors import ExternalServiceError
from domain.ports import MessagingPort
from infrastructure.logging import get_logger
from infrastructure.rate_limiter import RateLimiter

logger = get_logger(__name__)


class TwilioAdapter(MessagingPort):
    def __init__(self) -> None:
        from config.settings import settings

        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.message_rate_limit = settings.MESSAGE_RATE_LIMIT
        self.message_rate_window_seconds = settings.MESSAGE_RATE_WINDOW_SECONDS
        self.from_number = settings.TWILIO_PHONE_NUMBER
        self.webhook_base_url = settings.WEBHOOK_BASE_URL  # Optional

        self.rate_limiter = RateLimiter(
            max_messages=self.message_rate_limit,
            window_seconds=self.message_rate_window_seconds,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_message(self, to: str, body: str, media_url: str | None = None) -> str:
        logger.info("TWILIO_SEND_START", context={"to": to, "body_preview": body[:20]})
        # 1. Clean numbers
        clean_to = "".join(to.split())
        from_number = self.from_number

        # 2. Add whatsapp prefix safely
        final_to = f"whatsapp:{clean_to}" if not clean_to.startswith("whatsapp:") else clean_to
        final_from = (
            f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
        )

        logger.info(
            "TWILIO_FORMATTED_NUMBERS", context={"final_to": final_to, "final_from": final_from}
        )

        if final_to == final_from:
            logger.warning("SKIPPING_SELF_MESSAGE", context={"to": final_to, "from": final_from})
            return "skipped_self_send"

        try:
            params: dict[str, Any] = {"from_": final_from, "to": final_to, "body": body}
            if media_url:
                params["media_url"] = [media_url]

            # 3. Add Status Callback if configured
            # In production, this should be the public URL
            if self.webhook_base_url:
                params["status_callback"] = f"{self.webhook_base_url}/api/webhooks/twilio/status"

            logger.info("TWILIO_API_CALL", context={"params_keys": list(params.keys())})
            message = self.client.messages.create(**params)
            logger.info(
                "MESSAGE_SENT",
                context={"to": final_to, "sid": message.sid, "has_media": bool(media_url)},
            )
            return str(message.sid)
        except Exception as e:
            logger.error("TWILIO_SEND_FAILED", context={"to": to, "error": str(e)})
            raise ExternalServiceError("Failed to send WhatsApp message", cause=str(e)) from e

    def send_interactive_message(self, to: str, message: Any) -> str:
        """
        Sends an interactive message (Buttons, List, etc.).

        Currently not implemented for Twilio.
        """
        logger.warning("TWILIO_INTERACTIVE_NOT_IMPLEMENTED", context={"to": to})
        raise NotImplementedError("Interactive messages not yet supported for Twilio adapter")
