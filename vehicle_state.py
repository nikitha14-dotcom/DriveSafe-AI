# ============================================================
# DRIVESAFE AI - VEHICLE STATE MANAGER
# ============================================================

class VehicleState:

    def __init__(self):
        self.speed = None
        self.state = "NOT DRIVING"

    # --------------------------------------------------------
    # UPDATE SPEED
    # --------------------------------------------------------

    def update(self, speed):

        self.speed = speed

        # No real speed information
        if speed is None:
            self.state = "NOT DRIVING"

        # Vehicle stopped
        elif speed <= 0:
            self.state = "STOPPED"

        # Vehicle moving
        else:
            self.state = "DRIVING"

        return self.state

    # --------------------------------------------------------
    # GET CURRENT STATE
    # --------------------------------------------------------

    def get_state(self):
        return self.state

    # --------------------------------------------------------
    # CHECK DRIVING
    # --------------------------------------------------------

    def is_driving(self):

        return self.state == "DRIVING"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    vehicle = VehicleState()

    print("==============================================")
    print("DriveSafe AI - Vehicle State Manager")
    print("==============================================")

    test_values = [
        None,
        0,
        20,
        45,
        60
    ]

    for speed in test_values:

        state = vehicle.update(speed)

        print("----------------------------------------------")

        if speed is None:
            print("Speed: NOT AVAILABLE")
        else:
            print("Speed:", speed, "km/h")

        print("Vehicle State:", state)
        print("Driving:", vehicle.is_driving())

    print("==============================================")
    print("Vehicle State Manager test completed.")
    print("==============================================")