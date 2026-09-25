"""Small in-process status store shared by the camera loop and Flask API."""

from copy import deepcopy
from threading import RLock

_lock = RLock()
_state = {
    "camera": "STOPPED",
    "driver_status": "NOT MONITORING",
    "vehicle_state": "STOPPED",
    "speed": 0.0,
    "speed_source": "SIMULATED GPS",
    "mode": "NORMAL",
    "speed_rule": "SPEED NORMAL",
    "safety_level": 0,
    "detections": {"phone": False, "drowsiness": False, "yawning": False,
                   "distraction": False, "accident": False},
    "accident_detection": "NOT_INTEGRATED",
    "gps": None,
    "v2x": None,
}


def update(**values):
    with _lock:
        _state.update(values)
        return deepcopy(_state)


def snapshot():
    with _lock:
        return deepcopy(_state)
