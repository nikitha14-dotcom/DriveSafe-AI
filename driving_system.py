# ============================================================
# DRIVESAFE AI - DRIVING SYSTEM
# Speed Input + Vehicle State + Speed Manager + Mode Manager
# ============================================================

from speed_input import SpeedInput
from driving_controller import DrivingController


class DrivingSystem:

    def __init__(self, speed_limit=60):

        self.speed_input = SpeedInput()
        self.controller = DrivingController(speed_limit)

    # --------------------------------------------------------
    # UPDATE SYSTEM
    # --------------------------------------------------------

    def update(self, speed=None):

        self.speed_input.set_speed(speed)

        current_speed = self.speed_input.get_speed()

        result = self.controller.update(current_speed)

        result["speed_source"] = self.speed_input.get_source()

        return result

    # --------------------------------------------------------
    # EMERGENCY MODE
    # --------------------------------------------------------

    def emergency_mode(self):

        self.controller.activate_emergency()

    # --------------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------------

    def normal_mode(self):

        self.controller.normal_mode()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    system = DrivingSystem(speed_limit=60)

    print("==============================================")
    print("DriveSafe AI - Driving System")
    print("==============================================")

    # --------------------------------------------------------
    # TEST 1 - Sitting in room
    # --------------------------------------------------------

    print("\nTEST 1 - NO SPEED SOURCE")
    print("----------------------------------------------")

    result = system.update(None)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 2 - Vehicle stopped
    # --------------------------------------------------------

    print("\nTEST 2 - VEHICLE STOPPED")
    print("----------------------------------------------")

    result = system.update(0)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 3 - Normal driving
    # --------------------------------------------------------

    print("\nTEST 3 - NORMAL DRIVING")
    print("----------------------------------------------")

    result = system.update(50)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 4 - Speed violation
    # --------------------------------------------------------

    print("\nTEST 4 - SPEED VIOLATION")
    print("----------------------------------------------")

    result = system.update(80)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 5 - Emergency mode
    # --------------------------------------------------------

    print("\nTEST 5 - EMERGENCY MODE")
    print("----------------------------------------------")

    system.emergency_mode()

    result = system.update(100)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n==============================================")
    print("Driving System test completed.")
    print("==============================================")