"""
Voice Service — manages the full voice pipeline:
  always-on VAD listener → Whisper STT → publish SPEECH_TEXT event
  TTS_SPEAK event → synthesise and play audio
"""

import asyncio
import logging
import numpy as np

from core.event_bus import EventBus, Event, EventType
from audio.speech_to_text import SpeechToText
from audio.text_to_speech import TextToSpeech
from audio.wake_word import ContinuousVoiceListener

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Listens continuously for speech (no wake word needed).
    When an utterance is detected by the VAD, transcribes it with Whisper
    and publishes a SPEECH_TEXT event.
    Also handles TTS_SPEAK events by speaking the text.
    """

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self._stt = SpeechToText()
        self._tts = TextToSpeech()
        self._listener = ContinuousVoiceListener(on_speech=self._on_speech)
        self._loop: asyncio.AbstractEventLoop | None = None

        self.bus.subscribe(EventType.TTS_SPEAK, self._on_tts_speak)
        self.bus.subscribe(EventType.TTS_DONE, self._on_tts_done)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._listener.start(loop)
        logger.info("VoiceService started — always listening.")

    def stop(self) -> None:
        self._listener.stop()
        logger.info("VoiceService stopped.")

    # ── Speech callback ───────────────────────────────────────────────────────

    async def _on_speech(self, audio: np.ndarray) -> None:
        """
        Called by ContinuousVoiceListener when an utterance is ready.
        Transcribes with Whisper, publishes SPEECH_TEXT if non-empty.
        """
        try:
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(None, self._stt.transcribe, audio)
            if text:
                logger.info("STT: %s", text)
                await self.bus.publish(Event(
                    EventType.SPEECH_TEXT,
                    {"text": text},
                    source="voice_service",
                ))
        except Exception as exc:
            logger.error("STT failed: %s", exc)
            await self.bus.publish(Event(
                EventType.ERROR,
                {"source": "voice_service", "message": str(exc)},
                source="voice_service",
            ))

    # ── TTS handlers ──────────────────────────────────────────────────────────

    async def _on_tts_speak(self, event: Event) -> None:
        text = event.payload.get("text", "")
        if text:
            try:
                await self._tts.speak(text)
                await self.bus.publish(Event(EventType.TTS_DONE, {}, source="voice_service"))
            except Exception as exc:
                logger.error("TTS failed: %s", exc)

    async def _on_tts_done(self, event: Event) -> None:
        logger.debug("TTS playback complete.")
