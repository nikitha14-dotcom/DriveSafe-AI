import time

from speed_input import get_speed
from driving_system import get_driving_system
from ai_driving_integration import evaluate_ai_state


# ============================================================
# DRIVESAFE AI - FINAL SYSTEM CONTROLLER
# ============================================================

print("==============================================")
print("      DRIVESAFE AI - FINAL SYSTEM")
print("==============================================")

print("Starting DriveSafe AI...")
print()


# ============================================================
# SYSTEM STATE
# ============================================================

system_running = True

last_speed = None
current_mode = "NORMAL"


# ============================================================
# DISPLAY FUNCTION
# ============================================================

def display_system_state(speed, system):

    print("----------------------------------------------")

    if speed is None:
        print("Speed          : NOT AVAILABLE")
    else:
        print(f"Speed          : {speed:.1f} km/h")

    print(f"Vehicle State  : {system['vehicle_state']}")
    print(f"Speed Status   : {system['speed_status']}")
    print(f"Mode           : {system['mode']}")
    print(f"Speed Rule     : {system['speed_rule']}")
    print(f"AI Monitoring  : {system['ai_monitoring']}")


# ============================================================
# DEMONSTRATION DATA
# ============================================================

test_cases = [

    {
        "name": "SYSTEM NOT DRIVING",
        "speed": None,
        "detections": []
    },

    {
        "name": "VEHICLE STOPPED",
        "speed": 0,
        "detections": []
    },

    {
        "name": "NORMAL DRIVING",
        "speed": 50,
        "detections": []
    },

    {
        "name": "PHONE DETECTION",
        "speed": 50,
        "detections": ["PHONE"]
    },

    {
        "name": "DROWSINESS DETECTION",
        "speed": 50,
        "detections": ["DROWSINESS"]
    },

    {
        "name": "HIGH SPEED",
        "speed": 80,
        "detections": []
    },

    {
        "name": "EMERGENCY MODE",
        "speed": 100,
        "detections": ["ACCIDENT"]
    }

]


# ============================================================
# RUN SYSTEM TEST
# ============================================================

for index, test in enumerate(test_cases, start=1):

    print()
    print(f"TEST {index} - {test['name']}")

    speed = test["speed"]
    detections = test["detections"]

    # --------------------------------------------------------
    # Driving system
    # --------------------------------------------------------

    system = get_driving_system(
        speed=speed,
        emergency_mode=(test["name"] == "EMERGENCY MODE")
    )

    display_system_state(speed, system)

    # --------------------------------------------------------
    # AI integration
    # --------------------------------------------------------

    ai_result = evaluate_ai_state(
        vehicle_state=system["vehicle_state"],
        speed=speed,
        mode=system["mode"],
        detections=detections
    )

    print(f"Detections    : {detections}")
    print(f"Alert Level   : {ai_result['alert_level']}")
    print(f"Alert Status  : {ai_result['alert_status']}")

    # --------------------------------------------------------
    # Emergency
    # --------------------------------------------------------

    if ai_result["alert_level"] == 3:

        print("!!! EMERGENCY ALERT !!!")
        print("Emergency team notification required.")

    elif ai_result["alert_level"] == 2:

        print("!!! HIGH RISK WARNING !!!")

    elif ai_result["alert_level"] == 1:

        print("!!! DRIVER WARNING !!!")

    else:

        print("System Status : NORMAL")


# ============================================================
# FINISH
# ============================================================

print()
print("==============================================")
print("DriveSafe AI final system test completed.")
print("==============================================")