"""
Aura Controller — routes INTENT_CLASSIFIED events to skills, robotics, or TTS.
"""

import logging
from core.event_bus import EventBus, Event, EventType

logger = logging.getLogger(__name__)


class Controller:
    """
    Receives classified intents and dispatches them to the correct handler:
      - chat intents        → speak the LLM reply via TTS
      - movement / stop     → publish MOVEMENT_COMMAND
      - capture_image       → publish FRAME_CAPTURED request
      - registered skills   → execute skill and speak result
      - gestures            → react directly
    """

    def __init__(self, bus: EventBus, skills: list | None = None) -> None:
        self.bus = bus
        # Build a lookup: intent_name -> skill instance
        self._skill_map: dict[str, object] = {}
        for skill in (skills or []):
            for trigger in skill.triggers:
                self._skill_map[trigger] = skill
                logger.debug("Registered skill '%s' for intent '%s'", skill.name, trigger)

        self._register_handlers()
        logger.info(
            "Controller ready. Skills: %d trigger(s) registered.",
            len(self._skill_map),
        )

    def _register_handlers(self) -> None:
        self.bus.subscribe(EventType.INTENT_CLASSIFIED, self._on_intent)
        self.bus.subscribe(EventType.GESTURE_DETECTED, self._on_gesture)
        self.bus.subscribe(EventType.LLM_RESPONSE, self._on_llm_response)
        self.bus.subscribe(EventType.SKILL_DONE, self._on_skill_done)
        self.bus.subscribe(EventType.ERROR, self._on_error)

    # ── Intent routing ────────────────────────────────────────────────────────

    async def _on_intent(self, event: Event) -> None:
        intent = event.payload.get("intent", "chat")
        parameters = event.payload.get("parameters", {})
        confidence = event.payload.get("confidence", 0.0)

        logger.info("Intent: %s (conf=%.2f)", intent, confidence)

        # 1. Speak pre-computed LLM reply (chat / vision paths)
        response_text = event.payload.get("response", "")
        if response_text:
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": str(response_text)},
                source="controller",
            ))
            return  # reply already being spoken — no further action needed

        # 2. Built-in intents
        if intent in ("chat", "vision_chat"):
            pass  # response_text already handled above; nothing else to do

        elif intent == "capture_image":
            await self.bus.publish(Event(
                EventType.FRAME_CAPTURED, {}, source="controller"
            ))

        elif intent == "movement":
            direction = parameters.get("direction", "forward")
            if direction == "turn_left":
                direction = "left"
            elif direction == "turn_right":
                direction = "right"
            await self.bus.publish(Event(
                EventType.MOVEMENT_COMMAND,
                {
                    "direction": direction,
                    "speed": float(parameters.get("speed", 0.7)),
                    "duration": float(parameters.get("duration", 1.0)),
                },
                source="controller",
            ))

        elif intent == "stop":
            await self.bus.publish(Event(
                EventType.MOVEMENT_COMMAND,
                {"direction": "stop", "speed": 0.0},
                source="controller",
            ))

        elif intent == "follow":
            await self.bus.publish(Event(
                EventType.FOLLOW_MODE, {"enabled": True}, source="controller"
            ))
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": "Follow mode activated. I will track and follow you."},
                source="controller",
            ))

        elif intent == "unfollow":
            await self.bus.publish(Event(
                EventType.FOLLOW_MODE, {"enabled": False}, source="controller"
            ))
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": "Follow mode deactivated."},
                source="controller",
            ))

        # 3. Skill dispatch
        elif intent in self._skill_map:
            await self._run_skill(intent, parameters)

        else:
            logger.warning("Unhandled intent: %s", intent)

    # ── Skill execution ───────────────────────────────────────────────────────

    async def _run_skill(self, intent: str, parameters: dict) -> None:
        skill = self._skill_map[intent]
        logger.info("Executing skill '%s'", skill.name)
        try:
            result = await skill.execute(parameters)
            await self.bus.publish(Event(
                EventType.SKILL_DONE,
                {"skill": skill.name, "result": result},
                source="controller",
            ))
        except Exception as exc:
            logger.error("Skill '%s' raised: %s", skill.name, exc, exc_info=True)
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": f"Skill {skill.name} failed."},
                source="controller",
            ))

    async def _on_skill_done(self, event: Event) -> None:
        """Speak skill result back to the user."""
        result = event.payload.get("result", {})
        message = result.get("message", "") if isinstance(result, dict) else str(result)
        if message:
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": message},
                source="controller",
            ))

    # ── Gesture reactions ────────────────────────────────────────────────────

    async def _on_gesture(self, event: Event) -> None:
        gesture = event.payload.get("gesture", "")
        if gesture == "open_palm":
            logger.info("Gesture: open_palm → stop")
            await self.bus.publish(Event(
                EventType.MOVEMENT_COMMAND,
                {"direction": "stop", "speed": 0.0},
                source="controller",
            ))
        elif gesture == "thumbs_up":
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": "Thumbs up!"},
                source="controller",
            ))

    # ── Passthrough / error ──────────────────────────────────────────────────

    async def _on_llm_response(self, event: Event) -> None:
        """Log LLM_RESPONSE events. TTS is handled upstream by the event source."""
        result = event.payload.get("result", {})
        logger.debug("LLM_RESPONSE received: keys=%s", list(result.keys()) if isinstance(result, dict) else type(result))

    async def _on_error(self, event: Event) -> None:
        source = event.payload.get("source", "unknown")
        message = event.payload.get("message", "")
        logger.error("System error from %s: %s", source, message)
