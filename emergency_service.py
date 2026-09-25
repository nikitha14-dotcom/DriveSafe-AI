"""Prototype emergency workflow; does not contact real emergency services."""

from simulated_gps import SimulatedGPS
from v2x_simulator import V2XSimulator


class EmergencyService:
    def __init__(self, gps=None, v2x=None):
        self.gps = gps or SimulatedGPS()
        self.v2x = v2x or V2XSimulator()
        self.notifications = []

    def trigger(self, event_type="ACCIDENT", speed=None, heading=None):
        location = self.gps.update(speed=speed, heading=heading)
        v2x_result = self.v2x.broadcast_emergency(event_type, 3, location)
        notification = {
            "status": "SIMULATED EMERGENCY NOTIFICATION",
            "message": "Prototype notification recorded; no services contacted.",
            "event_type": event_type,
            "location": location,
            "v2x": v2x_result,
        }
        self.notifications.append(notification)
        return notification
