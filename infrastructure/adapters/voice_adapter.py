"""Voice adapter implementing VoicePort with Deepgram STT and GDPR consent."""

from datetime import datetime

from twilio.twiml.voice_response import VoiceResponse

from config.container import container
from domain.models import CallConsent
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class VoiceAdapter:
    """Voice adapter with Deepgram transcription and GDPR consent flow."""

    def __init__(self) -> None:
        """Initialize voice adapter."""
        self.deepgram = None  # Lazy loaded

    def get_greeting_twiml(self, webhook_url: str) -> str:
        """Returns TwiML with GDPR consent prompt and recording.

        Args:
            webhook_url: Base URL for voice webhooks

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        # GDPR Consent Prompt (Italian)
        response.say(
            "Benvenuto. Questa chiamata potrebbe essere registrata per garantire "
            "la qualità del servizio. Continuando, acconsenti alla registrazione. "
            "Premi uno per continuare, o riattacca per rifiutare.",
            language="it-IT",
            voice="alice",
        )

        # Gather consent input
        response.gather(
            num_digits=1,
            action=f"{webhook_url}/consent",
            method="POST",
            timeout=5,
        )

        # If no input, assume no consent
        response.say(
            "Nessuna risposta ricevuta. Chiusura della chiamata.",
            language="it-IT",
            voice="alice",
        )
        response.hangup()

        return str(response)

    def get_consent_handler_twiml(self, webhook_url: str, digits: str, call_sid: str) -> str:
        """Handle consent response and proceed with call.

        Args:
            webhook_url: Base URL for voice webhooks
            digits: User's input (1 = consent, anything else = reject)
            call_sid: Twilio Call SID

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        if digits == "1":
            # Consent given - log and proceed
            logger.info(
                "CALL_CONSENT_GIVEN",
                context={"call_sid": call_sid},
            )

            # Log consent to database (async task handled by webhook)
            response.say(
                "Grazie. Come posso aiutarti?",
                language="it-IT",
                voice="alice",
            )

            # Start recording
            response.record(
                action=f"{webhook_url}/recording",
                transcribe=False,  # We'll use Deepgram instead
                max_length=120,  # 2 minutes max
                play_beep=False,
            )

        else:
            # Consent rejected
            logger.info(
                "CALL_CONSENT_REJECTED",
                context={"call_sid": call_sid, "digits": digits},
            )

            response.say(
                "Capisco. Grazie per la chiamata. Arrivederci.",
                language="it-IT",
                voice="alice",
            )
            response.hangup()

        return str(response)

    def handle_transcription(self, transcription_text: str, from_phone: str) -> None:
        """Process transcribed text as an inbound lead.

        Args:
            transcription_text: Transcribed speech text
            from_phone: Caller's phone number
        """
        try:
            logger.info(
                "VOICE_TRANSCRIPTION_RECEIVED",
                context={"phone": from_phone, "text": transcription_text[:100]},
            )

            # Process through lead processor
            container.lead_processor.process_lead(
                phone=from_phone,
                name="Voice Caller",  # Will be extracted by AI if provided
                query=transcription_text,
            )

        except Exception as e:
            logger.error(
                "VOICE_LEAD_PROCESSING_FAILED",
                context={"phone": from_phone, "error": str(e)},
            )

    def log_call_consent(
        self,
        call_sid: str,
        phone: str,
        consent_given: bool,
        recording_url: str | None = None,
    ) -> None:
        """Log call consent to database for GDPR compliance.

        Args:
            call_sid: Twilio Call SID
            phone: Caller's phone number
            consent_given: Whether consent was provided
            recording_url: URL to call recording (if available)
        """
        try:
            consent = CallConsent(
                call_id=call_sid,
                phone=phone,
                consent_given=consent_given,
                consent_timestamp=datetime.now() if consent_given else None,
                consent_method="ivr",
                recording_url=recording_url,
            )

            # Save to database
            container.db.client.table("call_consents").insert(
                {
                    "call_id": consent.call_id,
                    "phone": consent.phone,
                    "consent_given": consent.consent_given,
                    "consent_timestamp": (
                        consent.consent_timestamp.isoformat() if consent.consent_timestamp else None
                    ),
                    "consent_method": consent.consent_method,
                    "recording_url": consent.recording_url,
                }
            ).execute()

            logger.info(
                "CALL_CONSENT_LOGGED",
                context={
                    "call_sid": call_sid,
                    "phone": phone,
                    "consent": consent_given,
                },
            )

        except Exception as e:
            logger.error(
                "CALL_CONSENT_LOG_FAILED",
                context={"call_sid": call_sid, "error": str(e)},
            )
