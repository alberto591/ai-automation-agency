from fastapi import APIRouter, BackgroundTasks, Form, Request, Response

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/voice", tags=["Voice"])


@router.post("/inbound")
async def inbound_call(request: Request) -> Response:
    """
    Handles incoming calls from Twilio.
    Returns TwiML to greet and record.
    """
    try:
        # Twilio sends form data
        form_data = await request.form()
        from_phone = form_data.get("From", "Unknown")

        logger.info("INBOUND_CALL_RECEIVED", context={"from": from_phone})

        # Construct the base URL for the callback
        # In Vercel/Prod, this should be the public URL
        # We can try to infer it from request.base_url or use a setting
        base_url = str(request.base_url).rstrip("/")
        webhook_base = f"{base_url}/api/webhooks/voice"

        # Generate TwiML
        twiml = container.voice.get_greeting_twiml(webhook_base)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error("INBOUND_CALL_HANDLER_FAILED", context={"error": str(e)})
        return Response(
            content="<Response><Say>Error</Say></Response>", media_type="application/xml"
        )


@router.post("/transcription")
async def transcription_callback(
    background_tasks: BackgroundTasks,
    transcription_text: str = Form(..., alias="TranscriptionText"),  # noqa: N803
    from_phone: str = Form(..., alias="From"),  # noqa: N803
) -> str:
    """
    Callback from Twilio when transcription is ready.
    """
    try:
        # Process in background
        background_tasks.add_task(
            container.voice.handle_transcription,
            transcription_text=transcription_text,
            from_phone=from_phone,
        )
        return "OK"
    except Exception as e:
        logger.error("TRANSCRIPTION_HANDLER_FAILED", context={"error": str(e)})
        # Return 200 to Twilio anyway so they stop retrying
        return "OK"
