"""
Text-to-Speech with two backends:
  - edge-tts  (default): async, neural voices, requires internet
  - pyttsx3   (fallback): fully offline, lower quality

Backend is selected via settings.tts_offline_fallback.
"""

import asyncio
import logging
import tempfile
import os
from config.settings import settings

logger = logging.getLogger(__name__)


class TextToSpeech:
    """
    Converts text to spoken audio.
    Uses edge-tts by default; falls back to pyttsx3 when offline mode is set.
    """

    def __init__(self) -> None:
        self._voice = settings.tts_voice
        self._rate = settings.tts_rate
        self._offline = settings.tts_offline_fallback
        self._pyttsx3_engine = None

    # ── Public API ────────────────────────────────────────────────────────────

    async def speak(self, text: str) -> None:
        """
        Speak the given text aloud.

        Args:
            text: Plain text string to synthesise.
        """
        if not text.strip():
            return

        if self._offline:
            await self._speak_offline(text)
        else:
            await self._speak_online(text)

    # ── edge-tts (online) ────────────────────────────────────────────────────

    async def _speak_online(self, text: str) -> None:
        """Generate audio with edge-tts and play it."""
        try:
            import edge_tts
            import pygame

            communicate = edge_tts.Communicate(text, self._voice, rate=self._rate)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name

            await communicate.save(tmp_path)
            await self._play_audio(tmp_path)

        except ImportError:
            logger.warning("edge-tts or pygame not installed; switching to offline TTS.")
            await self._speak_offline(text)
        except Exception as exc:
            logger.error("edge-tts failed: %s", exc)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    async def _play_audio(self, path: str) -> None:
        """Play an audio file asynchronously using pygame."""
        loop = asyncio.get_running_loop()

        def _play():
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.05)
            pygame.mixer.music.stop()
            pygame.mixer.quit()

        await loop.run_in_executor(None, _play)

    # ── pyttsx3 (offline) ────────────────────────────────────────────────────

    async def _speak_offline(self, text: str) -> None:
        """Synthesise and play text with pyttsx3 (blocking, run in executor)."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._pyttsx3_say, text)

    def _pyttsx3_say(self, text: str) -> None:
        try:
            import pyttsx3
            if self._pyttsx3_engine is None:
                self._pyttsx3_engine = pyttsx3.init()
            self._pyttsx3_engine.say(text)
            self._pyttsx3_engine.runAndWait()
        except Exception as exc:
            logger.error("pyttsx3 failed: %s", exc)
