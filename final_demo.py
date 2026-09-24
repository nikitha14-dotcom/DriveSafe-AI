# ============================================================
# DRIVESAFE AI - FINAL PRESENTATION DEMO
# Driver Monitoring + Driving System + Safety Manager
# ============================================================

import cv2
import time

from ai_driving_integration import AIDrivingIntegration


# ============================================================
# SETTINGS
# ============================================================

CAMERA_ID = 0

# DEMO SPEED
# This is SIMULATED speed for presentation/testing.
# It is NOT real vehicle speed.
DEMO_SPEED = 50.0

# Set True only when demonstrating Emergency Mode
DEMO_EMERGENCY = False

WINDOW_NAME = "DriveSafe AI - Final Demo"


# ============================================================
# START
# ============================================================

print("==============================================")
print("       DriveSafe AI - FINAL PRESENTATION")
print("==============================================")

print("Loading AI Driving Integration...")

system = AIDrivingIntegration()

print("AI system loaded successfully.")

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
print("Driver Monitoring : ACTIVE")
print("Speed Source      : SIMULATED GPS")
print("Driving System    : ACTIVE")
print("Safety Manager    : ACTIVE")
print("----------------------------------------------")
print("Press Q to quit.")
print("==============================================")


# ============================================================
# DEMO STATES
# ============================================================

phone = False
drowsiness = False
yawning = False
accident = False


# ============================================================
# HELP FUNCTION
# ============================================================

def draw_status(frame, text, position, scale=0.65):

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        2
    )


# ============================================================
# MAIN LOOP
# ============================================================

last_print = 0

