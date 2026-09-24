import time
from ultralytics import YOLO


class PhoneDetector:
    def __init__(
        self,
        model_path="yolo11n.pt",
        confidence=0.70,
        required_frames=2,
        image_size=320
    ):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.required_frames = required_frames
        self.image_size = image_size
        self.phone_frames = 0
        self.last_confidence = 0.0

        self.PHONE_CLASS_ID = 67

    def detect(self, frame):
        start_time = time.perf_counter()

        results = self.model.predict(
            source=frame,
            imgsz=self.image_size,
            conf=self.confidence,
            classes=[self.PHONE_CLASS_ID],
            verbose=False
        )

        inference_ms = (time.perf_counter() - start_time) * 1000

        detected = False
        confidence = 0.0
        boxes = []

        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                boxes.append(
                    (x1, y1, x2, y2, confidence)
                )

        if boxes:
            self.phone_frames += 1
            self.last_confidence = max(
                box[4] for box in boxes
            )
        else:
            self.phone_frames = 0
            self.last_confidence = 0.0

        if self.phone_frames >= self.required_frames:
            detected = True

        return {
            "detected": detected,
            "confidence": self.last_confidence,
            "boxes": boxes,
            "frames": self.phone_frames,
            "inference_ms": inference_ms
        }