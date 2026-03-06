"""
Person tracker — finds the largest detected person in YOLO detections
and computes their position relative to the frame centre.

Used by VisionService to feed the Navigator's follow/tracking loop.
"""

import logging

logger = logging.getLogger(__name__)


class PersonTracker:
    """
    Stateless helper: call update() on every processed frame.

    Returns a tracking dict:
        {
            "detected":   bool,
            "offset_x":   float,   # -1.0 (far left) .. 0.0 (centre) .. +1.0 (far right)
            "area_ratio": float,   # bbox_area / frame_area — proxy for distance
                                   #   small → person is far away
                                   #   large → person is close
            "bbox":       dict | None,  # {"x", "y", "w", "h"} in pixels
        }
    """

    def update(
        self,
        detections: list[dict],
        frame_width: int,
        frame_height: int,
    ) -> dict:
        """
        Args:
            detections:   list of YOLO dicts [{label, confidence, bbox:{x,y,w,h}}]
            frame_width:  frame pixel width
            frame_height: frame pixel height
        """
        persons = [d for d in detections if d.get("label", "").lower() == "person"]

        if not persons:
            return {"detected": False, "offset_x": 0.0, "area_ratio": 0.0, "bbox": None}

        # Track the largest (nearest) person
        target = max(persons, key=lambda d: d["bbox"].get("w", 0) * d["bbox"].get("h", 0))
        b = target["bbox"]

        frame_area = frame_width * frame_height or 1
        bbox_area = b.get("w", 0) * b.get("h", 0)
        area_ratio = bbox_area / frame_area

        # Horizontal centre of the bbox, normalised to [-1, +1]
        cx = b.get("x", 0) + b.get("w", 0) / 2
        offset_x = (cx / frame_width - 0.5) * 2.0

        logger.debug(
            "PersonTracker: offset_x=%.2f  area_ratio=%.3f",
            offset_x, area_ratio,
        )

        return {
            "detected": True,
            "offset_x": round(offset_x, 3),
            "area_ratio": round(area_ratio, 4),
            "bbox": b,
        }
