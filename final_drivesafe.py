"""Console-only simulation of the vehicle and safety state modules."""

from driving_system import DrivingSystem
from safety_manager import get_safety_level


def run_demo():
    system = DrivingSystem(speed_limit=60)
    scenarios = [
        ("NO SPEED SOURCE", None, {}),
        ("STOPPED", 0, {}),
        ("NORMAL DEMO SPEED", 50, {}),
        ("PHONE WARNING", 50, {"phone_detected": True}),
        ("DROWSINESS HIGH RISK", 50, {"drowsiness_detected": True}),
        ("EMERGENCY MODE SIMULATION", 50, {"accident_detected": True}),
    ]
    for name, speed, detections in scenarios:
        if name == "EMERGENCY MODE SIMULATION":
            system.emergency_mode()
        else:
            system.normal_mode()
        state = system.update(speed)
        level, status = get_safety_level(**detections)
        if system.controller.mode.get_mode() == "EMERGENCY":
            level, status = 3, "EMERGENCY MODE SIMULATION"
        print(f"{name}: speed={speed!r} ({state['speed_source']}), "
              f"vehicle={state['vehicle_state']}, mode={state['mode']}, "
              f"speed_rule={state['speed_rule']}, AI monitoring={state['ai_monitoring']}, "
              f"safety={level} {status}")
    print("Emergency notifications and vehicle hardware are not connected.")


if __name__ == "__main__":
    run_demo()
