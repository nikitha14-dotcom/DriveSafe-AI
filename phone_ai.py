import cv2
from ultralytics import YOLO

MODEL_PATH = "yolo11n.pt"
CONFIDENCE_THRESHOLD = 0.70
PHONE_CLASS_ID = 67
IMAGE_SIZE = 320

print("Loading phone AI model...")

model = YOLO(MODEL_PATH)

print("Phone AI model loaded.")


def detect_phone(frame):

    results = model.predict(
        source=frame,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE_THRESHOLD,
        classes=[PHONE_CLASS_ID],
        verbose=False
    )

    detected = False
    confidence = 0.0

    if results[0].boxes is not None:

        for box in results[0].boxes:

            conf = float(box.conf[0])

            if conf >= CONFIDENCE_THRESHOLD:

                detected = True

                if conf > confidence:
                    confidence = conf

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )

                cv2.putText(
                    frame,
                    f"PHONE {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

    return detected, confidence