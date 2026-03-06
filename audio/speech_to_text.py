"""
Speech-to-Text using faster-whisper (CTranslate2 backend).
Supports CPU int8 inference for fast transcription without a GPU.
"""

import asyncio
import logging
import numpy as np
from config.settings import settings

logger = logging.getLogger(__name__)


class SpeechToText:
    """
    Records audio from the microphone and transcribes it with Whisper.
    Lazy-loads the model on first use.
    """

    def __init__(self) -> None:
        self._model = None
        self._model_size = settings.whisper_model_size
        self._device = settings.whisper_device
        self._compute_type = settings.whisper_compute_type
        self._sample_rate = settings.audio_sample_rate

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            logger.info("Loading Whisper model: %s (%s)", self._model_size, self._device)
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )
            logger.info("Whisper model loaded.")

    def record_audio(self, duration: int | None = None) -> np.ndarray:
        """
        Record audio from the default microphone.

        Args:
            duration: Seconds to record. Defaults to settings.audio_record_duration.

        Returns:
            Flat float32 numpy array.
        """
        import sounddevice as sd

        secs = duration or settings.audio_record_duration
        logger.info("Recording %ds of audio...", secs)

        audio = sd.rec(
            int(secs * self._sample_rate),
            samplerate=self._sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        logger.info("Recording complete.")
        return audio.flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Convert a float32 audio array to text.

        Args:
            audio: Flat float32 numpy array at 16 kHz.

        Returns:
            Transcribed string.
        """
        self._load_model()
        segments, _ = self._model.transcribe(audio, language="en")
        text = " ".join(seg.text.strip() for seg in segments)
        logger.info("Transcribed: %s", text)
        return text.strip()

    async def listen_and_transcribe(self, duration: int | None = None) -> str:
        """
        Async wrapper: record then transcribe in an executor thread.
        Safe to call from an asyncio event loop without blocking.
        """
        loop = asyncio.get_running_loop()
        secs = duration or settings.audio_record_duration

        audio = await loop.run_in_executor(None, self.record_audio, secs)
        return await loop.run_in_executor(None, self.transcribe, audio)
