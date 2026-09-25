"""Deterministic GPS-like state for prototype and dashboard use only."""

from datetime import datetime, timezone


class SimulatedGPS:
    def __init__(self, latitude=37.4219999, longitude=-122.0840575):
        self.latitude = latitude
        self.longitude = longitude
        self.speed = 0.0
        self.heading = 0.0

    def update(self, speed=None, heading=None):
        if speed is not None:
            self.speed = float(speed)
        if heading is not None:
            self.heading = float(heading) % 360.0
        return self.snapshot()

    def snapshot(self):
        return {
            "source": "SIMULATED GPS",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "heading": self.heading,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
