"""In-process software-only V2X message fan-out simulation."""


class V2XSimulator:
    def __init__(self, vehicle_id="CAR_A", recipients=("CAR_B", "CAR_C", "CAR_D")):
        self.vehicle_id = vehicle_id
        self.recipients = tuple(recipients)
        self.sent_messages = []

    def broadcast_emergency(self, event_type, severity, location):
        message = {
            "vehicle_id": self.vehicle_id,
            "event_type": event_type,
            "severity": int(severity),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "speed": location["speed"],
            "heading": location["heading"],
            "timestamp": location["timestamp"],
            "simulation": True,
        }
        delivery = {"status": "V2X ALERT SENT", "message": message,
                    "recipients": [{"vehicle_id": vehicle, "status": "RECEIVED"}
                                   for vehicle in self.recipients]}
        self.sent_messages.append(delivery)
        return delivery
