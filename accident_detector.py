import cv2
import time
import pygame

# ============================================================
# DriveSafe AI - Camera Motion Demonstration
#
# This legacy standalone demo measures image motion only. A sudden camera
# movement is not evidence that a vehicle crash occurred.
# ============================================================

ALARM_PATH = "sounds/alert.wav"

# Motion threshold
MOTION_THRESHOLD = 35

# Number of consecutive high-motion frames
REQUIRED_FRAMES = 3

# Cooldown between alerts
ALERT_COOLDOWN = 5


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
            pygame.mixer.music.play()


def stop_alarm():
    if alarm_available:
        pygame.mixer.music.stop()


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("==============================================")
print("DriveSafe AI - Camera Motion Demo")
print("==============================================")
print("Camera started.")
print("High sudden camera motion will be monitored; this does not detect crashes.")
print("Press Q to quit.")
print("==============================================")


# ============================================================
# VARIABLES
# ============================================================

previous_gray = None
high_motion_frames = 0
last_alert_time = 0

high_motion_detected = False


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    motion_value = 0

    # ========================================================
    # MOTION DETECTION
    # ========================================================

    if previous_gray is not None:

        difference = cv2.absdiff(previous_gray, gray)

        _, threshold = cv2.threshold(
            difference,
            MOTION_THRESHOLD,
            255,
            cv2.THRESH_BINARY
        )

        threshold = cv2.dilate(
            threshold,
            None,
            iterations=2
        )

        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        largest_area = 0

        for contour in contours:

            area = cv2.contourArea(contour)

            if area > largest_area:
                largest_area = area

        motion_value = largest_area

        # ====================================================
        # HIGH MOTION
        # ====================================================

        if motion_value > 15000:

            high_motion_frames += 1

        else:

            high_motion_frames = 0

            if high_motion_detected:
                high_motion_detected = False
                stop_alarm()


        # ====================================================
        # CAMERA MOTION WARNING ONLY (not accident detection)
        # ====================================================

        current_time = time.time()

        if (
            high_motion_frames >= REQUIRED_FRAMES
            and current_time - last_alert_time >= ALERT_COOLDOWN
        ):

            high_motion_detected = True

            last_alert_time = current_time

            play_alarm()

    else:

        high_motion_frames = 0


    # ========================================================
    # SAVE CURRENT FRAME
    # ========================================================

    previous_gray = gray.copy()


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.putText(
        frame,
        f"Motion: {motion_value:.0f}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    if high_motion_detected:

        cv2.putText(
            frame,
            "HIGH CAMERA MOTION",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        cv2.putText(
            frame,
            "MOTION WARNING ONLY - NOT CRASH DETECTION",
            (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "NORMAL",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )


    cv2.imshow(
        "DriveSafe AI - Camera Motion Demo",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

stop_alarm()

cap.release()

cv2.destroyAllWindows()

pygame.quit()

print("==============================================")
print("DriveSafe AI - Camera Motion Demo stopped.")
print("Camera closed successfully.")
print("==============================================")
