"""
Navigation — high-level movement logic built on top of MotorController.

Handles:
  - MOVEMENT_COMMAND events (manual chat / gesture control)
  - DISTANCE_UPDATE events (safety: stop if obstacle too close)
  - FOLLOW_MODE events (toggle person-following)
  - TRACKING_UPDATE events (auto-steer/drive to follow a detected person)
"""

import asyncio
import logging
import time

from config.settings import settings
from core.event_bus import EventBus, Event, EventType
from robotics.motor_control import MotorController

logger = logging.getLogger(__name__)

# Minimum seconds between auto-movement commands (prevents command spam at 5 fps)
_FOLLOW_COOLDOWN = 0.4


class Navigator:
    """
    Receives movement events and translates them into motor commands.

    Follow mode logic (activated via "follow me" chat command):
      1. TRACKING_UPDATE fires at ~5 fps from VisionService
      2. Latest DISTANCE_UPDATE is stored for safety checks
      3. On each tracking update:
           - Front obstacle < OBSTACLE_STOP_DISTANCE → emergency stop
           - Person offset_x outside deadzone → turn left / right
           - Person area_ratio < TRACKING_AREA_TOO_FAR → move forward
           - Person area_ratio > TRACKING_AREA_TOO_CLOSE → move backward
           - Person centered + good distance → stop (hold position)
           - No person detected → stop and wait
    """

    DEFAULT_DURATION = 1.0

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self._motor = MotorController()
        self._moving = False
        self._follow_mode = False
        self._last_follow_cmd = 0.0
        self._distances = {"front": 999.0, "back": 999.0}

        self.bus.subscribe(EventType.MOVEMENT_COMMAND, self._on_movement_command)
        self.bus.subscribe(EventType.DISTANCE_UPDATE, self._on_distance_update)
        self.bus.subscribe(EventType.FOLLOW_MODE, self._on_follow_mode)
        self.bus.subscribe(EventType.TRACKING_UPDATE, self._on_tracking_update)

    def connect(self) -> bool:
        return self._motor.connect()

    def disconnect(self) -> None:
        self._motor.disconnect()

    # ── Manual movement ───────────────────────────────────────────────────────

    async def _on_movement_command(self, event: Event) -> None:
        direction = event.payload.get("direction", "stop")
        speed = float(event.payload.get("speed", 1.0))
        duration = float(event.payload.get("duration", self.DEFAULT_DURATION))

        if direction == "stop":
            await self.stop()
            return
        await self.move(direction, speed, duration)

    async def move(self, direction: str, speed: float = 1.0, duration: float = 1.0) -> None:
        """Move in a direction for duration seconds, then stop."""
        if self._moving:
            await self._motor.stop()

        self._moving = True
        logger.info("Moving %s speed=%.1f for %.1fs", direction, speed, duration)
        await self._motor.move(direction, speed)
        await asyncio.sleep(duration)
        await self._motor.stop()
        self._moving = False
        await self.bus.publish(Event(EventType.MOVEMENT_DONE, {}, source="navigator"))

    async def stop(self) -> None:
        self._moving = False
        await self._motor.stop()
        logger.info("Navigation stopped.")
        await self.bus.publish(Event(EventType.MOVEMENT_DONE, {}, source="navigator"))

    # ── Distance sensor ───────────────────────────────────────────────────────

    async def _on_distance_update(self, event: Event) -> None:
        self._distances = event.payload
        front = self._distances.get("front", 999.0)

        # Safety: emergency stop if obstacle too close
        if front < settings.obstacle_stop_distance and self._moving:
            logger.warning(
                "Obstacle at %.1f cm (threshold %.1f cm) — emergency stop!",
                front, settings.obstacle_stop_distance,
            )
            await self.stop()
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": "Obstacle detected — stopping!"},
                source="navigator",
            ))

    # ── Follow mode ───────────────────────────────────────────────────────────

    async def _on_follow_mode(self, event: Event) -> None:
        self._follow_mode = event.payload.get("enabled", False)
        if not self._follow_mode:
            await self.stop()
        logger.info("Navigator follow mode: %s", "ON" if self._follow_mode else "OFF")

    async def _on_tracking_update(self, event: Event) -> None:
        """React to person tracking data when follow mode is active."""
        if not self._follow_mode:
            return

        now = time.monotonic()
        if now - self._last_follow_cmd < _FOLLOW_COOLDOWN:
            return  # debounce — don't spam commands at 5 fps

        detected = event.payload.get("detected", False)
        offset_x = event.payload.get("offset_x", 0.0)
        area_ratio = event.payload.get("area_ratio", 0.0)

        front_dist = self._distances.get("front", 999.0)

        if not detected:
            # Person lost — stop and wait
            if self._moving:
                await self.stop()
            return

        # ── Safety gate ───────────────────────────────────────────────────────
        if front_dist < settings.obstacle_stop_distance:
            if self._moving:
                await self._motor.stop()
                self._moving = False
            return

        deadzone = settings.tracking_center_deadzone
        too_far = settings.tracking_area_too_far
        too_close = settings.tracking_area_too_close

        self._last_follow_cmd = now

        # ── Steering ──────────────────────────────────────────────────────────
        if offset_x > deadzone:
            logger.debug("Follow: turn right (offset=%.2f)", offset_x)
            await self._motor.move("right", 0.5)
            await asyncio.sleep(0.2)
            await self._motor.stop()

        elif offset_x < -deadzone:
            logger.debug("Follow: turn left (offset=%.2f)", offset_x)
            await self._motor.move("left", 0.5)
            await asyncio.sleep(0.2)
            await self._motor.stop()

        # ── Distance control ──────────────────────────────────────────────────
        elif area_ratio < too_far:
            logger.debug("Follow: move forward (area=%.3f)", area_ratio)
            await self._motor.move("forward", 0.6)
            await asyncio.sleep(0.3)
            await self._motor.stop()

        elif area_ratio > too_close:
            logger.debug("Follow: move backward (area=%.3f)", area_ratio)
            await self._motor.move("backward", 0.5)
            await asyncio.sleep(0.2)
            await self._motor.stop()

        else:
            # Centred and correct distance — hold position
            if self._moving:
                await self._motor.stop()
                self._moving = False
