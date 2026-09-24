# ============================================================
# DRIVESAFE AI - SPEED INPUT
# ============================================================

class SpeedInput:

    def __init__(self):
        self.speed = None
        self.source = "NO SPEED SOURCE"

    # --------------------------------------------------------
    # SET SPEED
    # --------------------------------------------------------

    def set_speed(self, speed):

        if speed is None:
            self.speed = None
            self.source = "NO SPEED SOURCE"

        else:
            self.speed = float(speed)
            self.source = "SIMULATED GPS"

    # --------------------------------------------------------
    # GET SPEED
    # --------------------------------------------------------

    def get_speed(self):

        return self.speed

    # --------------------------------------------------------
    # GET SOURCE
    # --------------------------------------------------------

    def get_source(self):

        return self.source


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    speed_input = SpeedInput()

    print("==============================================")
    print("DriveSafe AI - Speed Input")
    print("==============================================")

    print("\nTEST 1 - No speed source")
    print("----------------------------------------------")

    speed_input.set_speed(None)

    print("Speed:", speed_input.get_speed())
    print("Source:", speed_input.get_source())

    print("\nTEST 2 - Simulated GPS")
    print("----------------------------------------------")

    speed_input.set_speed(45)

    print("Speed:", speed_input.get_speed(), "km/h")
    print("Source:", speed_input.get_source())

    print("\n==============================================")
    print("Speed Input test completed.")
    print("==============================================")