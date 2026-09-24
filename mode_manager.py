# ============================================================
# DRIVESAFE AI - NORMAL / EMERGENCY MODE MANAGER
# ============================================================

class ModeManager:

    def __init__(self, speed_limit=60):

        self.speed_limit = speed_limit
        self.emergency_mode = False

    # --------------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------------

    def set_normal_mode(self):

        self.emergency_mode = False

    # --------------------------------------------------------
    # EMERGENCY MODE
    # --------------------------------------------------------

    def activate_emergency_mode(self):

        self.emergency_mode = True

    # --------------------------------------------------------
    # GET MODE
    # --------------------------------------------------------

    def get_mode(self):

        if self.emergency_mode:
            return "EMERGENCY"

        return "NORMAL"

    # --------------------------------------------------------
    # SPEED CHECK
    # --------------------------------------------------------

    def check_speed(self, speed):

        # No speed data
        if speed is None:
            return "NO SPEED DATA"

        # Emergency mode overrides normal speed restriction
        if self.emergency_mode:
            return "SPEED OVERRIDE"

        # Normal mode
        if speed > self.speed_limit:
            return "SPEED WARNING"

        return "SPEED NORMAL"

    # --------------------------------------------------------
    # AI DETECTION STATUS
    # --------------------------------------------------------

    def ai_monitoring_active(self):

        # AI monitoring remains active in BOTH modes
        return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    manager = ModeManager(speed_limit=60)

    print("==============================================")
    print("DriveSafe AI - Mode Manager")
    print("==============================================")

    # --------------------------------------------------------
    # TEST 1 - NORMAL MODE
    # --------------------------------------------------------

    print("\nTEST 1 - NORMAL MODE")
    print("----------------------------------------------")

    manager.set_normal_mode()

    print("Mode:", manager.get_mode())
    print("Speed:", 50, "km/h")
    print("Speed Status:", manager.check_speed(50))
    print("AI Monitoring:", manager.ai_monitoring_active())

    # --------------------------------------------------------
    # TEST 2 - SPEED WARNING
    # --------------------------------------------------------

    print("\nTEST 2 - NORMAL MODE / HIGH SPEED")
    print("----------------------------------------------")

    print("Mode:", manager.get_mode())
    print("Speed:", 80, "km/h")
    print("Speed Status:", manager.check_speed(80))
    print("AI Monitoring:", manager.ai_monitoring_active())

    # --------------------------------------------------------
    # TEST 3 - EMERGENCY MODE
    # --------------------------------------------------------

    print("\nTEST 3 - EMERGENCY MODE")
    print("----------------------------------------------")

    manager.activate_emergency_mode()

    print("Mode:", manager.get_mode())
    print("Speed:", 100, "km/h")
    print("Speed Status:", manager.check_speed(100))
    print("AI Monitoring:", manager.ai_monitoring_active())

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n==============================================")
    print("Mode Manager test completed.")
    print("==============================================")