import cv2
import time
import pygame
import numpy as np
from ultralytics import YOLO

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from eye_closure import eyes_closed, update_drowsiness


# ============================================================
# DRIVESAFE AI - FINAL INTEGRATED DEMO
# Phone + Drowsiness + Yawning
# ============================================================

FACE_MODEL_PATH = "models/face_landmarker.task"
YOLO_MODEL_PATH = "yolo11n.pt"
ALARM_PATH = "sounds/alert.wav"


# ============================================================
# PHONE SETTINGS
# ============================================================

PHONE_CLASS_ID = 67
PHONE_CONFIDENCE = 0.70
PHONE_REQUIRED_FRAMES = 2
PHONE_IMAGE_SIZE = 320
PHONE_ALARM_COOLDOWN = 0.5


# ============================================================
# DROWSINESS SETTINGS
# ============================================================

EAR_THRESHOLD = 0.21
DROWSINESS_TIME = 2.0


# ============================================================
# YAWNING SETTINGS
# ============================================================

MAR_THRESHOLD = 0.55
YAWN_TIME = 1.2


# ============================================================
# FACE LANDMARK MODEL
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=FACE_MODEL_PATH
)

face_options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=True
)

landmarker = vision.FaceLandmarker.create_from_options(
    face_options
)


# ============================================================
# ALARM
# ============================================================

pygame.mixer.init()

try:

    pygame.mixer.music.load(ALARM_PATH)

    alarm_available = True

    print("Alarm loaded successfully.")

except Exception as e:

    alarm_available = False

    print("WARNING: Alarm could not be loaded.")
    print(e)


last_alarm_time = 0


def play_alarm():

    global last_alarm_time

    current_time = time.time()

    if current_time - last_alarm_time >= PHONE_ALARM_COOLDOWN:

        if alarm_available:

            pygame.mixer.music.play()

        last_alarm_time = current_time


def stop_alarm():

    if alarm_available:

        pygame.mixer.music.stop()


# ============================================================
# LOAD YOLO
# ============================================================

print("Loading YOLO model...")

model = YOLO(YOLO_MODEL_PATH)

print("YOLO model loaded.")


# ============================================================
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]

RIGHT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]


# ============================================================
# MOUTH LANDMARKS
# ============================================================

MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308


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
# MAR
# ============================================================

def calculate_mar(landmarks):

    top = landmarks[MOUTH_TOP]
    bottom = landmarks[MOUTH_BOTTOM]

    left = landmarks[MOUTH_LEFT]
    right = landmarks[MOUTH_RIGHT]

    vertical = distance(
        top,
        bottom
    )

    horizontal = distance(
        left,
        right
    )

    if horizontal == 0:

        return 0

    return vertical / horizontal


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Camera could not be opened.")

    landmarker.close()
    pygame.quit()

    raise SystemExit


cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


# ============================================================
# START
# ============================================================

print()
print("==============================================")
print("      DriveSafe AI - FINAL INTEGRATED DEMO")
print("==============================================")
print("Camera started.")
print("Drowsiness detection: ACTIVE")
print("Phone detection: ACTIVE")
print("Yawning detection: ACTIVE")
print("Alarm system: ACTIVE")
print()
print("Phone confidence:", PHONE_CONFIDENCE)
print("Phone required frames:", PHONE_REQUIRED_FRAMES)
print("Phone image size:", PHONE_IMAGE_SIZE)
print("Yawning MAR threshold:", MAR_THRESHOLD)
print("Yawning required time:", YAWN_TIME)
print()
print("Press Q to quit.")
print("==============================================")
print()


# ============================================================
# VARIABLES
# ============================================================

phone_frames = 0
phone_detected = False

eyes_closed_start = None
drowsy = False

yawn_start = None
yawning = False

