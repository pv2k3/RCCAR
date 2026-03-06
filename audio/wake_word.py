"""
Continuous voice listener with energy-based VAD (Voice Activity Detection).

Always listens. No wake word required.
Detects speech via RMS energy threshold, accumulates audio until silence,
then fires the async on_speech callback with the raw audio array.
"""

import asyncio
import logging
import threading
import numpy as np
from config.settings import settings

logger = logging.getLogger(__name__)

_SAMPLE_RATE     = 16000   # Hz
_CHUNK_SAMPLES   = 512     # ~32 ms per chunk
_SPEECH_THRESHOLD = 0.01   # RMS energy — raise if too sensitive, lower if missing speech
_SILENCE_CHUNKS  = 20      # ~640 ms of silence ends the utterance
_MIN_SPEECH_CHUNKS = 8     # ~256 ms minimum — ignore very short noise bursts
_MAX_SPEECH_SECS = 15      # safety cap — auto-flush after this many seconds


class ContinuousVoiceListener:
    """
    Runs on a background daemon thread.
    Uses RMS energy to detect speech, accumulates audio, then calls
    the async on_speech(audio: np.ndarray) callback with the full utterance.

    Usage:
        listener = ContinuousVoiceListener(on_speech=my_async_fn)
        listener.start(loop)
        ...
        listener.stop()
    """

    def __init__(self, on_speech: callable) -> None:
        self._on_speech = on_speech
        self._running = False
        self._busy = False          # True while Whisper is transcribing
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._running = True
        self._thread = threading.Thread(
            target=self._listen, daemon=True, name="voice-vad"
        )
        self._thread.start()
        logger.info("Continuous voice listener started (threshold=%.3f).", _SPEECH_THRESHOLD)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Continuous voice listener stopped.")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _listen(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice not installed — voice listener disabled.")
            return

        max_chunks = int(_SAMPLE_RATE * _MAX_SPEECH_SECS / _CHUNK_SAMPLES)
        speech_buffer: list[np.ndarray] = []
        silence_count = 0
        in_speech = False

        logger.info("Microphone open — listening continuously.")

        with sd.InputStream(
            samplerate=_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=_CHUNK_SAMPLES,
        ) as stream:
            while self._running:
                chunk, _ = stream.read(_CHUNK_SAMPLES)
                flat = chunk.flatten()
                rms = float(np.sqrt(np.mean(flat ** 2)))

                if rms >= _SPEECH_THRESHOLD:
                    in_speech = True
                    silence_count = 0
                    speech_buffer.append(flat)

                elif in_speech:
                    speech_buffer.append(flat)
                    silence_count += 1

                    if silence_count >= _SILENCE_CHUNKS:
                        self._flush(speech_buffer)
                        speech_buffer = []
                        silence_count = 0
                        in_speech = False

                # Safety cap — flush if recording too long
                if in_speech and len(speech_buffer) >= max_chunks:
                    self._flush(speech_buffer)
                    speech_buffer = []
                    silence_count = 0
                    in_speech = False

    def _flush(self, buffer: list[np.ndarray]) -> None:
        """Send accumulated audio to the callback if long enough and not busy."""
        if len(buffer) < _MIN_SPEECH_CHUNKS:
            return
        if self._busy:
            logger.debug("VAD: utterance detected but STT still busy — skipping.")
            return
        audio = np.concatenate(buffer)
        self._fire(audio)

    def _fire(self, audio: np.ndarray) -> None:
        if self._loop and self._loop.is_running():
            self._busy = True
            future = asyncio.run_coroutine_threadsafe(
                self._on_speech(audio), self._loop
            )
            future.add_done_callback(lambda _: setattr(self, "_busy", False))
