"""Deepgram adapter for real-time Italian speech-to-text transcription."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from deepgram import DeepgramClient, DeepgramClientOptions, LiveOptions, LiveTranscriptionEvents

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class DeepgramAdapter:
    """Adapter for Deepgram Nova-3 Italian transcription."""

    MODEL = "nova-3"
    LANGUAGE = "it"

    def __init__(self) -> None:
        """Initialize Deepgram client."""
        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY, config)

    async def stream_transcription(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """Stream audio to Deepgram and yield Italian transcripts in real-time.

        Args:
            audio_stream: Async generator yielding audio chunks (20ms from Twilio)

        Yields:
            Transcribed text segments
        """
        try:
            # Configure live transcription options for Italian
            options = LiveOptions(
                model=self.MODEL,
                language=self.LANGUAGE,
                encoding="mulaw",  # Twilio uses µ-law
                sample_rate=8000,  # Twilio standard
                channels=1,
                interim_results=True,
                punctuate=True,
                smart_format=True,
            )

            # Create live connection
            dg_connection = self.client.listen.live.v("1")

            # Setup transcript handler
            transcripts: asyncio.Queue[str] = asyncio.Queue()

            def on_message(self: object, result: dict[str, Any], **kwargs: dict[str, Any]) -> None:
                """Handle incoming transcript."""
                sentence = result["channel"]["alternatives"][0]["transcript"]
                if len(sentence) > 0:
                    if result.get("is_final", False):
                        asyncio.create_task(transcripts.put(sentence))
                        logger.info("DEEPGRAM_TRANSCRIPT", context={"text": sentence})

            def on_error(self: object, error: Exception, **kwargs: dict[str, Any]) -> None:
                """Handle errors."""
                logger.error("DEEPGRAM_ERROR", context={"error": str(error)})

            # Register event handlers
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            # Start connection
            if not await dg_connection.start(options):
                logger.error("DEEPGRAM_START_FAILED")
                return

            logger.info("DEEPGRAM_STREAM_STARTED")

            # Forward audio chunks
            try:
                async for chunk in audio_stream:
                    await dg_connection.send(chunk)

                    # Yield any available transcripts
                    while not transcripts.empty():
                        yield await transcripts.get()

            finally:
                # Flush remaining transcripts
                while not transcripts.empty():
                    yield await transcripts.get()

                # Close connection
                await dg_connection.finish()
                logger.info("DEEPGRAM_STREAM_CLOSED")

        except Exception as e:
            logger.error("DEEPGRAM_STREAM_ERROR", context={"error": str(e)})
            raise

    async def transcribe_file(self, audio_url: str) -> str:
        """Batch transcription for recordings (post-call).

        Args:
            audio_url: URL to audio file (e.g., Twilio recording)

        Returns:
            Full transcript text
        """
        try:
            # Configure prerecorded options
            options = {
                "model": self.MODEL,
                "language": self.LANGUAGE,
                "punctuate": True,
                "smart_format": True,
            }

            logger.info("DEEPGRAM_FILE_TRANSCRIPTION", context={"url": audio_url})

            # Send URL-based transcription request
            response = await self.client.listen.prerecorded.v("1").transcribe_url(
                {"url": audio_url}, options
            )

            # Extract transcript
            transcript = str(response.results.channels[0].alternatives[0].transcript)

            logger.info(
                "DEEPGRAM_FILE_COMPLETE",
                context={"url": audio_url, "length": len(transcript)},
            )

            return transcript

        except Exception as e:
            logger.error("DEEPGRAM_FILE_ERROR", context={"error": str(e), "url": audio_url})
            raise
