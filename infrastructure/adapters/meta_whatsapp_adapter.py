from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from domain.errors import ExternalServiceError, RateLimitError
from domain.ports import MessagingPort
from infrastructure.logging import get_logger
from infrastructure.rate_limiter import RateLimiter

logger = get_logger(__name__)


class MetaWhatsAppAdapter(MessagingPort):
    """
    Adapter for WhatsApp Cloud API (Meta).
    """

    def __init__(self) -> None:
        self.access_token = settings.META_ACCESS_TOKEN
        self.phone_id = settings.META_PHONE_ID
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_id}/messages"
        self.rate_limiter = RateLimiter(
            max_messages=settings.MESSAGE_RATE_LIMIT,
            window_seconds=settings.MESSAGE_RATE_WINDOW_SECONDS,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def send_message(self, to: str, body: str, media_url: str | None = None) -> str:
        # Check rate limit
        if not self.rate_limiter.check_rate_limit(to):
            remaining = self.rate_limiter.get_remaining(to)
            raise RateLimitError(
                f"Rate limit exceeded for {to}",
                cause=f"Exceeded {settings.MESSAGE_RATE_LIMIT} messages per {settings.MESSAGE_RATE_WINDOW_SECONDS}s",
                remediation=f"Wait before sending more messages. Remaining: {remaining}",
            )

        # Clean number (Meta expects digits only, no prefix like 'whatsapp:')
        clean_to = "".join(filter(str.isdigit, to))

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
        }

        if media_url:
            # Note: Meta handles media differently (image, document, etc.)
            # For simplicity, we assume image if media_url is provided.
            # In a production scenario, we'd detect the file type.
            payload["type"] = "image"
            payload["image"] = {"link": media_url, "caption": body}
        else:
            payload["type"] = "text"
            payload["text"] = {"preview_url": False, "body": body}

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            response_data = response.json()

            if response.status_code != 200:
                logger.error(
                    "META_WHATSAPP_SEND_FAILED",
                    context={
                        "to": clean_to,
                        "status": response.status_code,
                        "error": response_data,
                    },
                )
                raise ExternalServiceError(
                    f"Meta API returned status {response.status_code}",
                    cause=str(response_data),
                )

            message_id = response_data.get("messages", [{}])[0].get("id")
            logger.info(
                "MESSAGE_SENT_META",
                context={"to": clean_to, "message_id": message_id, "has_media": bool(media_url)},
            )
            return str(message_id)

        except Exception as e:
            if isinstance(e, ExternalServiceError):
                raise e
            logger.error("META_WHATSAPP_HTTP_FAILED", context={"to": clean_to, "error": str(e)})
            raise ExternalServiceError(
                "Failed to connect to Meta WhatsApp API", cause=str(e)
            ) from e

    def send_interactive_message(self, to: str, message: Any) -> str:
        """
        Sends an interactive message (Buttons or List).
        Expects 'message' to be an instance of domain.messages.InteractiveMessage.
        """
        # Clean number
        clean_to = "".join(filter(str.isdigit, to))

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        interactive_payload = {}

        # 1. Map Domain Model to Meta Payload
        if message.type == "button":
            interactive_payload = {
                "type": "button",
                "body": {"text": message.body_text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": btn.id, "title": btn.title[:20]},  # Meta limit 20 chars
                        }
                        for btn in (message.buttons or [])
                    ]
                },
            }
        elif message.type == "list":
            interactive_payload = {
                "type": "list",
                "body": {"text": message.body_text},
                "action": {
                    "button": message.button_text or "Menu",
                    "sections": [
                        {
                            "title": section.title,
                            "rows": [
                                {
                                    "id": row.id,
                                    "title": row.title[:24],  # Meta limit
                                    "description": (row.description or "")[:72],
                                }
                                for row in section.rows
                            ],
                        }
                        for section in (message.sections or [])
                    ],
                },
            }

        # Add Header/Footer if present
        if message.header_text:
            interactive_payload["header"] = {"type": "text", "text": message.header_text}

        if message.footer_text:
            interactive_payload["footer"] = {"text": message.footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "interactive",
            "interactive": interactive_payload,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            response_data = response.json()

            if response.status_code != 200:
                logger.error("META_WHATSAPP_INTERACTIVE_FAILED", context={"error": response_data})
                raise ExternalServiceError(f"Meta API Error: {response_data}")

            messages = response_data.get("messages", [])
            if messages and isinstance(messages, list):
                return str(messages[0].get("id", ""))
            return ""

        except Exception as e:
            logger.error("META_INTERACTIVE_SEND_ERROR", context={"error": str(e)})
            raise ExternalServiceError("Failed to send interactive message", cause=str(e)) from e

    def parse_webhook_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Parses webhook data from Meta WhatsApp Cloud API.
        Meta webhooks have a different structure than Twilio.
        """
        # Meta webhook structure is nested in entry[0].changes[0].value.messages[0]
        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [{}])

            if not messages:
                # This might be a status update
                return {
                    "phone": "",
                    "body": "",
                    "media_url": None,
                    "is_status_update": True,
                }

            message = messages[0]
            from_phone = message.get("from", "")
            msg_type = message.get("type", "text")

            # Extract body based on message type
            body = ""
            media_url = None

            if msg_type == "text":
                body = message.get("text", {}).get("body", "")
            elif msg_type == "image":
                media_url = message.get("image", {}).get(
                    "id"
                )  # Meta uses media ID, not URL directly
                body = message.get("image", {}).get("caption", "")
            elif msg_type == "button":
                body = message.get("button", {}).get("text", "")
            elif msg_type == "interactive":
                # Handle interactive responses (button/list replies)
                interactive = message.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    body = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    body = interactive.get("list_reply", {}).get("title", "")

            return {
                "phone": from_phone,
                "body": body.strip(),
                "media_url": media_url,
                "is_status_update": False,
            }

        except Exception as e:
            logger.error("META_WEBHOOK_PARSE_FAILED", context={"error": str(e)})
            return {
                "phone": "",
                "body": "",
                "media_url": None,
                "is_status_update": True,
            }
