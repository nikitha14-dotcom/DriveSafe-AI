"""Primary DriveSafe AI camera application.

Camera observations are real. Speed, location, emergency notifications and V2X
delivery are software simulations. Press E to demonstrate an emergency workflow.
"""

import time
from pathlib import Path
from threading import Thread

PROJECT_ROOT = Path(__file__).resolve().parent
FACE_MODEL = PROJECT_ROOT / "models" / "face_landmarker.task"
EAR_THRESHOLD = 0.21
DROWSY_SECONDS = 2.0
MAR_THRESHOLD = 0.45
YAWN_SECONDS = 1.2
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]


def distance(p1, p2):
    import math
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def calculate_ear(landmarks, eye):
    a, b, c, d, e, f = (landmarks[index] for index in eye)
    horizontal = distance(a, d)
    return 0.0 if horizontal == 0 else (distance(b, f) + distance(c, e)) / (2 * horizontal)


def calculate_mar(landmarks):
    horizontal = distance(landmarks[61], landmarks[291])
    return 0.0 if horizontal == 0 else distance(landmarks[13], landmarks[14]) / horizontal


def run_camera(camera_id=0):
    try:
        import cv2
        import mediapipe as mp
        from phone_module import PhoneDetector
        from distraction_detector import DistractionDetector
        from eye_closure import eyes_closed, update_drowsiness
        from safety_manager import get_safety_level
        from event_logger import initialize_database, log_event
        from alert_manager import trigger_alert, stop_alert, close_alert_system
        from simulated_gps import SimulatedGPS
        from emergency_service import EmergencyService
        from driving_system import DrivingSystem
        import runtime_state
    except ImportError as exc:
        raise RuntimeError(f"Camera dependencies are unavailable: {exc}") from exc

    if not FACE_MODEL.is_file():
        raise FileNotFoundError(f"MediaPipe face model not found: {FACE_MODEL}")
    initialize_database()
    detector = PhoneDetector()
    distraction_detector = DistractionDetector()
    gps = SimulatedGPS()
    emergency_service = EmergencyService(gps=gps)
    driving_system = DrivingSystem(speed_limit=60)

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(FACE_MODEL)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_faces=1,
        output_face_blendshapes=True,
    )
    landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        landmarker.close()
        raise RuntimeError(f"Could not open camera {camera_id}.")

    closed_since = None
    yawn_since = None
    active = {"PHONE_DETECTED": False, "DROWSINESS": False,
              "YAWNING": False, "DISTRACTION_DETECTED": False}
    timestamp_ms = -1
    emergency_mode = False
    current_speed = 0.0  # Demonstration value; no vehicle interface is connected.
    print("DriveSafe AI camera monitoring started. Speed/GPS are simulated; press E for emergency demo, Q to quit.")
    runtime_state.update(camera="ACTIVE", driver_status="DRIVER SAFE", mode="NORMAL",
                         speed=current_speed, speed_source="SIMULATED GPS", gps=gps.snapshot(),
                         safety_level=0, safety_status="NORMAL",
                         detections={"phone": False, "drowsiness": False,
                                     "yawning": False, "distraction": False,
                                     "accident": False}, v2x=None)
    api_server = None
    try:
        from werkzeug.serving import make_server
        from api_test import app as api_app
        api_server = make_server("127.0.0.1", 5000, api_app, threaded=True)
        Thread(target=api_server.serve_forever, daemon=True).start()
        print("Local API started at http://127.0.0.1:5000")
    except OSError as exc:
        print(f"Local API was not started: {exc}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera frame could not be read.")
                break
            frame = cv2.flip(frame, 1)
            now = time.monotonic()
            phone_result = detector.detect(frame)
            phone = phone_result["detected"]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = max(timestamp_ms + 1, int(now * 1000))
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            face = bool(result.face_landmarks)
            drowsy = yawning = distraction = False
            direction = None
            ear = mar = 0.0
            if face:
                landmarks = result.face_landmarks[0]
                ear = (calculate_ear(landmarks, LEFT_EYE) + calculate_ear(landmarks, RIGHT_EYE)) / 2
                mar = calculate_mar(landmarks)
                blendshapes = result.face_blendshapes[0] if result.face_blendshapes else []
                closed_since, drowsy, _ = update_drowsiness(
                    eyes_closed(ear, blendshapes, EAR_THRESHOLD), closed_since, now, DROWSY_SECONDS
                )
                if mar >= MAR_THRESHOLD:
                    yawn_since = now if yawn_since is None else yawn_since
                    yawning = now - yawn_since >= YAWN_SECONDS
                else:
                    yawn_since = None
                distraction, direction, calibrated = distraction_detector.update(landmarks, now)
            else:
                closed_since = yawn_since = None
                distraction_detector.reset()
                calibrated = False

            detections = {
                "phone": phone, "drowsiness": drowsy, "yawning": yawning,
                "distraction": distraction, "accident": False,
            }
            level, level_name = get_safety_level(
                phone_detected=phone, drowsiness_detected=drowsy,
                yawning_detected=yawning, distraction_detected=distraction,
                accident_detected=False,
            )
            external_mode = runtime_state.snapshot().get("mode")
            if external_mode == "EMERGENCY" and not emergency_mode:
                emergency_mode = True
                driving_system.emergency_mode()
            elif external_mode == "NORMAL" and emergency_mode:
                emergency_mode = False
                driving_system.normal_mode()
            driving_state = driving_system.update(current_speed)
            if emergency_mode:
                level, level_name = 3, "EMERGENCY MODE"
            driver_status = (
                "DROWSINESS DETECTED" if drowsy else
                "PHONE DETECTED" if phone else
                "DISTRACTION DETECTED" if distraction else
                "YAWNING DETECTED" if yawning else
                "NO FACE" if not face else "DRIVER SAFE"
            )

            event_values = {
                "PHONE_DETECTED": (phone, 1),
                "DROWSINESS": (drowsy, 2),
                "YAWNING": (yawning, 1),
                "DISTRACTION_DETECTED": (distraction, 1),
            }
            for event_type, (is_active, event_level) in event_values.items():
                if is_active and not active[event_type]:
                    details = f"{event_type.replace('_', ' ').title()} detected by real camera AI."
                    if event_type == "DISTRACTION_DETECTED":
                        details += f" Sustained head direction: {direction}. This does not establish phone use."
                    log_event(event_type, event_level, details)
                    trigger_alert(details)
                active[event_type] = is_active

            location = gps.update(speed=current_speed)
            runtime_state.update(
                camera="ACTIVE", driver_status=driver_status,
                vehicle_state=driving_state["vehicle_state"],
                speed_rule=driving_state["speed_rule"],
                safety_level=level, safety_status=level_name,
                detections=detections, gps=location,
                mode="EMERGENCY" if emergency_mode else "NORMAL",
            )

            for x1, y1, x2, y2, confidence in phone_result["boxes"]:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"PHONE {confidence:.2f}", (x1, max(18, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
            color = (0, 0, 255) if level else (0, 210, 0)
            lines = ["DriveSafe AI | REAL CAMERA", driver_status,
                     f"Safety: {level_name}", f"Phone: {'YES' if phone else 'NO'}",
                     f"Drowsiness: {'YES' if drowsy else 'NO'}  EAR {ear:.2f}",
                     f"Yawning: {'YES' if yawning else 'NO'}  MAR {mar:.2f}",
                     f"Distraction: {direction or 'NO'} | calibration {'READY' if calibrated else 'CALIBRATING'}",
                     f"Speed: {current_speed:.0f} km/h (DEMO SPEED)",
                     f"Speed rule: {driving_state['speed_rule']}",
                     f"GPS: {location['latitude']:.5f}, {location['longitude']:.5f} (SIMULATED)",
                     f"Mode: {'EMERGENCY' if emergency_mode else 'NORMAL'} | E: emergency demo | Q: quit"]
            for row, line in enumerate(lines):
                cv2.putText(frame, line, (18, 28 + row * 29), cv2.FONT_HERSHEY_SIMPLEX,
                            0.56, color if row in (1, 2) else (245, 245, 245), 2)
            cv2.imshow("DriveSafe AI - Real Camera", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q")):
                break
            if key in (ord("e"), ord("E")) and not emergency_mode:
                emergency_mode = True
                notification = emergency_service.trigger("EMERGENCY_DEMO", speed=current_speed)
                event = log_event("EMERGENCY_DEMO", 3,
                                  "Manual emergency workflow demonstration; not a camera accident detection. "
                                  f"Location: {location['latitude']:.6f}, {location['longitude']:.6f}.")
                runtime_state.update(mode="EMERGENCY", safety_level=3,
                                     safety_status="EMERGENCY", v2x=notification["v2x"],
                                     emergency=notification, last_event=event)
                trigger_alert("EMERGENCY MODE - simulated notification and V2X sent")
                print("V2X ALERT SENT; CAR_B, CAR_C and CAR_D RECEIVED. Notification is simulated.")
            if key in (ord("n"), ord("N")) and emergency_mode:
                emergency_mode = False
                driving_system.normal_mode()
                level, level_name = get_safety_level(
                    phone_detected=phone, drowsiness_detected=drowsy,
                    yawning_detected=yawning, distraction_detected=distraction,
                )
                runtime_state.update(mode="NORMAL", safety_level=level,
                                     safety_status=level_name)
                print("Returned to NORMAL MODE.")
    finally:
        runtime_state.update(camera="STOPPED", driver_status="NOT MONITORING")
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()
        if api_server is not None:
            api_server.shutdown()
        stop_alert()
        close_alert_system()
        print("Camera monitoring stopped.")


if __name__ == "__main__":
    try:
        run_camera()
    except (RuntimeError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
