# ============================================================
# DRIVESAFE AI - REAL DRIVING DEMO
# AI + VEHICLE STATE + SPEED + SAFETY INTEGRATION
# ============================================================

import cv2
import time

from ai_driving_integration import AIDrivingIntegration


# ============================================================
# SETTINGS
# ============================================================

CAMERA_ID = 0

# IMPORTANT:
# This is only a TEST speed.
# It is NOT real vehicle speed.
TEST_SPEED = None

DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540


# ============================================================
# START SYSTEM
# ============================================================

print("==============================================")
print("      DriveSafe AI - REAL DRIVING DEMO")
print("==============================================")

print("Starting AI driving integration...")

system = AIDrivingIntegration()

print("AI integration loaded.")

# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Camera started.")

print("----------------------------------------------")
print("Speed source: NOT CONNECTED")
print("Vehicle state: NOT DRIVING")
print("AI driving monitoring: WAITING")
print("----------------------------------------------")
print("Press Q to quit.")
print("==============================================")


# ============================================================
# VARIABLES
# ============================================================

last_print_time = 0


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
    # CURRENT SPEED
    # ========================================================
    #
    # None means NO REAL SPEED DATA.
    #
    # DO NOT put 50 or 80 here for the final demo.
    #

    speed = TEST_SPEED


    # ========================================================
    # PROCESS DRIVING SYSTEM
    # ========================================================

    result = system.process(speed)


    vehicle_state = result["vehicle_state"]
    ai_monitoring = result["ai_monitoring"]

    mode = result["mode"]

    speed_status = result.get(
        "speed_status",
        "NO SPEED DATA"
    )

    speed_rule = result.get(
        "speed_rule",
        "NO SPEED DATA"
    )

    alert_level = result["alert_level"]
    alert_status = result["alert_status"]

    detections = result["detections"]


    # ========================================================
    # DISPLAY HEADER
    # ========================================================

    cv2.putText(
        frame,
        "DRIVESAFE AI",
        (25, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2
    )


    # ========================================================
    # VEHICLE STATE
    # ========================================================

    cv2.putText(
        frame,
        f"Vehicle: {vehicle_state}",
        (25, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SPEED
    # ========================================================

    if speed is None:

        speed_text = "Speed: NOT AVAILABLE"

    else:

        speed_text = f"Speed: {speed:.1f} km/h"


    cv2.putText(
        frame,
        speed_text,
        (25, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SPEED STATUS
    # ========================================================

    cv2.putText(
        frame,
        f"Speed Status: {speed_status}",
        (25, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # MODE
    # ========================================================

    cv2.putText(
        frame,
        f"Mode: {mode}",
        (25, 185),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # AI MONITORING
    # ========================================================

    if ai_monitoring:

        ai_text = "AI MONITORING: ACTIVE"

    else:

        ai_text = "AI MONITORING: WAITING"


    cv2.putText(
        frame,
        ai_text,
        (25, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SPEED RULE
    # ========================================================

    cv2.putText(
        frame,
        f"Speed Rule: {speed_rule}",
        (25, 255),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # ALERT LEVEL
    # ========================================================

    cv2.putText(
        frame,
        f"Safety Level: {alert_level}",
        (25, 290),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # ALERT STATUS
    # ========================================================

    cv2.putText(
        frame,
        f"Status: {alert_status}",
        (25, 325),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DETECTIONS
    # ========================================================

    if detections:

        detection_text = ", ".join(detections)

    else:

        detection_text = "NONE"


    cv2.putText(
        frame,
        f"Detections: {detection_text}",
        (25, 360),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # WAITING MESSAGE
    # ========================================================

    if vehicle_state == "NOT DRIVING":

        cv2.putText(
            frame,
            "WAITING FOR REAL VEHICLE SPEED...",
            (25, 410),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


    # ========================================================
    # PRINT STATUS PERIODICALLY
    # ========================================================

    current_time = time.time()

    if current_time - last_print_time >= 3:

        print("----------------------------------------------")

        print("Vehicle State:", vehicle_state)
        print("Speed:", speed)
        print("Speed Status:", speed_status)
        print("Mode:", mode)
        print("AI Monitoring:", ai_monitoring)
        print("Detections:", detections)
        print("Safety Level:", alert_level)
        print("Alert Status:", alert_status)

        last_print_time = current_time


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    frame = cv2.resize(
        frame,
        (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    )

    cv2.imshow(
        "DriveSafe AI - Real Driving Demo",
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

print("==============================================")
print("DriveSafe AI real driving demo stopped.")
print("Camera closed successfully.")
print("==============================================")