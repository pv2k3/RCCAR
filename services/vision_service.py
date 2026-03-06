"""
Vision Service — runs all vision modules in a background thread
and publishes detections to the event bus.

Supports:
  - Local webcam (CAMERA_INDEX) or network stream (RC_VIDEO_URL)
  - Object detection (YOLO), face detection (OpenCV), gesture detection (MediaPipe)
  - Person tracking / follow mode: publishes TRACKING_UPDATE when FOLLOW_MODE is active
"""

import asyncio
import logging
import threading
import time
import os
import cv2
import numpy as np

from config.settings import settings
from core.event_bus import EventBus, Event, EventType
from vision.object_detection import ObjectDetector
from vision.face_recognition import FaceDetector
from vision.gesture_detection import GestureDetector
from vision.person_tracker import PersonTracker

logger = logging.getLogger(__name__)


class VisionService:
    """
    Captures frames from a camera (local or RC stream) in a background thread.
    Runs object / face / gesture detection at ~5 fps.
    When follow mode is active, also publishes TRACKING_UPDATE for the Navigator.
    """

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self._cap: cv2.VideoCapture | None = None
        self._frame_lock = threading.Lock()
        self._current_frame: np.ndarray | None = None
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._follow_mode = False

        self.object_detector = ObjectDetector()
        self.face_detector = FaceDetector()
        self.gesture_detector = GestureDetector()
        self.person_tracker = PersonTracker()

        os.makedirs("captured_images", exist_ok=True)

        self.bus.subscribe(EventType.FRAME_CAPTURED, self._on_capture_request)
        self.bus.subscribe(EventType.FOLLOW_MODE, self._on_follow_mode)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

        # Use RC stream URL if configured, otherwise local webcam index
        video_source = settings.rc_video_url if settings.rc_video_url else settings.camera_index
        self._cap = cv2.VideoCapture(video_source)

        if not self._cap.isOpened():
            logger.error("Video source '%s' could not be opened.", video_source)
            return

        self._running = True
        threading.Thread(target=self._capture_loop, daemon=True, name="vision-capture").start()
        threading.Thread(target=self._process_loop, daemon=True, name="vision-process").start()
        logger.info("VisionService started (source=%s).", video_source)

    def stop(self) -> None:
        self._running = False
        if self._cap:
            self._cap.release()
        logger.info("VisionService stopped.")

    def get_frame(self) -> np.ndarray | None:
        """Return a copy of the latest frame (thread-safe)."""
        with self._frame_lock:
            if self._current_frame is None:
                return None
            return self._current_frame.copy()

    # ── Threads ───────────────────────────────────────────────────────────────

    def _capture_loop(self) -> None:
        """Continuously read frames from camera / stream."""
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                with self._frame_lock:
                    self._current_frame = frame
            else:
                # For network streams, brief pause before retry
                time.sleep(0.05)

    def _process_loop(self) -> None:
        """Process frames at ~5 fps and publish detection events."""
        while self._running:
            frame = self.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            try:
                objects = self.object_detector.detect(frame)
                faces = self.face_detector.detect(frame)
                gestures = self.gesture_detector.detect(frame)

                if objects:
                    self._publish(EventType.OBJECTS_DETECTED, {"objects": objects})
                if faces:
                    self._publish(EventType.FACE_DETECTED, {"faces": faces})
                if gestures:
                    for hand in gestures:
                        self._publish(EventType.GESTURE_DETECTED, {"gesture": hand["gesture"]})

                # Person tracking — only publish when follow mode is active
                if self._follow_mode:
                    h, w = frame.shape[:2]
                    tracking = self.person_tracker.update(objects, w, h)
                    self._publish(EventType.TRACKING_UPDATE, tracking)

            except Exception as exc:
                logger.error("Vision processing error: %s", exc, exc_info=True)

            time.sleep(0.2)  # ~5 fps

    def _publish(self, event_type: EventType, payload: dict) -> None:
        """Thread-safe publish to the async event bus."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.bus.publish(Event(event_type, payload, source="vision_service")),
                self._loop,
            )

    # ── Event handlers ────────────────────────────────────────────────────────

    async def _on_follow_mode(self, event: Event) -> None:
        """Toggle follow/tracking mode."""
        self._follow_mode = event.payload.get("enabled", False)
        logger.info("Follow mode: %s", "ON" if self._follow_mode else "OFF")

    async def _on_capture_request(self, event: Event) -> None:
        """Save current frame to disk."""
        frame = self.get_frame()
        if frame is None:
            logger.warning("Capture requested but no frame available.")
            return

        path = f"captured_images/photo_{int(time.time())}.jpg"
        cv2.imwrite(path, frame)
        logger.info("Photo captured: %s", path)

        await self.bus.publish(Event(
            EventType.FRAME_CAPTURED,
            {"path": path},
            source="vision_service",
        ))