timestamp = -1


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        ret, frame = cap.read()

        if not ret:

            print("ERROR: Could not read camera.")

            break


        # ----------------------------------------------------
        # MIRROR CAMERA
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        # ====================================================
        # FACE PROCESSING
        # ====================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # VIDEO mode requires elapsed milliseconds, not one millisecond per frame.
        timestamp = max(timestamp + 1, int(time.monotonic() * 1000))
        result = landmarker.detect_for_video(
            mp_image,
            timestamp
        )


        ear = 0.0
        mar = 0.0

        face_detected = False


        if result.face_landmarks:

            face_detected = True

            landmarks = result.face_landmarks[0]


            # =================================================
            # EAR
            # =================================================

            left_ear = calculate_ear(
                landmarks,
                LEFT_EYE
            )

            right_ear = calculate_ear(
                landmarks,
                RIGHT_EYE
            )

            ear = (
                left_ear +
                right_ear
            ) / 2.0


            # =================================================
            # MAR
            # =================================================

            mar = calculate_mar(
                landmarks
            )


            # =================================================
            # DROWSINESS
            # =================================================

            blendshapes = result.face_blendshapes[0] if result.face_blendshapes else []
            eyes_closed_start, currently_drowsy, closed_time = update_drowsiness(
                eyes_closed(ear, blendshapes, EAR_THRESHOLD),
                eyes_closed_start, time.monotonic(), DROWSINESS_TIME
            )
            if currently_drowsy and not drowsy:
                print("[DROWSINESS DETECTED] Driver eyes remained closed.")
                play_alarm()
            drowsy = currently_drowsy


            # =================================================
            # YAWNING
            # =================================================

            if mar >= MAR_THRESHOLD:

                if yawn_start is None:

                    yawn_start = time.time()

                yawn_duration = (
                    time.time()
                    - yawn_start
                )

                if yawn_duration >= YAWN_TIME:

                    if not yawning:

                        print(
                            "[YAWN DETECTED] "
                            "Driver mouth remained open."
                        )

                        play_alarm()

                    yawning = True

            else:

                yawn_start = None

                yawning = False


        else:

            eyes_closed_start = None
            yawn_start = None

            drowsy = False
            yawning = False


        # ====================================================
        # PHONE DETECTION
        # EXACT LOGIC FROM WORKING phone_detector.py
        # ====================================================

        start_time = time.perf_counter()

        results = model.predict(
            source=frame,
            imgsz=PHONE_IMAGE_SIZE,
            conf=PHONE_CONFIDENCE,
            classes=[PHONE_CLASS_ID],
            verbose=False
        )

        inference_time = (
            time.perf_counter()
            - start_time
        ) * 1000


        current_phone = False
        best_confidence = 0.0


        if results[0].boxes is not None:

            for box in results[0].boxes:

                confidence = float(
                    box.conf[0]
                )

                if confidence >= PHONE_CONFIDENCE:

                    current_phone = True

                    if confidence > best_confidence:

                        best_confidence = confidence


                    # ------------------------------------------------
                    # PHONE BOUNDING BOX
                    # ------------------------------------------------

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
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )


        # ====================================================
        # PHONE FRAME CONFIRMATION
        # ====================================================

        if current_phone:

            phone_frames += 1

        else:

            phone_frames = 0
            phone_detected = False


        if phone_frames >= PHONE_REQUIRED_FRAMES:

            if not phone_detected:

                print(
                    f"[PHONE DETECTED] "
                    f"Confidence: {best_confidence:.2f}"
                )

                play_alarm()

            phone_detected = True


        # ====================================================
        # DISPLAY - EAR
        # ====================================================

        cv2.putText(
            frame,
            f"EAR: {ear:.3f}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY - MAR
        # ====================================================

        cv2.putText(
            frame,
            f"MAR: {mar:.3f}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # PHONE STATUS
        # ====================================================

        if phone_detected:

            cv2.putText(
                frame,
                "PHONE DETECTED",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (0, 0, 255),
                3
            )

            cv2.putText(
                frame,
                "DRIVER DISTRACTION WARNING",
                (20, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                f"Confidence: {best_confidence:.2f}",
                (20, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "NO PHONE",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 0),
                2
            )


        # ====================================================
        # DROWSINESS STATUS
        # ====================================================

        if drowsy:

            cv2.putText(
                frame,
                "DROWSINESS DETECTED",
                (20, 205),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                3
            )

        elif face_detected:

            cv2.putText(
                frame,
                "DRIVER AWAKE",
                (20, 205),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


        # ====================================================
        # YAWNING STATUS
        # ====================================================

        if yawning:

            cv2.putText(
                frame,
                "YAWNING DETECTED",
                (20, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                3
            )


        # ====================================================
        # PERFORMANCE
        # ====================================================

        cv2.putText(
            frame,
            f"YOLO: {inference_time:.1f} ms",
            (20, 275),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Phone confirm: "
            f"{phone_frames}/{PHONE_REQUIRED_FRAMES}",
            (20, 305),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            "DriveSafe AI - FINAL INTEGRATED SYSTEM",
            frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break


finally:

    print()
    print("==============================================")
    print("DriveSafe AI integrated system stopped.")
    print("Camera closed successfully.")
    print("==============================================")


    cap.release()

    cv2.destroyAllWindows()

    stop_alarm()

    landmarker.close()

    pygame.quit()