import cv2
import time
from ultralytics import YOLO
from utils.alarm import play_alarm

# -------------------------
# Load YOLO Model
# -------------------------
model = YOLO("models/yolo11n.pt")

# -------------------------
# Start Webcam
# -------------------------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

phone_start = None
warning_given = False

risk_level = "SAFE"
status = "Monitoring"

while True:

    start = time.time()

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, conf=0.30)

    phone_detected = False
    person_detected = False

    for r in results:

        for box in r.boxes:

            cls = int(box.cls[0])
            name = model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            color = (0, 255, 0)

            if name == "person":
                person_detected = True

            if name == "cell phone":
                phone_detected = True
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                name,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

    # -------------------------
    # Phone Timer
    # -------------------------

    if phone_detected:

        if phone_start is None:
            phone_start = time.time()

        duration = time.time() - phone_start

        if duration < 3:

            risk_level = "LEVEL 1"
            status = "Phone Detected"

        elif duration < 6:

            risk_level = "LEVEL 2"
            status = "Continuous Phone Usage"

            if not warning_given:
                print("Alarm Triggered")
                play_alarm()
                warning_given = True

        else:

            risk_level = "LEVEL 3"
            status = "Danger"

            if not warning_given:
                print("Alarm Triggered")
                play_alarm()
                warning_given = True

    else:

        phone_start = None
        duration = 0
        risk_level = "SAFE"
        status = "Monitoring"
        warning_given = False

    # -------------------------
    # FPS
    # -------------------------

    fps = int(1 / (time.time() - start))

    # -------------------------
    # Side Panel
    # -------------------------

    panel_width = 350

    display = cv2.copyMakeBorder(
        frame,
        0,
        0,
        0,
        panel_width,
        cv2.BORDER_CONSTANT,
        value=(40, 40, 40),
    )

    x = frame.shape[1] + 20

    cv2.putText(
        display,
        "DriveSafe AI",
        (x, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2,
    )

    cv2.putText(
        display,
        f"Person : {person_detected}",
        (x, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        display,
        f"Phone : {phone_detected}",
        (x, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        display,
        f"Phone Time : {duration:.1f}s",
        (x, 170),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        display,
        f"FPS : {fps}",
        (x, 210),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )

    color = (0, 255, 0)

    if risk_level == "LEVEL 2":
        color = (0, 255, 255)

    elif risk_level == "LEVEL 3":
        color = (0, 0, 255)

    cv2.putText(
        display,
        f"Risk : {risk_level}",
        (x, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
    )

    cv2.putText(
        display,
        f"Status : {status}",
        (x, 290),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 0),
        2,
    )

    cv2.imshow("DriveSafe AI", display)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()