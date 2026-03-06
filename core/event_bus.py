"""
Aura Event Bus — async publish/subscribe system.

All modules communicate exclusively through this bus.
No module imports another module directly for runtime data.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All system event types."""

    # ── Voice ─────────────────────────────────────────────────────────────────
    WAKE_WORD_DETECTED = auto()
    SPEECH_TEXT = auto()          # STT completed, payload: {"text": str}
    TTS_SPEAK = auto()            # Request TTS output, payload: {"text": str}
    TTS_DONE = auto()

    # ── Vision ────────────────────────────────────────────────────────────────
    OBJECTS_DETECTED = auto()     # payload: {"objects": list[dict]}
    FACE_DETECTED = auto()        # payload: {"faces": list[dict]}
    GESTURE_DETECTED = auto()     # payload: {"gesture": str}
    FRAME_CAPTURED = auto()       # payload: {"path": str}

    # ── LLM ───────────────────────────────────────────────────────────────────
    LLM_REQUEST = auto()          # payload: {"text": str, "image_path": str|None}
    LLM_RESPONSE = auto()         # payload: {"result": dict}
    INTENT_CLASSIFIED = auto()    # payload: {"intent": str, "confidence": float, "parameters": dict}

    # ── Skills / Actions ──────────────────────────────────────────────────────
    SKILL_TRIGGER = auto()        # payload: {"skill": str, "parameters": dict}
    SKILL_DONE = auto()           # payload: {"skill": str, "result": Any}

    # ── Robotics ──────────────────────────────────────────────────────────────
    MOVEMENT_COMMAND = auto()     # payload: {"direction": str, "speed": float, "duration": float}
    MOVEMENT_DONE = auto()
    DISTANCE_UPDATE = auto()      # payload: {"front": float, "back": float}  (cm)
    FOLLOW_MODE = auto()          # payload: {"enabled": bool}
    TRACKING_UPDATE = auto()      # payload: {"detected": bool, "offset_x": float, "area_ratio": float, "bbox": dict|None}

    # ── System ────────────────────────────────────────────────────────────────
    SYSTEM_READY = auto()
    SYSTEM_SHUTDOWN = auto()
    ERROR = auto()                # payload: {"source": str, "message": str}


@dataclass
class Event:
    """An event published on the bus."""

    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"


# Type alias for async subscriber callbacks
Subscriber = Callable[[Event], Coroutine]


class EventBus:
    """
    Central async event bus using asyncio.Queue.

    Usage:
        bus = EventBus()

        # Subscribe
        await bus.subscribe(EventType.SPEECH_TEXT, my_async_handler)

        # Publish
        await bus.publish(Event(EventType.SPEECH_TEXT, {"text": "hello"}, source="voice"))

        # Run dispatch loop (call once in main)
        await bus.run()
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._subscribers: dict[EventType, list[Subscriber]] = {}
        self._running = False

    def subscribe(self, event_type: EventType, callback: Subscriber) -> None:
        """Register an async callback for an event type."""
        self._subscribers.setdefault(event_type, []).append(callback)
        logger.debug("Subscribed %s → %s", callback.__qualname__, event_type.name)

    async def publish(self, event: Event) -> None:
        """Put an event on the queue (non-blocking)."""
        await self._queue.put(event)
        logger.debug("Published %s from %s", event.type.name, event.source)

    async def run(self) -> None:
        """
        Dispatch loop — call once as an asyncio task.
        Processes events from the queue and calls all subscribers.
        """
        self._running = True
        logger.info("EventBus dispatch loop started.")

        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            subscribers = self._subscribers.get(event.type, [])
            for callback in subscribers:
                try:
                    await callback(event)
                except Exception as exc:
                    logger.error(
                        "Subscriber %s failed on %s: %s",
                        callback.__qualname__,
                        event.type.name,
                        exc,
                        exc_info=True,
                    )
            self._queue.task_done()

    def stop(self) -> None:
        """Signal the dispatch loop to exit."""
        self._running = False
        logger.info("EventBus stopped.")
