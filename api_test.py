"""DriveSafe local dashboard/API. Emergency and V2X actions are simulations."""

from flask import Flask, jsonify, render_template, request

from emergency_service import EmergencyService
from event_logger import get_event_counts_by_type, get_events, get_summary, log_event
import runtime_state

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("dashboard.html")


@app.get("/api/status")
def api_status():
    state = runtime_state.snapshot()
    return jsonify({
        "system": "DriveSafe AI", "status": "Running",
        "camera": state["camera"], "driver_status": state["driver_status"],
        "detections": state["detections"],
        "accident_detection": state.get("accident_detection", "NOT_INTEGRATED"),
        "vehicle_state": state["vehicle_state"],
        "ai_monitoring": state["camera"] == "ACTIVE",
        "driving_alerts_enabled": (state["camera"] == "ACTIVE" and
                                   (state["vehicle_state"] == "DRIVING" or state["mode"] == "EMERGENCY")),
        "safety_level": state["safety_level"],
        "safety_status": state.get("safety_status", "NORMAL"),
        "mode": state["mode"], "event_counts": get_summary(),
        "detection_counts": get_event_counts_by_type(),
        "speed": state.get("speed", 0.0),
        "speed_source": "SIMULATED GPS", "gps": state.get("gps"),
        "v2x_status": "IDLE" if state.get("v2x") is None else "SENT",
    })


@app.get("/api/events")
def api_events():
    limit = request.args.get("limit", default=100, type=int)
    return jsonify({
        "summary": get_summary(),
        "counts_by_type": get_event_counts_by_type(),
        "events": get_events(max(1, min(limit, 500))),
    })


@app.get("/api/vehicle")
def api_vehicle():
    state = runtime_state.snapshot()
    return jsonify({"vehicle_state": state["vehicle_state"],
                    "speed": state.get("speed", 0.0),
                    "speed_source": "SIMULATED GPS", "mode": state["mode"],
                    "speed_rule": state.get("speed_rule", "NO SPEED DATA"),
                    "ai_monitoring": state["camera"] == "ACTIVE",
                    "driving_alerts_enabled": (state["camera"] == "ACTIVE" and
                                               (state["vehicle_state"] == "DRIVING" or state["mode"] == "EMERGENCY")),
                    "accident_detection": state.get("accident_detection", "NOT_INTEGRATED"),
                    "gps": state["gps"]})


@app.post("/api/emergency")
def api_emergency():
    # The phone dashboard is read-only; trigger the demo at the PC keyboard.
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Run the emergency demonstration at the PC."}), 403
    payload = request.get_json(silent=True) or {}
    event_type = str(payload.get("event_type", "EMERGENCY_DEMO"))
    if event_type not in {"EMERGENCY_DEMO", "ACCIDENT_DEMO"}:
        return jsonify({"error": "Use EMERGENCY_DEMO or ACCIDENT_DEMO."}), 400
    state = runtime_state.snapshot()
    if state.get("mode") == "EMERGENCY" and state.get("emergency"):
        return jsonify(state["emergency"]), 200
    speed = state.get("speed", 0.0)
    notification = EmergencyService().trigger(event_type, speed=speed)
    event_message = (
        "Manual accident workflow demo; no accident was detected and no services contacted. "
        if event_type == "ACCIDENT_DEMO" else
        "API-triggered emergency simulation; no accident was detected and no services contacted. "
    )
    event = log_event(event_type, 3, event_message +
                      f"Location: {notification['location']['latitude']:.6f}, "
                      f"{notification['location']['longitude']:.6f}.")
    runtime_state.update(mode="EMERGENCY", safety_level=3,
                         safety_status="EMERGENCY", v2x=notification["v2x"],
                         emergency=notification, last_event=event,
                         accident_detection=("MANUAL WORKFLOW DEMO - NOT DETECTED"
                                              if event_type == "ACCIDENT_DEMO" else "NOT_INTEGRATED"))
    try:
        from alert_manager import trigger_alert
        trigger_alert("EMERGENCY MODE - simulated notification and V2X sent", level=3)
    except Exception as exc:
        app.logger.warning("Could not play emergency alert: %s", exc)
    return jsonify(notification), 202


@app.get("/api/v2x")
def api_v2x():
    result = runtime_state.snapshot().get("v2x")
    return jsonify({"simulation": True, "status": "IDLE" if result is None else "SENT",
                    "result": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
