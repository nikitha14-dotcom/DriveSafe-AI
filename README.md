# DriveSafe AI

DriveSafe AI is a university prototype for driver-safety monitoring. It combines real webcam observations with software-only vehicle, location, V2X, and emergency-notification simulations. It is not a vehicle control or emergency-response system.

## Features

- **Real camera AI:** YOLO phone detection (COCO class 67, confidence 0.70, two consecutive frames), MediaPipe eye-closure monitoring, sustained yawning detection, and sustained left/right/down head-direction distraction detection.
- **Risk levels:** emergency demonstration level 3, drowsiness level 2, and phone/distraction/yawning level 1. Accident detection is not integrated in the camera app. Level-specific alarms and event records occur when a detection starts, not once per frame.
- **Events:** SQLite event history at `database/drivesafe_events.db`. `DRIVESAFE_DB_PATH` can point to a different database file.
- **Dashboard and API:** A responsive mobile browser dashboard shows current detections, persistent per-detection counts, risk totals, and recent events. The phone page is read-only and works on the same trusted Wi-Fi as the PC.
- **Simulations:** demo speed, GPS coordinates, V2X recipients CAR_B/CAR_C/CAR_D, and emergency notification. They do not connect to GPS, OBD-II, physical V2X, or emergency services.

## Architecture

- `real_camera_integration.py` — primary real-camera app. It uses `phone_module.py`, `eye_closure.py`, `distraction_detector.py`, and `safety_manager.py`.
- `event_logger.py` — SQLite initialization, event transitions, event queries, and summary counts.
- `simulated_gps.py`, `v2x_simulator.py`, `emergency_service.py` — deterministic software simulations.
- `api_test.py` serves the phone dashboard and prototype API; `templates/dashboard.html` is the responsive live display.
- `dashboard.py` — existing Tkinter dashboard, now refreshes event counts, event history, and API status.
- `driving_system.py`, `driving_controller.py`, `mode_manager.py`, `speed_input.py`, `speed_manager.py`, and `vehicle_state.py` — existing speed and mode architecture, using demo speed only.
- `integrated_demo.py`, `main.py`, `accident_detector.py`, and other demos remain separate utilities. The primary camera app does not run their separate camera loops.

## Requirements and setup (Windows)

The `.replit` configuration targets Python 3.12, which was unavailable on the test PC. Python 3.11.9 successfully installed and ran the camera application. For a clean project-local setup in Command Prompt, use:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` lists the direct runtime packages for the camera app, API, and alarm. The YOLO detector uses `yolo11n.pt`; the face detector uses `models/face_landmarker.task`. Use the isolated environment so project dependencies stay separate from other Python applications.

## Run

Start the primary camera application:

```powershell
python real_camera_integration.py
```

The app opens the real webcam, performs AI monitoring, and serves the dashboard on this PC at `http://127.0.0.1:5000/`. Press **E** to run a clearly labeled emergency-workflow demonstration, **N** to return to normal mode, and **Q** to quit. Emergency mode leaves camera monitoring active and overrides the existing simulated speed restriction.

For phone access on the same trusted Wi-Fi, start in Command Prompt with:

```cmd
set DRIVESAFE_LAN=1
python real_camera_integration.py
```

The app prints the phone URL if it can identify the PC's Wi-Fi address. Otherwise run `ipconfig` on the PC and open `http://<PC-IPv4>:5000/` on the phone, for example `http://192.168.1.24:5000/`. If Windows Firewall asks, allow Python on **Private networks only**. Do not configure router port forwarding or expose this prototype to the public internet. The phone dashboard is read-only; emergency demo controls remain on the PC.

Start the dashboard in another terminal while the camera app is running:

```powershell
python dashboard.py
```

Run the API by itself, for API-only inspection without a camera, with:

```powershell
python api_test.py
```

Do not start this separate API command while the camera app already owns port 5000.

## API

- `GET /` — phone-friendly dashboard, refreshed every two seconds.
- `GET /api/status` — camera/runtime state, current detections, safety level, risk totals, and saved per-detection totals.
- `GET /api/events?limit=100` — latest detection transitions and per-type summary counts.
- `GET /api/vehicle` — simulated speed, vehicle state, mode, and simulated GPS.
- `POST /api/emergency` — explicitly starts an emergency demonstration and returns simulated GPS, V2X delivery, and notification status. It never contacts emergency services; this control accepts requests from the PC only.
- `GET /api/v2x` — most recent software-simulation delivery.

Example emergency demo request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/emergency -ContentType 'application/json' -Body '{"event_type":"EMERGENCY_DEMO"}'
```

## Testing

Run the hardware-free core tests:

```powershell
python -m unittest -v test_core_services
```

Compile Python files:

```powershell
python -m compileall .
```

The manual camera checks below need the runtime packages, camera, model files, and a stationary setup. Do not test while driving.

## Manual camera checks

1. Keep your head centered: the display should report `DRIVER SAFE` after neutral calibration.
2. Hold your head left, right, then down: after sustained movement, expect `DISTRACTION DETECTED`; return to center to clear it. This observes head direction and does not prove phone use.
3. Show a phone in frame for at least two confirmed detections: expect `PHONE DETECTED`. With no phone in view, the app must not claim one.
4. Close both eyes for about two seconds: expect `DROWSINESS DETECTED`.
5. Hold your mouth open past the yawning threshold: expect `YAWNING DETECTED`.
6. Press **E** for the emergency simulation, confirm the V2X recipients are reported, then press **N**. AI monitoring continues throughout.

## Limitations and future scope

- Distraction measures approximate head direction from face landmarks. Lighting, camera placement, face pose, calibration, and individual differences affect accuracy; it is a prototype signal, not proof of intent or phone use.
- **Accident detection is not integrated into the primary camera app.** The existing `accident_detector.py` is a separate motion-threshold demo; abrupt image motion is not reliable evidence of a vehicle accident. Emergency workflow is triggered manually or through the API and is labeled a simulation.
- Road/object tools are separate scripts and are not run by the primary driver camera.
- GPS coordinates, heading, speed, V2X messages, and notifications are simulated. There is no real GPS, OBD-II, physical V2X radio, emergency-service call, native mobile app, or production cloud deployment.
- Camera behavior must be validated on the target PC. This software is an academic prototype, not a safety-certified driver-assistance system.
