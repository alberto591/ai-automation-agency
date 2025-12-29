import email
import imaplib
from email.header import decode_header
from typing import Any

from config.settings import settings
from domain.errors import ExternalServiceError
from domain.ports import EmailPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class IMAPAdapter(EmailPort):
    def __init__(self) -> None:
        self.imap_server = settings.IMAP_SERVER
        self.email_user = settings.IMAP_EMAIL
        self.email_pass = settings.IMAP_PASSWORD
        self.imap: imaplib.IMAP4_SSL | None = None

    def _connect(self) -> None:
        if not self.email_user or not self.email_pass:
            logger.warning("IMAP_NOT_CONFIGURED")
            raise ExternalServiceError("IMAP credentials missing")
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email_user, self.email_pass)
        except Exception as e:
            logger.error("IMAP_CONNECTION_FAILED", context={"error": str(e)})
            raise ExternalServiceError("Failed to connect to IMAP") from e

    def fetch_unread_emails(self, criteria: dict[str, Any] | None = None) -> list[dict[str, Any]]:  # noqa: PLR0912
        if not self.imap:
            self._connect()

        if not self.imap:  # Should be connected by now
            return []

        emails = []
        try:
            self.imap.select("INBOX")
            # Search for all unread emails
            status, messages = self.imap.search(None, "UNSEEN")

            if status != "OK":
                return []

            for num in messages[0].split():
                try:
                    _, msg_data = self.imap.fetch(num, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])

                            # Decode Subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")

                            # Get Sender
                            from_ = msg.get("From")

                            # Get Body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/html":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode()

                            emails.append(
                                {
                                    "id": num.decode(),
                                    "subject": subject,
                                    "sender": from_,
                                    "body": body,
                                    "date": msg.get("Date"),
                                }
                            )
                except Exception as e:
                    logger.error("EMAIL_FETCH_ERROR", context={"id": num, "error": str(e)})
                    continue

        except Exception as e:
            logger.error("IMAP_SEARCH_FAILED", context={"error": str(e)})

        return emails

    def mark_as_processed(self, email_id: str) -> None:
        if not self.imap:
            return
        # Flag as Seen is usually automatic with fetch, but we can be explicit
        self.imap.store(email_id, "+FLAGS", "\\Seen")
