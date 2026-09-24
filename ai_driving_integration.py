# ============================================================
# DRIVESAFE AI - AI + DRIVING INTEGRATION TEST
# ============================================================

from driving_system import DrivingSystem


class AIDrivingIntegration:

    def __init__(self):

        self.driving_system = DrivingSystem(speed_limit=60)

        self.phone_detected = False
        self.drowsiness_detected = False
        self.yawning_detected = False
        self.accident_detected = False

    # --------------------------------------------------------
    # UPDATE AI DETECTION STATUS
    # --------------------------------------------------------

    def update_ai(
        self,
        phone=False,
        drowsiness=False,
        yawning=False,
        accident=False
    ):

        self.phone_detected = phone
        self.drowsiness_detected = drowsiness
        self.yawning_detected = yawning
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

        # ----------------------------------------------------
        # DETECTION STATUS
        # ----------------------------------------------------

        detections = []

        if ai_monitoring:

            if self.phone_detected:
                detections.append("PHONE")

            if self.drowsiness_detected:
                detections.append("DROWSINESS")

            if self.yawning_detected:
                detections.append("YAWNING")

            if self.accident_detected:
                detections.append("ACCIDENT")

        # ----------------------------------------------------
        # ALERT LEVEL
        # ----------------------------------------------------

        if self.accident_detected:

            alert_level = 3
            alert_status = "EMERGENCY"

        elif self.drowsiness_detected:

            alert_level = 2
            alert_status = "HIGH RISK"

        elif (
            self.phone_detected
            or self.yawning_detected
        ):

            alert_level = 1
            alert_status = "WARNING"

        else:

            alert_level = 0
            alert_status = "NORMAL"

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