"""DriveSafe local prototype API. All emergency and V2X actions are simulated."""

from flask import Flask, jsonify, request

from emergency_service import EmergencyService
from event_logger import get_events, get_summary, log_event
import runtime_state

app = Flask(__name__)


@app.get("/")
def home():
    return "DriveSafe AI API. See /api/status, /api/events, /api/vehicle, /api/v2x."


@app.get("/api/status")
def api_status():
    state = runtime_state.snapshot()
    return jsonify({"system": "DriveSafe AI", "status": "Running",
                    "camera": state["camera"], "driver_status": state["driver_status"],
                    "detections": state["detections"], "safety_level": state["safety_level"],
                    "mode": state["mode"], "event_counts": get_summary(),
                    "speed_source": "SIMULATED GPS"})


@app.get("/api/events")
def api_events():
    limit = request.args.get("limit", default=100, type=int)
    return jsonify({"summary": get_summary(), "events": get_events(max(1, min(limit, 500)))})


@app.get("/api/vehicle")
def api_vehicle():
    state = runtime_state.snapshot()
    return jsonify({"vehicle_state": state["vehicle_state"], "speed": state["speed"],
                    "speed_source": "SIMULATED GPS", "mode": state["mode"],
                    "speed_rule": state.get("speed_rule", "NO SPEED DATA"),
                    "ai_monitoring": True, "gps": state["gps"]})


@app.post("/api/emergency")
def api_emergency():
    payload = request.get_json(silent=True) or {}
    event_type = str(payload.get("event_type", "EMERGENCY_DEMO"))[:80]
    state = runtime_state.snapshot()
    if state.get("mode") == "EMERGENCY" and state.get("emergency"):
        return jsonify(state["emergency"]), 200
    speed = state.get("speed", 0.0)
    notification = EmergencyService().trigger(event_type, speed=speed)
    event = log_event("EMERGENCY_DEMO", 3,
                      "API-triggered emergency simulation; no accident was detected and no services contacted. "
                      f"Location: {notification['location']['latitude']:.6f}, "
                      f"{notification['location']['longitude']:.6f}.")
    runtime_state.update(mode="EMERGENCY", safety_level=3,
                         safety_status="EMERGENCY", v2x=notification["v2x"],
                         emergency=notification, last_event=event)
    return jsonify(notification), 202


@app.get("/api/v2x")
def api_v2x():
    result = runtime_state.snapshot().get("v2x")
    return jsonify({"simulation": True, "status": "IDLE" if result is None else "SENT",
                    "result": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
