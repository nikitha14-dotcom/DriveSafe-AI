# ============================================================
# DRIVESAFE AI - SPEED MANAGER
# ============================================================

class SpeedManager:

    def __init__(self, speed_limit=60):
        self.speed_limit = speed_limit

    def get_status(self, speed):

        # No real speed information available
        if speed is None:
            return "NO SPEED DATA"

        if speed <= 0:
            return "STOPPED"

        elif speed <= 30:
            return "SLOW"

        elif speed <= self.speed_limit:
            return "MEDIUM"

        else:
            return "FAST"

    def is_vehicle_moving(self, speed):

        if speed is None:
            return False

        return speed > 0

    def is_speed_violation(self, speed):

        if speed is None:
            return False

        return speed > self.speed_limit


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    manager = SpeedManager(speed_limit=60)

    print("==============================================")
    print("DriveSafe AI - Speed Manager")
    print("==============================================")

    test_speeds = [None, 0, 20, 45, 60, 80]

    for speed in test_speeds:

        status = manager.get_status(speed)
        moving = manager.is_vehicle_moving(speed)
        violation = manager.is_speed_violation(speed)

        print("----------------------------------------------")

        if speed is None:
            print("Speed: NOT AVAILABLE")
        else:
            print("Speed:", speed, "km/h")

        print("Status:", status)
        print("Vehicle Moving:", moving)
        print("Speed Violation:", violation)

    print("==============================================")
    print("Speed Manager test completed.")
    print("==============================================")