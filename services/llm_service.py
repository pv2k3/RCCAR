"""
LLM Service — receives SPEECH_TEXT events, decides whether visual context
is needed (auto-captures a frame if so), calls the AI engine, and publishes
INTENT_CLASSIFIED + LLM_RESPONSE events.
"""

import logging
import time
import os

from core.event_bus import EventBus, Event, EventType
from ai.ai_engine import AIEngine

logger = logging.getLogger(__name__)


class LLMService:
    """
    Bridge between the event bus and the AI engine.

    Auto-vision logic:
      - If the user's text triggers needs_vision(), a frame is grabbed from
        VisionService and the query is sent as a multimodal (image+text) call.
      - Otherwise standard chat / intent flow is used.
    """

    def __init__(self, bus: EventBus, vision_service=None) -> None:
        self.bus = bus
        self._engine = AIEngine()
        self._vision = vision_service   # optional VisionService reference

        self.bus.subscribe(EventType.SPEECH_TEXT, self._on_speech_text)
        self.bus.subscribe(EventType.LLM_REQUEST, self._on_llm_request)

        logger.info("LLMService initialized.")

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def _on_speech_text(self, event: Event) -> None:
        """
        Handle transcribed speech.

        Decision tree:
          1. If text needs visual context → capture frame → chat_with_vision()
          2. Else classify intent:
             a. chat     → chat() for conversational reply
             b. capture_image / vision_analysis → capture + analyze_vision()
             c. movement / stop / other → process() for structured params
        """
        text = event.payload.get("text", "").strip()
        if not text:
            return

        logger.info("LLMService processing: %s", text)

        try:
            # ── Path 1: vision keywords detected ─────────────────────────────
            if self._engine.needs_vision(text) and self._vision is not None:
                image_path = self._capture_frame()
                if image_path:
                    logger.info("Auto-captured frame for vision query: %s", image_path)
                    result = await self._engine.chat_with_vision(image_path, text)
                    reply = (
                        result.get("response")
                        or result.get("answer")
                        or result.get("message")
                        or ""
                    )
                    await self._publish_response(result)
                    await self.bus.publish(Event(
                        EventType.INTENT_CLASSIFIED,
                        {"intent": "vision_chat", "confidence": 1.0,
                         "parameters": {}, "response": reply},
                        source="llm_service",
                    ))
                    return

            # ── Path 2: standard intent classification ────────────────────────
            intent_result = await self._engine.process(text)
            intent = intent_result.get("intent", "chat")
            confidence = intent_result.get("confidence", 0.0)
            parameters = intent_result.get("parameters", {})

            payload = {
                "intent": intent,
                "confidence": confidence,
                "parameters": parameters,
            }

            if intent == "chat":
                chat_result = await self._engine.chat(text)
                reply = chat_result.get("message") or chat_result.get("response") or ""
                payload["response"] = reply
                await self._publish_response(chat_result)

            elif intent in ("capture_image", "vision_analysis"):
                image_path = self._capture_frame()
                if image_path:
                    result = await self._engine.analyze_vision(image_path, text)
                    reply = result.get("description") or result.get("response") or ""
                    payload["response"] = reply
                    await self._publish_response(result)
                else:
                    payload["response"] = "Camera is not available."
                    await self.bus.publish(Event(
                        EventType.TTS_SPEAK,
                        {"text": "Camera is not available right now."},
                        source="llm_service",
                    ))

            # movement / stop / other intents have no LLM spoken reply;
            # the controller handles them via INTENT_CLASSIFIED

            await self.bus.publish(Event(
                EventType.INTENT_CLASSIFIED,
                payload,
                source="llm_service",
            ))

        except Exception as exc:
            logger.error("LLMService error: %s", exc, exc_info=True)
            await self.bus.publish(Event(
                EventType.ERROR,
                {"source": "llm_service", "message": str(exc)},
                source="llm_service",
            ))

    async def _on_llm_request(self, event: Event) -> None:
        """
        Handle explicit LLM_REQUEST events (from the API or skills).
        Supports optional image_path for vision chat.
        """
        text = event.payload.get("text", "").strip()
        image_path = event.payload.get("image_path")

        if not text:
            return

        try:
            if image_path:
                result = await self._engine.chat_with_vision(image_path, text)
            elif self._engine.needs_vision(text) and self._vision is not None:
                captured = self._capture_frame()
                result = (
                    await self._engine.chat_with_vision(captured, text)
                    if captured
                    else await self._engine.chat(text)
                )
            else:
                result = await self._engine.chat(text)

            await self.bus.publish(Event(
                EventType.LLM_RESPONSE,
                {"result": result},
                source="llm_service",
            ))
            reply = (
                result.get("response")
                or result.get("message")
                or result.get("answer")
                or ""
            )
            if reply:
                await self.bus.publish(Event(
                    EventType.TTS_SPEAK,
                    {"text": str(reply)},
                    source="llm_service",
                ))
        except Exception as exc:
            logger.error("LLM request failed: %s", exc, exc_info=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _publish_response(self, result: dict) -> None:
        """Publish LLM_RESPONSE only. TTS is handled by the controller via INTENT_CLASSIFIED."""
        await self.bus.publish(Event(
            EventType.LLM_RESPONSE,
            {"result": result},
            source="llm_service",
        ))

    def _capture_frame(self) -> str | None:
        """
        Grab the latest frame from VisionService and save to captured_images/.
        Returns the saved file path, or None if camera is unavailable.
        """
        if self._vision is None:
            return None
        frame = self._vision.get_frame()
        if frame is None:
            return None
        try:
            import cv2
            os.makedirs("captured_images", exist_ok=True)
            path = f"captured_images/auto_{int(time.time() * 1000)}.jpg"
            cv2.imwrite(path, frame)
            return path
        except Exception as exc:
            logger.error("Auto-capture failed: %s", exc)
            return None
