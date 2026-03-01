import cv2
import threading
import base64
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
import os
import time


class VisionEngine:

    _instance = None
    _lock = threading.Lock()

    # ==========================
    # SINGLETON
    # ==========================

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ==========================
    # INIT
    # ==========================

    def __init__(self, camera_index=0):
        if hasattr(self, "_initialized"):
            return

        self.cap = cv2.VideoCapture(camera_index)

        self._frame_lock = threading.Lock()
        self._current_frame = None
        self._running = False

        print("🔧 Loading YOLO...")
        self.yolo_model = YOLO("yolov8n.pt")

        print("🔧 Initializing MediaPipe...")
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands()
        self.face_detector = self.mp_face.FaceDetection()

        os.makedirs("captured_images", exist_ok=True)

        self._initialized = True
        print("✅ Vision Engine Ready")

    # ==========================
    # STREAM CONTROL
    # ==========================

    def start(self):
        if self._running:
            return
        self._running = True
        threading.Thread(target=self._update, daemon=True).start()

    def stop(self):
        self._running = False
        self.cap.release()

    def _update(self):
        while self._running:
            ret, frame = self.cap.read()
            if ret:
                with self._frame_lock:
                    self._current_frame = frame

    # ==========================
    # FRAME ACCESS
    # ==========================

    def get_frame(self):
        with self._frame_lock:
            if self._current_frame is None:
                return None
            return self._current_frame.copy()

    # ==========================
    # PHOTO CAPTURE
    # ==========================

    def capture_photo(self):
        frame = self.get_frame()
        if frame is None:
            return None

        filename = f"captured_images/photo_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Photo saved: {filename}")
        return filename

    # ==========================
    # ANNOTATED FRAME
    # ==========================

    def annotate_frame(self):
        frame = self.get_frame()
        if frame is None:
            return None

        annotated = frame.copy()

        # ---------------------
        # YOLO OBJECT DETECTION
        # ---------------------
        results = self.yolo_model(annotated, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.yolo_model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # ---------------------
        # HAND DETECTION
        # ---------------------
        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb)

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    annotated,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        # ---------------------
        # FACE DETECTION
        # ---------------------
        face_results = self.face_detector.process(rgb)

        if face_results.detections:
            h, w, _ = annotated.shape
            for detection in face_results.detections:
                bbox = detection.location_data.relative_bounding_box

                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)

                cv2.rectangle(
                    annotated,
                    (x, y),
                    (x + width, y + height),
                    (255, 0, 0),
                    2
                )

        return annotated


# ==========================
# TEST RUNNER
# ==========================

if __name__ == "__main__":

    vision = VisionEngine()
    vision.start()

    print("\nPress:")
    print("  Q → Quit")
    print("  C → Capture Photo")

    while True:

        annotated = vision.annotate_frame()
        if annotated is None:
            continue

        cv2.imshow("Live Vision Engine", annotated)

        key = cv2.waitKey(1) & 0xFF

        # Quit
        if key == ord("q"):
            break

        # Capture photo
        if key == ord("c"):
            vision.capture_photo()

    vision.stop()
    cv2.destroyAllWindows()