from twilio.twiml.voice_response import VoiceResponse

from config.container import container
from domain.ports import VoicePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class TwilioVoiceAdapter(VoicePort):
    def get_greeting_twiml(self, webhook_url: str) -> str:
        """
        Generates TwiML to greet the caller and record a message.
        The recording is sent to 'webhook_url/transcription' for processing.
        """
        response = VoiceResponse()

        # 1. Greeting
        # Italian greeting using Alice (or other Italian voice)
        response.say(
            "Salve. Benvenuti in Anzevino A I. "
            "Al momento non possiamo rispondere. "
            "Per favore, lasciate un messaggio dopo il segnale acustico indicando il vostro nome e l'immobile di interesse. "
            "Vi contatteremo immediatamente su WhatsApp.",
            voice="alice",
            language="it-IT",
        )

        # 2. Record
        # transcribe=True enables automatic transcription
        # transcribeCallback points to our webhook
        transcription_url = f"{webhook_url}/transcription"

        response.record(
            transcribe=True, transcribe_callback=transcription_url, max_length=60, play_beep=True
        )

        # 3. Hangup if recording finishes or no input
        response.hangup()

        return str(response)

    def handle_transcription(self, transcription_text: str, from_phone: str) -> None:
        """
        Processes the transcription as a new lead message.
        """
        logger.info(
            "VOICE_TRANSCRIPTION_RECEIVED", context={"from": from_phone, "text": transcription_text}
        )

        if not transcription_text:
            logger.warning("EMPTY_TRANSCRIPTION", context={"from": from_phone})
            return

        # Treat this as an incoming message in the generic flow
        # This will:
        # 1. Create/Get Lead
        # 2. Save Message (Role: User)
        # 3. Trigger AI Agent -> WhatsApp Reply

        try:
            # We prefix with [VOICE MAIL] to give context to the AI
            enriched_text = f"[VOICE MAIL] {transcription_text}"

            # Using lazy import or container to avoid circular deps if needed,
            # but adapter is called by webhook, so should be safe.
            container.lead_processor.process_incoming_message(phone=from_phone, text=enriched_text)
        except Exception as e:
            logger.error("VOICE_PROCESSING_FAILED", context={"error": str(e)})
            raise
