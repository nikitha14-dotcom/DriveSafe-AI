# ============================================================
# DRIVESAFE AI - AI + DRIVING INTEGRATION TEST
# ============================================================

from driving_system import DrivingSystem
from safety_manager import get_safety_level


class AIDrivingIntegration:

    def __init__(self):

        self.driving_system = DrivingSystem(speed_limit=60)

        self.phone_detected = False
        self.drowsiness_detected = False
        self.yawning_detected = False
        self.distraction_detected = False
        self.seatbelt_missing = False
        self.accident_detected = False

    # --------------------------------------------------------
    # UPDATE AI DETECTION STATUS
    # --------------------------------------------------------

    def update_ai(
        self,
        phone=False,
        drowsiness=False,
        yawning=False,
        accident=False,
        distraction=False,
        seatbelt_missing=False,
    ):

        self.phone_detected = phone
        self.drowsiness_detected = drowsiness
        self.yawning_detected = yawning
        self.distraction_detected = distraction
        self.seatbelt_missing = seatbelt_missing
        self.accident_detected = accident

    # --------------------------------------------------------
    # PROCESS SYSTEM
    # --------------------------------------------------------

    def process(self, speed=None):

        driving_result = self.driving_system.update(speed)

        # ----------------------------------------------------
        # AI monitoring remains active while driving
        # ----------------------------------------------------

        ai_monitoring = driving_result["ai_monitoring"]
        alerts_enabled = driving_result["driving_alerts_enabled"]
        emergency_active = driving_result["mode"] == "EMERGENCY"

        # ----------------------------------------------------
        # DETECTION STATUS
        # ----------------------------------------------------

        detections = []

        if alerts_enabled:

            if self.phone_detected:
                detections.append("PHONE")

            if self.drowsiness_detected:
                detections.append("DROWSINESS")

            if self.yawning_detected:
                detections.append("YAWNING")

            if self.distraction_detected:
                detections.append("DISTRACTION")

            if self.seatbelt_missing:
                detections.append("SEATBELT_MISSING")

            if self.accident_detected:
                detections.append("ACCIDENT")

        # ----------------------------------------------------
        # ALERT LEVEL
        # ----------------------------------------------------

        alert_level, alert_status = get_safety_level(
            phone_detected=self.phone_detected and alerts_enabled,
            drowsiness_detected=self.drowsiness_detected and alerts_enabled,
            seatbelt_missing=self.seatbelt_missing and alerts_enabled,
            yawning_detected=self.yawning_detected and alerts_enabled,
            distraction_detected=self.distraction_detected and alerts_enabled,
            accident_detected=self.accident_detected,
        )
        if emergency_active and not self.accident_detected:
            alert_level, alert_status = 3, "EMERGENCY MODE"

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            **driving_result,
            "detections": detections,
            "alert_level": alert_level,
            "alert_status": alert_status
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    system = AIDrivingIntegration()

    print("==============================================")
    print("DriveSafe AI - AI Driving Integration")
    print("==============================================")

    # --------------------------------------------------------
    # TEST 1
    # Sitting in room
    # --------------------------------------------------------

    print("\nTEST 1 - NOT DRIVING")
    print("----------------------------------------------")

    system.update_ai(
        phone=True,
        drowsiness=True,
        yawning=True
    )

    result = system.process(None)

    print("Vehicle State:", result["vehicle_state"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Detections:", result["detections"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    # --------------------------------------------------------
    # TEST 2
    # Normal driving
    # --------------------------------------------------------

    print("\nTEST 2 - NORMAL DRIVING")
    print("----------------------------------------------")

    system.update_ai()

    result = system.process(50)

    print("Vehicle State:", result["vehicle_state"])
    print("Speed:", result["speed"])
    print("Mode:", result["mode"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Detections:", result["detections"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    # --------------------------------------------------------
    # TEST 3
    # Phone detected
    # --------------------------------------------------------

    print("\nTEST 3 - PHONE DETECTED")
    print("----------------------------------------------")

    system.update_ai(phone=True)

    result = system.process(50)

    print("Vehicle State:", result["vehicle_state"])
    print("Speed:", result["speed"])
    print("Mode:", result["mode"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Detections:", result["detections"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    # --------------------------------------------------------
    # TEST 4
    # Drowsiness detected
    # --------------------------------------------------------

    print("\nTEST 4 - DROWSINESS DETECTED")
    print("----------------------------------------------")

    system.update_ai(drowsiness=True)

    result = system.process(50)

    print("Vehicle State:", result["vehicle_state"])
    print("Speed:", result["speed"])
    print("Mode:", result["mode"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Detections:", result["detections"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    # --------------------------------------------------------
    # TEST 5
    # High speed
    # --------------------------------------------------------

    print("\nTEST 5 - HIGH SPEED")
    print("----------------------------------------------")

    system.update_ai()

    result = system.process(80)

    print("Vehicle State:", result["vehicle_state"])
    print("Speed:", result["speed"])
    print("Mode:", result["mode"])
    print("Speed Rule:", result["speed_rule"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    # --------------------------------------------------------
    # TEST 6
    # Emergency mode
    # --------------------------------------------------------

    print("\nTEST 6 - EMERGENCY MODE")
    print("----------------------------------------------")

    system.driving_system.emergency_mode()

    system.update_ai(accident=True)

    result = system.process(100)

    print("Vehicle State:", result["vehicle_state"])
    print("Speed:", result["speed"])
    print("Mode:", result["mode"])
    print("Speed Rule:", result["speed_rule"])
    print("AI Monitoring:", result["ai_monitoring"])
    print("Detections:", result["detections"])
    print("Alert Level:", result["alert_level"])
    print("Alert Status:", result["alert_status"])

    print("\n==============================================")
    print("AI Driving Integration test completed.")
    print("==============================================")
