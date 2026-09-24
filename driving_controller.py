# ============================================================
# DRIVESAFE AI - DRIVING CONTROLLER
# Combines vehicle state + speed + driving mode
# ============================================================

from vehicle_state import VehicleState
from speed_manager import SpeedManager
from mode_manager import ModeManager


class DrivingController:

    def __init__(self, speed_limit=60):

        self.vehicle = VehicleState()
        self.speed = SpeedManager(speed_limit)
        self.mode = ModeManager(speed_limit)

    def update(self, current_speed):

        vehicle_state = self.vehicle.update(current_speed)

        speed_status = self.speed.get_status(current_speed)

        mode = self.mode.get_mode()

        speed_rule = self.mode.check_speed(current_speed)

        return {
            "speed": current_speed,
            "vehicle_state": vehicle_state,
            "speed_status": speed_status,
            "mode": mode,
            "speed_rule": speed_rule,
            "ai_monitoring": self.mode.ai_monitoring_active()
        }

    def activate_emergency(self):

        self.mode.activate_emergency_mode()

    def normal_mode(self):

        self.mode.set_normal_mode()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    controller = DrivingController(speed_limit=60)

    print("==============================================")
    print("DriveSafe AI - Driving Controller")
    print("==============================================")

    # --------------------------------------------------------
    # TEST 1 - Sitting / No speed data
    # --------------------------------------------------------

    print("\nTEST 1 - NO SPEED DATA")
    print("----------------------------------------------")

    result = controller.update(None)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 2 - Vehicle stopped
    # --------------------------------------------------------

    print("\nTEST 2 - VEHICLE STOPPED")
    print("----------------------------------------------")

    result = controller.update(0)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 3 - Normal driving
    # --------------------------------------------------------

    print("\nTEST 3 - NORMAL DRIVING")
    print("----------------------------------------------")

    result = controller.update(50)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 4 - Speed violation
    # --------------------------------------------------------

    print("\nTEST 4 - HIGH SPEED / NORMAL MODE")
    print("----------------------------------------------")

    result = controller.update(80)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 5 - Emergency mode
    # --------------------------------------------------------

    print("\nTEST 5 - EMERGENCY MODE")
    print("----------------------------------------------")

    controller.activate_emergency()

    result = controller.update(100)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n==============================================")
    print("Driving Controller test completed.")
    print("==============================================")