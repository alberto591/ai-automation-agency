from fastapi import APIRouter, BackgroundTasks, Form, Request, Response

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/voice", tags=["Voice"])


@router.post("/inbound")
async def inbound_call(request: Request) -> Response:
    """Handles incoming calls with GDPR consent prompt."""
    try:
        form_data = await request.form()
        from_phone = form_data.get("From", "Unknown")
        call_sid = form_data.get("CallSid", "")

        logger.info("INBOUND_CALL_RECEIVED", context={"from": from_phone, "sid": call_sid})

        base_url = str(request.base_url).rstrip("/")
        webhook_base = f"{base_url}/api/webhooks/voice"

        # Get greeting with consent prompt
        twiml = container.voice.get_greeting_twiml(webhook_base)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error("INBOUND_CALL_HANDLER_FAILED", context={"error": str(e)})
        return Response(
            content="<Response><Say language='it-IT'>Errore</Say></Response>",
            media_type="application/xml",
        )


@router.post("/consent")
async def consent_handler(
    background_tasks: BackgroundTasks,
    request: Request,
    digits: str = Form(..., alias="Digits"),  # noqa: N803
    from_phone: str = Form(..., alias="From"),  # noqa: N803
    call_sid: str = Form(..., alias="CallSid"),  # noqa: N803
) -> Response:
    """Handle user consent response."""
    try:
        base_url = str(request.base_url).rstrip("/")
        webhook_base = f"{base_url}/api/webhooks/voice"

        # Get TwiML based on consent
        twiml = container.voice.get_consent_handler_twiml(webhook_base, digits, call_sid)

        # Log consent in background
        consent_given = digits == "1"
        background_tasks.add_task(
            container.voice.log_call_consent,
            call_sid=call_sid,
            phone=from_phone,
            consent_given=consent_given,
        )

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error("CONSENT_HANDLER_FAILED", context={"error": str(e)})
        return Response(
            content="<Response><Say language='it-IT'>Errore</Say><Hangup/></Response>",
            media_type="application/xml",
        )


@router.post("/recording")
async def recording_callback(
    background_tasks: BackgroundTasks,
    recording_url: str = Form(..., alias="RecordingUrl"),  # noqa: N803
    from_phone: str = Form(..., alias="From"),  # noqa: N803
    call_sid: str = Form(..., alias="CallSid"),  # noqa: N803
) -> Response:
    """Handle recording completion and trigger Deepgram transcription."""
    try:
        logger.info(
            "RECORDING_RECEIVED",
            context={"call_sid": call_sid, "url": recording_url},
        )

        # Trigger Deepgram transcription in background
        # (This would use DeepgramAdapter.transcribe_file)
        # For now, we acknowledge receipt

        return Response(content="<Response></Response>", media_type="application/xml")

    except Exception as e:
        logger.error("RECORDING_CALLBACK_FAILED", context={"error": str(e)})
        return Response(content="<Response></Response>", media_type="application/xml")


@router.post("/transcription")
async def transcription_callback(
    background_tasks: BackgroundTasks,
    transcription_text: str = Form(..., alias="TranscriptionText"),  # noqa: N803
    from_phone: str = Form(..., alias="From"),  # noqa: N803
) -> str:
    """Callback from Twilio when transcription is ready (legacy fallback)."""
    try:
        background_tasks.add_task(
            container.voice.handle_transcription,
            transcription_text=transcription_text,
            from_phone=from_phone,
        )
        return "OK"
    except Exception as e:
        logger.error("TRANSCRIPTION_HANDLER_FAILED", context={"error": str(e)})
        return "OK"
