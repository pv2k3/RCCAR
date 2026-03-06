"""
Object detection using YOLOv8.
Runs inference on a single frame and returns structured detections.
"""

import logging
import numpy as np
from config.settings import settings

logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    Wraps YOLOv8 for single-frame object detection.
    Lazy-loads the model on first use to keep startup fast.
    """

    def __init__(self) -> None:
        self._model = None
        self._model_path = settings.yolo_model_path
        self._confidence = settings.vision_confidence_threshold

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO
            logger.info("Loading YOLO model: %s", self._model_path)
            self._model = YOLO(self._model_path)
            logger.info("YOLO model loaded.")

    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Run object detection on a BGR frame.

        Args:
            frame: BGR numpy array from OpenCV.

        Returns:
            List of detections: [{label, confidence, bbox: [x1,y1,x2,y2]}]
        """
        self._load_model()

        results = self._model(frame, verbose=False, conf=self._confidence)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            detections.append({
                "label": self._model.names[cls_id],
                "confidence": round(float(box.conf[0]), 3),
                "bbox": list(map(int, box.xyxy[0].tolist())),
            })

        return detections

    def annotate(self, frame: np.ndarray, detections: list[dict]) -> np.ndarray:
        """Draw bounding boxes and labels on a frame copy."""
        import cv2
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = f"{det['label']} {det['confidence']:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated, label, (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2
            )
        return annotated
