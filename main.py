import cv2
import mediapipe as mp
import numpy as np
import pygame
import time

from ultralytics import YOLO
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from eye_closure import eyes_closed, update_drowsiness


# ============================================================
# SETTINGS
# ============================================================

FACE_MODEL = "models/face_landmarker.task"
YOLO_MODEL = "yolo11n.pt"
ALARM_PATH = "sounds/alert.wav"

EAR_THRESHOLD = 0.21
DROWSY_TIME = 2.0


# ============================================================
# MEDIAPIPE FACE LANDMARKER
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=FACE_MODEL
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=True
)

landmarker = vision.FaceLandmarker.create_from_options(options)


# ============================================================
# YOLO PHONE DETECTOR
# ============================================================

print("Loading YOLO model...")
yolo_model = YOLO(YOLO_MODEL)

# COCO class 67 = cell phone
PHONE_CLASS = 67


# ============================================================
# ALARM
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


def play_alarm():
    if alarm_available:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)


def stop_alarm():
    if alarm_available:
        pygame.mixer.music.stop()


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
# EAR CALCULATION
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

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    landmarker.close()
    pygame.quit()
    exit()

print("==============================================")
print("        DriveSafe AI - MAIN SYSTEM")
print("==============================================")
print("Camera started.")
print("Drowsiness Detection: ON")
print("Phone Detection: ON")
print("Alarm System: ON")
print("Close eyes for 2 seconds to test.")
print("Show a phone to the camera to test.")
print("Press Q to quit.")
print("==============================================")


# ============================================================
# VARIABLES
# ============================================================

frame_timestamp = -1
eyes_closed_start = None
drowsy = False
phone_detected = False


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("ERROR: Could not read camera.")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        # ----------------------------------------------------
        # FACE DETECTION
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        frame_timestamp = max(frame_timestamp + 1, int(time.monotonic() * 1000))
        result = landmarker.detect_for_video(
            mp_image,
            frame_timestamp
        )

        # Default values
        ear = 0
        status = "NO FACE"

        # ----------------------------------------------------
        # DROWSINESS DETECTION
        # ----------------------------------------------------

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

            ear = (left_ear + right_ear) / 2.0

            cv2.putText(
                frame,
                f"EAR: {ear:.3f}",
                (30, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            # Eyes closed
            blendshapes = result.face_blendshapes[0] if result.face_blendshapes else []
            eyes_closed_start, drowsy, closed_duration = update_drowsiness(
                eyes_closed(ear, blendshapes, EAR_THRESHOLD),
                eyes_closed_start, time.monotonic(), DROWSY_TIME
            )
            if eyes_closed_start is not None:

                cv2.putText(
                    frame,
                    f"Eyes Closed: {closed_duration:.1f}s",
                    (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

                if drowsy:

                    drowsy = True
                    status = "DROWSINESS DETECTED"

            else:

                cv2.putText(
                    frame,
                    "AWAKE",
                    (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        else:

            eyes_closed_start = None
            drowsy = False

        # ----------------------------------------------------
        # YOLO PHONE DETECTION
        # ----------------------------------------------------

        phone_detected = False

        yolo_results = yolo_model(
            frame,
            verbose=False
        )

        for detection in yolo_results[0].boxes:

            class_id = int(
                detection.cls[0]
            )

            confidence = float(
                detection.conf[0]
            )

            if class_id == PHONE_CLASS and confidence > 0.40:

                phone_detected = True

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
        # FINAL SAFETY STATUS
        # ----------------------------------------------------

        if drowsy and phone_detected:

            status = "DROWSINESS + PHONE DETECTED"
            play_alarm()

        elif drowsy:

            status = "DROWSINESS DETECTED"
            play_alarm()

        elif phone_detected:

            status = "PHONE DETECTED"
            play_alarm()

        else:

            if result.face_landmarks:
                status = "SAFE"

            stop_alarm()

        # ----------------------------------------------------
        # STATUS DISPLAY
        # ----------------------------------------------------

        cv2.putText(
            frame,
            status,
            (30, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 255) if (
                drowsy or phone_detected
            ) else (0, 255, 0),
            3
        )

        # System indicators

        cv2.putText(
            frame,
            "DROWSINESS: ON",
            (30, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "PHONE DETECTION: ON",
            (30, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------------
        # SHOW CAMERA
        # ----------------------------------------------------

        cv2.imshow(
            "DriveSafe AI - Driver Monitoring System",
            frame
        )

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ============================================================
# CLEANUP
# ============================================================

finally:

    print("Closing DriveSafe AI...")

    stop_alarm()

    cap.release()

    cv2.destroyAllWindows()

    landmarker.close()

    pygame.quit()

    print("Camera closed successfully.")
    print("DriveSafe AI stopped.")

