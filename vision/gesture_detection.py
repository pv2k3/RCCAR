"""
Gesture detection using MediaPipe Tasks HandLandmarker.
Classifies basic hand gestures from landmark positions.

Uses the new mediapipe.tasks API (compatible with mediapipe >= 0.10.x).
Auto-downloads the hand_landmarker.task model on first use.
"""

import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")


def _ensure_model() -> None:
    """Download the HandLandmarker model file if not present."""
    if os.path.exists(_MODEL_PATH):
        return
    import urllib.request
    logger.info("Downloading hand_landmarker.task model (~8 MB)…")
    try:
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        logger.info("Model saved to %s", _MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(f"Failed to download hand landmarker model: {exc}") from exc


class GestureDetector:
    """
    Detects hand landmarks and classifies simple gestures.
    Lazy-loads MediaPipe Tasks HandLandmarker on first use.
    """

    def __init__(self, max_hands: int = 2, min_detection_confidence: float = 0.5) -> None:
        self._max_hands = max_hands
        self._min_confidence = min_detection_confidence
        self._landmarker = None

    def _load(self) -> None:
        if self._landmarker is not None:
            return
        _ensure_model()
        import mediapipe as mp
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_hands=self._max_hands,
            min_hand_detection_confidence=self._min_confidence,
            min_hand_presence_confidence=self._min_confidence,
            min_tracking_confidence=self._min_confidence,
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        logger.info("MediaPipe Tasks HandLandmarker loaded.")

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Detect hands and classify gestures in a BGR frame.

        Returns:
            List of hand dicts: [{gesture: str, landmarks: list}]
        """
        self._load()
        import cv2
        import mediapipe as mp

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect(mp_image)

        hands = []
        if not result.hand_landmarks:
            return hands

        for hand_landmarks in result.hand_landmarks:
            landmarks = [
                {"x": lm.x, "y": lm.y, "z": lm.z}
                for lm in hand_landmarks
            ]
            gesture = self._classify(landmarks)
            hands.append({"gesture": gesture, "landmarks": landmarks})

        return hands

    def _classify(self, landmarks: list[dict]) -> str:
        """
        Classify gesture from 21 hand landmark positions.
        Uses fingertip-vs-knuckle y-position heuristic.
        """
        # Fingertip indices: 4,8,12,16,20 — PIP (knuckle) indices: 3,6,10,14,18
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]

        fingers_up = [landmarks[tip]["y"] < landmarks[pip]["y"]
                      for tip, pip in zip(tips, pips)]
        count = sum(fingers_up)

        if count == 5:
            return "open_palm"
        if count == 0:
            return "fist"
        if fingers_up[0] and count == 1:
            return "thumbs_up"
        if fingers_up[1] and count == 1:
            return "pointing"
        if fingers_up[1] and fingers_up[2] and count == 2:
            return "peace"
        return f"fingers_{count}"

    def annotate(self, frame: np.ndarray, hands: list[dict]) -> np.ndarray:
        """Draw hand landmarks and gesture label on a frame copy."""
        import cv2
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        for hand in hands:
            landmarks = hand["landmarks"]
            for lm in landmarks:
                cx, cy = int(lm["x"] * w), int(lm["y"] * h)
                cv2.circle(annotated, (cx, cy), 4, (0, 200, 255), -1)

            wrist = landmarks[0]
            cv2.putText(
                annotated,
                hand["gesture"],
                (int(wrist["x"] * w), int(wrist["y"] * h) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2,
            )

        return annotated
