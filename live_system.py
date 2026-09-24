import time
from ai_driving_integration import AIDrivingIntegration


class LiveDriveSafeSystem:

    def __init__(self):
        print("DriveSafe AI - Live System")

        self.system = AIDrivingIntegration()
        self.speed = 50.0

        self.phone = False
        self.drowsiness = False
        self.yawning = False
        self.accident = False

    def update_detections(
        self,
        phone=False,
        drowsiness=False,
        yawning=False,
        accident=False
    ):
        self.phone = phone
        self.drowsiness = drowsiness
        self.yawning = yawning
        self.accident = accident

        self.system.update_ai(
            phone=phone,
            drowsiness=drowsiness,
            yawning=yawning,
            accident=accident
        )

    def process(self):
        result = self.system.process(self.speed)

        print("--------------------------------")
        print("Vehicle State:", result["vehicle_state"])
        print("Speed:", result["speed"])
        print("Speed Status:", result["speed_status"])
        print("Mode:", result["mode"])
        print("AI Monitoring:", result["ai_monitoring"])
        print("Detections:", result["detections"])
        print("Safety Level:", result["alert_level"])
        print("Alert Status:", result["alert_status"])

        return result


if __name__ == "__main__":

    live = LiveDriveSafeSystem()

    print("Driver Camera: READY")
    print("Front Camera: PENDING")
    print("Phone Detection: READY")
    print("Drowsiness Detection: READY")
    print("Yawning Detection: READY")
    print("Accident Detection: READY")
    print("Speed Source: SIMULATED GPS")
    print("Event Logger: READY")
    print("Dashboard: READY")

    print("\nTEST 1 - NORMAL DRIVING")
    live.speed = 50
    live.update_detections()
    live.process()

    print("\nTEST 2 - PHONE DETECTION")
    live.speed = 50
    live.update_detections(phone=True)
    live.process()

    print("\nTEST 3 - DROWSINESS DETECTION")
    live.speed = 50
    live.update_detections(drowsiness=True)
    live.process()

    print("\nTEST 4 - YAWNING DETECTION")
    live.speed = 50
    live.update_detections(yawning=True)
    live.process()

    print("\nTEST 5 - HIGH SPEED")
    live.speed = 80
    live.update_detections()
    live.process()

    print("\nTEST 6 - ACCIDENT")
    live.speed = 80
    live.update_detections(accident=True)
    live.process()

    print("\nLive system test completed.")