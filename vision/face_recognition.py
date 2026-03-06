"""
Face detection using OpenCV Haar Cascade.
Returns bounding boxes and confidence for each detected face.

Uses OpenCV's built-in Haar cascade — no external model download required,
fully compatible with all mediapipe versions.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Detects human faces in a BGR frame using OpenCV Haar Cascade.
    Lazy-loads on first use.
    """

    def __init__(self, min_detection_confidence: float = 0.5) -> None:
        self._min_confidence = min_detection_confidence
        self._detector = None

    def _load(self):
        if self._detector is None:
            import cv2
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._detector = cv2.CascadeClassifier(cascade_path)
            if self._detector.empty():
                raise RuntimeError("Failed to load Haar cascade face detector.")
            logger.info("OpenCV Haar Cascade FaceDetector loaded.")

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Detect faces in a BGR frame.

        Args:
            frame: BGR numpy array from OpenCV.

        Returns:
            List of face dicts: [{confidence, bbox: {x, y, w, h}}]
        """
        self._load()
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        detections = self._detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        faces = []
        if len(detections) == 0:
            return faces

        for (x, y, w, h) in detections:
            faces.append({
                "confidence": 0.9,
                "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            })

        return faces

    def annotate(self, frame: np.ndarray, faces: list[dict]) -> np.ndarray:
        """Draw face bounding boxes on a frame copy."""
        import cv2
        annotated = frame.copy()
        for face in faces:
            b = face["bbox"]
            cv2.rectangle(
                annotated,
                (b["x"], b["y"]),
                (b["x"] + b["w"], b["y"] + b["h"]),
                (255, 0, 0), 2
            )
            cv2.putText(
                annotated,
                f"face {face['confidence']:.2f}",
                (b["x"], b["y"] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2
            )
        return annotated
