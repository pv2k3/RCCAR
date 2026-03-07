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

# ── Search behavior constants ─────────────────────────────────────────────────
_SEARCH_ROTATE_DURATION = 0.5    # seconds to rotate per scan step
_SEARCH_ROTATE_SPEED    = 0.45   # motor speed while scanning
_SEARCH_STEPS_PER_SWEEP = 8      # 8 steps ≈ full 360° rotation
_SEARCH_MAX_SWEEPS      = 3      # give up after this many full sweeps
_SEARCH_FORWARD_DURATION = 1.0   # seconds to advance between sweeps
_SEARCH_FORWARD_SPEED   = 0.5
_SEARCH_APPROACH_AREA   = 0.12   # area_ratio threshold = "close enough"
_SEARCH_APPROACH_DEADZONE = 0.25 # |offset_x| threshold for steering correction


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

        # Search state
        self._search_mode = False
        self._search_target = ""
        self._search_task: asyncio.Task | None = None
        self._last_detections: list[dict] = []
        self._last_det_frame_w: int = 640
        self._last_det_frame_h: int = 480

        self.bus.subscribe(EventType.MOVEMENT_COMMAND, self._on_movement_command)
        self.bus.subscribe(EventType.DISTANCE_UPDATE, self._on_distance_update)
        self.bus.subscribe(EventType.FOLLOW_MODE, self._on_follow_mode)
        self.bus.subscribe(EventType.TRACKING_UPDATE, self._on_tracking_update)
        self.bus.subscribe(EventType.SEARCH_MODE, self._on_search_mode)
        self.bus.subscribe(EventType.OBJECTS_DETECTED, self._on_objects_detected)

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

    # ── Search mode ───────────────────────────────────────────────────────────

    async def _on_objects_detected(self, event: Event) -> None:
        """Cache the latest detections for use by the search loop."""
        self._last_detections = event.payload.get("objects", [])
        self._last_det_frame_w = event.payload.get("frame_w", 640) or 640
        self._last_det_frame_h = event.payload.get("frame_h", 480) or 480

    async def _on_search_mode(self, event: Event) -> None:
        """Start or stop an autonomous object search."""
        enabled = event.payload.get("enabled", False)
        target  = event.payload.get("target", "").lower().strip()

        if not enabled:
            self._search_mode = False
            if self._search_task and not self._search_task.done():
                self._search_task.cancel()
            await self.stop()
            logger.info("Search mode deactivated.")
            return

        # Cancel any running search before starting a new one
        if self._search_task and not self._search_task.done():
            self._search_task.cancel()

        self._search_mode = True
        self._search_target = target
        self._search_task = asyncio.create_task(self._search_loop())
        logger.info("Search mode started — target: '%s'", target)

    def _find_target_in_detections(self) -> dict | None:
        """
        Scan cached detections for the search target.
        Returns an enriched dict with offset_x and area_ratio, or None.
        """
        fw = self._last_det_frame_w
        fh = self._last_det_frame_h
        target = self._search_target

        for det in self._last_detections:
            label = det.get("label", "").lower()
            # Accept exact match, partial overlap, or plural/singular variation
            if label == target or target in label or label in target:
                x1, y1, x2, y2 = det["bbox"]
                cx = (x1 + x2) / 2
                offset_x  = (cx / fw - 0.5) * 2.0
                area_ratio = ((x2 - x1) * (y2 - y1)) / (fw * fh)
                return {
                    "label":      label,
                    "offset_x":   round(offset_x, 3),
                    "area_ratio": round(area_ratio, 4),
                    "bbox":       det["bbox"],
                }
        return None

    async def _speak(self, text: str) -> None:
        await self.bus.publish(Event(EventType.TTS_SPEAK, {"text": text}, source="navigator"))

    async def _search_loop(self) -> None:
        """
        Autonomous search state machine:
          Scan frame  →  rotate a step  →  repeat
          After STEPS_PER_SWEEP steps  →  move forward
          After MAX_SWEEPS full sweeps →  give up
          Object found at any point    →  hand off to _approach_target
        """
        target = self._search_target
        logger.info("Search loop running for: %s", target)
        await self._speak(f"Starting search for {target}. I will rotate and scan the area.")

        total_steps = 0
        max_steps   = _SEARCH_STEPS_PER_SWEEP * _SEARCH_MAX_SWEEPS

        try:
            while self._search_mode and total_steps < max_steps:
                # Let the vision pipeline deliver the latest frame first
                await asyncio.sleep(0.35)

                found = self._find_target_in_detections()
                if found:
                    logger.info("Search: found '%s' — switching to approach.", target)
                    await self._speak(f"Found the {target}! Moving toward it.")
                    await self._approach_target()
                    return

                # Rotate right by one step to scan a new slice
                logger.debug("Search: step %d/%d — rotating.", total_steps + 1, max_steps)
                self._moving = True
                await self._motor.move("right", _SEARCH_ROTATE_SPEED)
                await asyncio.sleep(_SEARCH_ROTATE_DURATION)
                await self._motor.stop()
                self._moving = False

                total_steps += 1

                # After a full 360° sweep, advance to a new position
                if total_steps % _SEARCH_STEPS_PER_SWEEP == 0:
                    sweep_num = total_steps // _SEARCH_STEPS_PER_SWEEP
                    front = self._distances.get("front", 999.0)
                    await self._speak(
                        f"Completed sweep {sweep_num} of {_SEARCH_MAX_SWEEPS}. "
                        f"Moving forward to search a new area."
                    )
                    if front > settings.obstacle_stop_distance:
                        self._moving = True
                        await self._motor.move("forward", _SEARCH_FORWARD_SPEED)
                        await asyncio.sleep(_SEARCH_FORWARD_DURATION)
                        await self._motor.stop()
                        self._moving = False
                    else:
                        await self._speak("Obstacle ahead — trying a different angle.")
                        self._moving = True
                        await self._motor.move("left", _SEARCH_ROTATE_SPEED)
                        await asyncio.sleep(_SEARCH_ROTATE_DURATION * 2)
                        await self._motor.stop()
                        self._moving = False

            # Exhausted all steps without finding the target
            if self._search_mode:
                logger.info("Search: '%s' not found after %d steps.", target, max_steps)
                await self._speak(
                    f"I could not find the {target} after searching the entire area."
                )
                self._search_mode = False
                await self.bus.publish(Event(
                    EventType.SEARCH_DONE,
                    {"found": False, "target": target},
                    source="navigator",
                ))

        except asyncio.CancelledError:
            logger.info("Search loop cancelled.")
            await self._motor.stop()
            self._moving = False

    async def _approach_target(self) -> None:
        """
        Steer toward the detected target and drive until close enough.
        Falls back to the search loop if the target is lost mid-approach.
        """
        target = self._search_target

        for _ in range(20):
            if not self._search_mode:
                return

            await asyncio.sleep(0.25)

            found = self._find_target_in_detections()
            if found is None:
                # Target temporarily out of view — wait one extra frame
                await asyncio.sleep(0.4)
                found = self._find_target_in_detections()
                if found is None:
                    logger.warning("Approach: lost '%s' — returning to search.", target)
                    await self._speak(f"Lost sight of the {target}. Resuming search.")
                    # Restart the search loop
                    self._search_task = asyncio.create_task(self._search_loop())
                    return

            offset_x   = found["offset_x"]
            area_ratio = found["area_ratio"]
            front      = self._distances.get("front", 999.0)

            # Close enough — stop
            if area_ratio >= _SEARCH_APPROACH_AREA or front < settings.obstacle_stop_distance:
                await self._motor.stop()
                self._moving = False
                await self._speak(f"I have reached the {target}.")
                self._search_mode = False
                await self.bus.publish(Event(
                    EventType.SEARCH_DONE,
                    {"found": True, "target": target},
                    source="navigator",
                ))
                return

            # Steer toward the target centre before advancing
            if abs(offset_x) > _SEARCH_APPROACH_DEADZONE:
                direction = "right" if offset_x > 0 else "left"
                self._moving = True
                await self._motor.move(direction, 0.4)
                await asyncio.sleep(0.25)
                await self._motor.stop()
                self._moving = False
            else:
                # Centred — move forward
                self._moving = True
                await self._motor.move("forward", 0.5)
                await asyncio.sleep(0.4)
                await self._motor.stop()
                self._moving = False

        # Reached the step limit — declare success at best-effort position
        await self._speak(f"I am as close as I can get to the {target}.")
        self._search_mode = False
        await self.bus.publish(Event(
            EventType.SEARCH_DONE,
            {"found": True, "target": target},
            source="navigator",
        ))
