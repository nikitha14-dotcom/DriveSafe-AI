import cv2
import time
import mediapipe as mp
import numpy as np
from phone_module import PhoneDetector


MODEL_PATH = "models/face_landmarker.task"

EAR_THRESHOLD = 0.21
DROWSY_TIME = 2.0

MAR_THRESHOLD = 0.45
YAWN_TIME = 1.2

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

UPPER_LIP = 13
LOWER_LIP = 14
LEFT_MOUTH = 61
RIGHT_MOUTH = 291


def distance(p1, p2):
    return np.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


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
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def calculate_mar(landmarks):
    upper = landmarks[UPPER_LIP]
    lower = landmarks[LOWER_LIP]
    left = landmarks[LEFT_MOUTH]
    right = landmarks[RIGHT_MOUTH]

    horizontal = distance(left, right)

    if horizontal == 0:
        return 0.0

    return distance(upper, lower) / horizontal


print("==============================================")
print("DriveSafe AI - REAL CAMERA INTEGRATION")
print("==============================================")
print("Loading phone detector...")

phone_detector = PhoneDetector()

print("Phone detector loaded.")
print("Loading face detector...")

base_options = mp.tasks.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_faces=1
)

landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(
    options
)

print("Face detector loaded.")
print("==============================================")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    landmarker.close()
    exit()

print("Camera started.")
print("Phone: ACTIVE")
print("Drowsiness: ACTIVE")
print("Yawning: ACTIVE")
print("Vehicle state: DEMO DRIVING")
print("Press Q to quit.")
print("==============================================")

eyes_closed_start = None
mouth_open_start = None

drowsiness = False
yawning = False

timestamp_ms = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    frame = cv2.flip(frame, 1)

    phone_result = phone_detector.detect(frame)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp_ms += 33

    face_result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    ear = 0.0
    mar = 0.0
    face_detected = False

    if face_result.face_landmarks:
        face_detected = True
        landmarks = face_result.face_landmarks[0]

        left_ear = calculate_ear(
            landmarks,
            LEFT_EYE
        )

        right_ear = calculate_ear(
            landmarks,
            RIGHT_EYE
        )

        ear = (left_ear + right_ear) / 2.0
        mar = calculate_mar(landmarks)

        if ear < EAR_THRESHOLD:

            if eyes_closed_start is None:
                eyes_closed_start = time.time()

            if time.time() - eyes_closed_start >= DROWSY_TIME:
                drowsiness = True

        else:
            eyes_closed_start = None
            drowsiness = False

        if mar >= MAR_THRESHOLD:

            if mouth_open_start is None:
                mouth_open_start = time.time()

            if time.time() - mouth_open_start >= YAWN_TIME:
                yawning = True

        else:
            mouth_open_start = None
            yawning = False

    else:
        eyes_closed_start = None
        mouth_open_start = None
        drowsiness = False
        yawning = False

    if phone_result["detected"]:
        phone = True
    else:
        phone = False

    if phone:
        status = "PHONE DETECTED"
    elif drowsiness:
        status = "DROWSINESS DETECTED"
    elif yawning:
        status = "YAWNING DETECTED"
    elif not face_detected:
        status = "NO FACE"
    else:
        status = "DRIVER SAFE"

    for x1, y1, x2, y2, confidence in phone_result["boxes"]:
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"PHONE {confidence:.2f}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.putText(
        frame,
        "DriveSafe AI - LIVE",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Vehicle: DRIVING",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Phone: {'YES' if phone else 'NO'}",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"EAR: {ear:.3f}",
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"MAR: {mar:.3f}",
        (20, 175),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        status,
        (20, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 255) if phone or drowsiness or yawning else (0, 255, 0),
        2
    )

    cv2.imshow(
        "DriveSafe AI - Real Camera Integration",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
landmarker.close()

print("==============================================")
print("DriveSafe AI integration stopped.")
print("Camera closed successfully.")
print("==============================================")