import cv2
import time
import pygame
from ultralytics import YOLO

# ============================================================
# DRIVESAFE AI - PHONE ONLY DETECTION
# ============================================================

MODEL_PATH = "yolo11n.pt"
ALARM_PATH = "sounds/alert.wav"

# Phone is accepted only above this confidence
CONFIDENCE_THRESHOLD = 0.70

# Number of consecutive frames required
REQUIRED_FRAMES = 2

# Alarm repeat delay
ALARM_COOLDOWN = 0.5

# COCO class ID:
# 67 = cell phone
PHONE_CLASS_ID = 67

# Smaller image = faster inference
IMAGE_SIZE = 320


# ============================================================
# LOAD YOLO
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded.")


# ============================================================
# LOAD ALARM
# ============================================================

pygame.mixer.init()

try:
    pygame.mixer.music.load(ALARM_PATH)
    alarm_available = True
    print("Alarm loaded successfully.")

except Exception as e:
    print("WARNING: Alarm could not be loaded.")
    print(e)
    alarm_available = False


# ============================================================
# ALARM FUNCTION
# ============================================================

last_alarm_time = 0


def play_alarm():

    global last_alarm_time

    current_time = time.time()

    if current_time - last_alarm_time >= ALARM_COOLDOWN:

        if alarm_available:
            pygame.mixer.music.play()

        last_alarm_time = current_time


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()


# Try to keep camera processing responsive
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


print("==============================================")
print("DriveSafe AI - PHONE ONLY DETECTOR")
print("==============================================")
print("Camera started.")
print("Phone confidence:", CONFIDENCE_THRESHOLD)
print("Required frames:", REQUIRED_FRAMES)
print("Press Q to quit.")
print("==============================================")


# ============================================================
# VARIABLES
# ============================================================

phone_frames = 0
phone_detected = False

previous_time = time.perf_counter()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("ERROR: Could not read camera.")
        break


    # Mirror camera
    frame = cv2.flip(frame, 1)


    # ========================================================
    # YOLO PHONE DETECTION ONLY
    # ========================================================

    start_time = time.perf_counter()

    results = model.predict(
        source=frame,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE_THRESHOLD,
        classes=[PHONE_CLASS_ID],
        verbose=False
    )

    inference_time = (
        time.perf_counter() - start_time
    ) * 1000


    # ========================================================
    # CHECK PHONE
    # ========================================================

    current_phone = False
    best_confidence = 0.0


    if results[0].boxes is not None:

        for box in results[0].boxes:

            confidence = float(box.conf[0])

            if confidence >= CONFIDENCE_THRESHOLD:

                current_phone = True

                if confidence > best_confidence:
                    best_confidence = confidence


                # Bounding box
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
                    f"PHONE {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )


    # ========================================================
    # MULTI-FRAME CONFIRMATION
    # ========================================================

    if current_phone:

        phone_frames += 1

    else:

        phone_frames = 0
        phone_detected = False


    # Confirm phone only after several consecutive frames

    if phone_frames >= REQUIRED_FRAMES:

        phone_detected = True


    # ========================================================
    # DISPLAY STATUS
    # ========================================================

    if phone_detected:

        cv2.putText(
            frame,
            "PHONE DETECTED",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )


        cv2.putText(
            frame,
            "DRIVER DISTRACTION WARNING",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


        cv2.putText(
            frame,
            f"Confidence: {best_confidence:.2f}",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )


        play_alarm()


    else:

        cv2.putText(
            frame,
            "NO PHONE",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )


    # ========================================================
    # PERFORMANCE DISPLAY
    # ========================================================

    cv2.putText(
        frame,
        f"Inference: {inference_time:.1f} ms",
        (20, 155),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Confirm: {phone_frames}/{REQUIRED_FRAMES}",
        (20, 185),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # CAMERA WINDOW
    # ========================================================

    cv2.imshow(
        "DriveSafe AI - Phone Detection",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

if alarm_available:

    pygame.mixer.music.stop()

pygame.quit()

print("==============================================")
print("DriveSafe AI phone detection stopped.")
print("Camera closed successfully.")
print("==============================================")