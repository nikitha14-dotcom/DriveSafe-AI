import time

# ============================================================
# DriveSafe AI - Safety Level Manager
# ============================================================

LEVEL_NORMAL = 0
LEVEL_WARNING = 1
LEVEL_HIGH_RISK = 2
LEVEL_EMERGENCY = 3


def get_safety_level(
    phone_detected=False,
    drowsiness_detected=False,
    seatbelt_missing=False,
    yawning_detected=False,
    distraction_detected=False,
    accident_detected=False
):

    # ========================================================
    # LEVEL 3 - EMERGENCY
    # ========================================================

    if accident_detected:

        return LEVEL_EMERGENCY, "EMERGENCY"


    # ========================================================
    # LEVEL 2 - HIGH RISK
    # ========================================================

    if drowsiness_detected:

        return LEVEL_HIGH_RISK, "HIGH RISK - DROWSINESS"


    # ========================================================
    # LEVEL 1 - WARNING
    # ========================================================

    warning_events = 0

    if phone_detected:
        warning_events += 1

    if seatbelt_missing:
        warning_events += 1

    if yawning_detected:
        warning_events += 1

    if distraction_detected:
        warning_events += 1

    if warning_events > 0:

        return LEVEL_WARNING, "WARNING"


    # ========================================================
    # NORMAL
    # ========================================================

    return LEVEL_NORMAL, "NORMAL"


# ============================================================
# DISPLAY FUNCTION
# ============================================================

def print_safety_status(level, message):

    print("----------------------------------------------")

    if level == LEVEL_NORMAL:

        print("SAFETY LEVEL: 0")
        print("STATUS:", message)

    elif level == LEVEL_WARNING:

        print("SAFETY LEVEL: 1")
        print("STATUS:", message)

    elif level == LEVEL_HIGH_RISK:

        print("SAFETY LEVEL: 2")
        print("STATUS:", message)

    elif level == LEVEL_EMERGENCY:

        print("SAFETY LEVEL: 3")
        print("STATUS:", message)

    print("----------------------------------------------")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("==============================================")
    print("DriveSafe AI - Safety Level Manager")
    print("==============================================")

    # Test 1 - Normal
    level, message = get_safety_level()

    print("\nTEST 1 - Normal")
    print_safety_status(level, message)


    # Test 2 - Phone
    level, message = get_safety_level(
        phone_detected=True
    )

    print("\nTEST 2 - Phone detected")
    print_safety_status(level, message)


    # Test 3 - Seat belt missing
    level, message = get_safety_level(
        seatbelt_missing=True
    )

    print("\nTEST 3 - Seat belt missing")
    print_safety_status(level, message)


    # Test 4 - Yawning
    level, message = get_safety_level(
        yawning_detected=True
    )

    print("\nTEST 4 - Yawning")
    print_safety_status(level, message)


    # Test 5 - Distraction
    level, message = get_safety_level(
        distraction_detected=True
    )

    print("\nTEST 5 - Distraction")
    print_safety_status(level, message)


    # Test 6 - Drowsiness
    level, message = get_safety_level(
        drowsiness_detected=True
    )

    print("\nTEST 6 - Drowsiness")
    print_safety_status(level, message)


    # Test 7 - Accident
    level, message = get_safety_level(
        accident_detected=True
    )

    print("\nTEST 7 - Accident")
    print_safety_status(level, message)

    print("\n==============================================")
    print("Safety Level Manager test completed.")
    print("==============================================")