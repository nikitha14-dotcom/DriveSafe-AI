import cv2
import mediapipe as mp
import numpy as np
import pygame
import time

from ultralytics import YOLO
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ============================================================
# DriveSafe AI - Integrated Safety Demo
# Drowsiness + Phone Detection + Alarm
# ============================================================

FACE_MODEL = "models/face_landmarker.task"
YOLO_MODEL = "yolo11n.pt"
ALARM_FILE = "sounds/alert.wav"

# ---------------- SETTINGS ----------------

EAR_THRESHOLD = 0.21
DROWSY_TIME = 2.0

PHONE_CONFIDENCE = 0.70
PHONE_REQUIRED_FRAMES = 2

# ============================================================
# ALARM SETUP
# ============================================================

pygame.mixer.init()

try:
    pygame.mixer.music.load(ALARM_FILE)
    alarm_available = True
    print("Alarm loaded successfully.")
except Exception as e:
    print("WARNING: Alarm could not be loaded.")
    print(e)
    alarm_available = False


def play_alarm():
    if alarm_available:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()


def stop_alarm():
    if alarm_available:
        pygame.mixer.music.stop()


# ============================================================
# YOLO MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(YOLO_MODEL)

print("YOLO model loaded.")


# ============================================================
# MEDIAPIPE FACE LANDMARKER
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=FACE_MODEL
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1
)

landmarker = vision.FaceLandmarker.create_from_options(
    options
)


# ============================================================
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [
    362, 385, 387, 263, 373, 380
]

RIGHT_EYE = [
    33, 160, 158, 133, 153, 144
]


# ============================================================
# DISTANCE
# ============================================================

def distance(p1, p2):
    return np.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


# ============================================================
# EAR
# ============================================================

def calculate_ear(landmarks, eye):

    p1 = landmarks[eye[0]]
    p2 = landmarks[eye[1]]
    p3 = landmarks[eye[2]]
    p4 = landmarks[eye[3]]
    p5 = landmarks[eye[4]]
    p6 = landmarks[eye[5]]

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0

    return (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    raise SystemExit


# ============================================================
# VARIABLES
# ============================================================

frame_timestamp = 0

eyes_closed_start = None
drowsy = False

phone_frames = 0
phone_detected = False

print()
print("==============================================")
print("      DriveSafe AI - INTEGRATED DEMO")
print("==============================================")
print("Camera started.")
print("Drowsiness detection: ACTIVE")
print("Phone detection: ACTIVE")
print("Alarm system: ACTIVE")
print("Phone confidence:", PHONE_CONFIDENCE)
print("Phone required frames:", PHONE_REQUIRED_FRAMES)
print("Press Q to quit.")
print("==============================================")


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("ERROR: Could not read camera.")
            break

        frame = cv2.flip(frame, 1)

        # ----------------------------------------------------
        # MEDIAPIPE DROWSINESS DETECTION
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = landmarker.detect_for_video(
            mp_image,
            frame_timestamp
        )

        frame_timestamp += 1

        drowsiness_status = "NO FACE"

        if result.face_landmarks:

            landmarks = result.face_landmarks[0]

            left_ear = calculate_ear(
                landmarks,
                LEFT_EYE
            )

            right_ear = calculate_ear(
                landmarks,
                RIGHT_EYE
            )

            ear = (
                left_ear + right_ear
            ) / 2.0

            cv2.putText(
                frame,
                f"EAR: {ear:.3f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # -----------------------------------------------
            # EYES CLOSED
            # -----------------------------------------------

            if ear < EAR_THRESHOLD:

                if eyes_closed_start is None:
                    eyes_closed_start = time.time()

                closed_duration = (
                    time.time()
                    - eyes_closed_start
                )

                cv2.putText(
                    frame,
                    f"Eyes Closed: {closed_duration:.1f}s",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

                if closed_duration >= DROWSY_TIME:

                    drowsy = True
                    drowsiness_status = "DROWSINESS"

            else:

                eyes_closed_start = None
                drowsy = False

                drowsiness_status = "AWAKE"


        # ----------------------------------------------------
        # YOLO PHONE DETECTION
        # ----------------------------------------------------

        results = model(
            frame,
            verbose=False
        )

        current_phone = False

        for detection in results[0].boxes:

            confidence = float(
                detection.conf[0]
            )

            class_id = int(
                detection.cls[0]
            )

            class_name = model.names[class_id]

            # COCO class for cell phone = 67
            if (
                class_name == "cell phone"
                and confidence >= PHONE_CONFIDENCE
            ):

                current_phone = True

                x1, y1, x2, y2 = map(
                    int,
                    detection.xyxy[0]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"PHONE {confidence:.2f}",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

        # ----------------------------------------------------
        # PHONE CONFIRMATION
        # ----------------------------------------------------

        if current_phone:

            phone_frames += 1

        else:

            phone_frames = 0
            phone_detected = False

        if phone_frames >= PHONE_REQUIRED_FRAMES:

            phone_detected = True


        # ----------------------------------------------------
        # ALERT DECISION
        # ----------------------------------------------------

        if drowsy or phone_detected:

            play_alarm()

        else:

            stop_alarm()


        # ----------------------------------------------------
        # DISPLAY STATUS
        # ----------------------------------------------------

        if drowsy:

            cv2.putText(
                frame,
                "DROWSINESS ALERT!",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3
            )

        elif drowsiness_status == "AWAKE":

            cv2.putText(
                frame,
                "DRIVER AWAKE",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        if phone_detected:

            cv2.putText(
                frame,
                "PHONE DETECTED!",
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3
            )

        else:

            cv2.putText(
                frame,
                "PHONE: CLEAR",
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


        # ----------------------------------------------------
        # SYSTEM STATUS
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "DriveSafe AI - ACTIVE",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.imshow(
            "DriveSafe AI - Integrated Safety System",
            frame
        )


        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    print()
    print("==============================================")
    print("DriveSafe AI integrated system stopped.")
    print("Camera closed successfully.")
    print("==============================================")

    stop_alarm()

    cap.release()

    cv2.destroyAllWindows()

    landmarker.close()

    pygame.quit()