while True:

    ret, frame = cap.read()

    if not ret:

        print("ERROR: Camera frame unavailable.")
        break


    # Mirror webcam
    frame = cv2.flip(frame, 1)


    # ========================================================
    # EMERGENCY MODE
    # ========================================================

    if DEMO_EMERGENCY:

        try:
            system.driving_system.emergency_mode()
        except:
            pass


    # ========================================================
    # UPDATE AI STATUS
    # ========================================================

    system.update_ai(
        phone=phone,
        drowsiness=drowsiness,
        yawning=yawning,
        accident=accident
    )


    # ========================================================
    # PROCESS
    # ========================================================

    result = system.process(DEMO_SPEED)


    vehicle_state = result["vehicle_state"]
    speed = result["speed"]
    mode = result["mode"]

    ai_monitoring = result["ai_monitoring"]

    detections = result["detections"]

    alert_level = result["alert_level"]
    alert_status = result["alert_status"]

    speed_status = result.get(
        "speed_status",
        "NO SPEED DATA"
    )

    speed_rule = result.get(
        "speed_rule",
        "NO SPEED DATA"
    )


    # ========================================================
    # TITLE
    # ========================================================

    draw_status(
        frame,
        "DRIVESAFE AI",
        (30, 40),
        1.0
    )

    draw_status(
        frame,
        "FINAL PRESENTATION DEMO",
        (30, 70),
        0.55
    )


    # ========================================================
    # DRIVING INFORMATION
    # ========================================================

    draw_status(
        frame,
        f"Vehicle State: {vehicle_state}",
        (30, 115)
    )

    draw_status(
        frame,
        f"Speed: {speed:.1f} km/h",
        (30, 150)
    )

    draw_status(
        frame,
        f"Speed Status: {speed_status}",
        (30, 185)
    )

    draw_status(
        frame,
        f"Speed Rule: {speed_rule}",
        (30, 220)
    )

    draw_status(
        frame,
        f"Mode: {mode}",
        (30, 255)
    )


    # ========================================================
    # AI MONITORING
    # ========================================================

    monitoring_text = (
        "AI Monitoring: ACTIVE"
        if ai_monitoring
        else
        "AI Monitoring: WAITING"
    )

    draw_status(
        frame,
        monitoring_text,
        (30, 300)
    )


    # ========================================================
    # DETECTIONS
    # ========================================================

    draw_status(
        frame,
        "DRIVER MONITORING",
        (30, 350),
        0.75
    )

    phone_text = (
        "PHONE: DETECTED"
        if phone
        else
        "PHONE: NOT DETECTED"
    )

    draw_status(
        frame,
        phone_text,
        (30, 390)
    )


    drowsiness_text = (
        "DROWSINESS: DETECTED"
        if drowsiness
        else
        "DROWSINESS: NOT DETECTED"
    )

    draw_status(
        frame,
        drowsiness_text,
        (30, 425)
    )


    yawning_text = (
        "YAWNING: DETECTED"
        if yawning
        else
        "YAWNING: NOT DETECTED"
    )

    draw_status(
        frame,
        yawning_text,
        (30, 460)
    )


    accident_text = (
        "ACCIDENT: DETECTED"
        if accident
        else
        "ACCIDENT: NOT DETECTED"
    )

    draw_status(
        frame,
        accident_text,
        (30, 495)
    )


    # ========================================================
    # SAFETY RESULT
    # ========================================================

    draw_status(
        frame,
        f"SAFETY LEVEL: {alert_level}",
        (30, 550),
        0.8
    )

    draw_status(
        frame,
        f"STATUS: {alert_status}",
        (30, 590),
        0.8
    )


    # ========================================================
    # DETECTION LIST
    # ========================================================

    detection_text = (
        ", ".join(detections)
        if detections
        else
        "NONE"
    )

    draw_status(
        frame,
        f"Active Detections: {detection_text}",
        (30, 630),
        0.55
    )


    # ========================================================
    # KEYBOARD CONTROLS
    # ========================================================

    draw_status(
        frame,
        "P=Phone  D=Drowsiness  Y=Yawning  A=Accident",
        (30, 665),
        0.48
    )

    draw_status(
        frame,
        "E=Emergency  N=Normal  Q=Quit",
        (30, 695),
        0.48
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    frame = cv2.resize(
        frame,
        (1100, 700)
    )

    cv2.imshow(
        WINDOW_NAME,
        frame
    )


    # ========================================================
    # KEYBOARD INPUT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if key == ord("p"):

        phone = not phone

        print(
            "Phone detection:",
            "ON" if phone else "OFF"
        )


    # --------------------------------------------------------
    # DROWSINESS
    # --------------------------------------------------------

    elif key == ord("d"):

        drowsiness = not drowsiness

        print(
            "Drowsiness detection:",
            "ON" if drowsiness else "OFF"
        )


    # --------------------------------------------------------
    # YAWNING
    # --------------------------------------------------------

    elif key == ord("y"):

        yawning = not yawning

        print(
            "Yawning detection:",
            "ON" if yawning else "OFF"
        )


    # --------------------------------------------------------
    # ACCIDENT
    # --------------------------------------------------------

    elif key == ord("a"):

        accident = not accident

        print(
            "Accident detection:",
            "ON" if accident else "OFF"
        )


    # --------------------------------------------------------
    # EMERGENCY MODE
    # --------------------------------------------------------

    elif key == ord("e"):

        DEMO_EMERGENCY = True

        try:
            system.driving_system.emergency_mode()
        except:
            pass

        print("EMERGENCY MODE ACTIVATED")


    # --------------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------------

    elif key == ord("n"):

        DEMO_EMERGENCY = False

        try:
            system.driving_system.normal_mode()
        except:
            pass

        print("NORMAL MODE ACTIVATED")


    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    elif key == ord("q"):

        break


    # ========================================================
    # TERMINAL STATUS
    # ========================================================

    current_time = time.time()

    if current_time - last_print >= 3:

        print("----------------------------------------------")
        print("Vehicle State:", vehicle_state)
        print("Speed:", speed)
        print("Mode:", mode)
        print("AI Monitoring:", ai_monitoring)
        print("Detections:", detections)
        print("Safety Level:", alert_level)
        print("Alert Status:", alert_status)

        last_print = current_time


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print("==============================================")
print("DriveSafe AI final demo stopped.")
print("Camera closed successfully.")
print("==============================================")