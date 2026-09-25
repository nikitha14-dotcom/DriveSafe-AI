"""Safe, hardware-free tests for DriveSafe core services."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import event_logger
from api_test import app
from distraction_detector import DistractionDetector
from emergency_service import EmergencyService
from safety_manager import get_safety_level
from ai_driving_integration import AIDrivingIntegration
from driving_system import DrivingSystem
import runtime_state


class CoreServiceTests(unittest.TestCase):
    def setUp(self):
        self.old_database = event_logger.DATABASE
        self.old_runtime = runtime_state.snapshot()
        self.temp_dir = tempfile.TemporaryDirectory()
        event_logger.DATABASE = Path(self.temp_dir.name) / "database" / "events.db"

    def tearDown(self):
        event_logger.DATABASE = self.old_database
        runtime_state.update(**self.old_runtime)
        self.temp_dir.cleanup()

    def _landmarks(self, yaw_shift=0.0, pitch_shift=0.0):
        points = [SimpleNamespace(x=0.5, y=0.5) for _ in range(468)]
        points[234] = SimpleNamespace(x=0.2, y=0.5)
        points[454] = SimpleNamespace(x=0.8, y=0.5)
        points[1] = SimpleNamespace(x=0.5 + yaw_shift, y=0.55 + pitch_shift)
        points[159] = SimpleNamespace(x=0.43, y=0.35)
        points[386] = SimpleNamespace(x=0.57, y=0.35)
        points[152] = SimpleNamespace(x=0.5, y=0.9)
        return points

    def test_safety_priority(self):
        self.assertEqual(get_safety_level(phone_detected=True, drowsiness_detected=True,
                                          accident_detected=True)[0], 3)
        self.assertEqual(get_safety_level(phone_detected=True, drowsiness_detected=True)[0], 2)
        self.assertEqual(get_safety_level(phone_detected=True, distraction_detected=True)[0], 1)

    def test_distraction_requires_sustained_direction_and_clears(self):
        detector = DistractionDetector(duration=1.7, calibration_samples=5)
        neutral = self._landmarks()
        for index in range(5):
            active, _, _ = detector.update(neutral, index * 0.03)
            self.assertFalse(active)
        active, direction, _ = detector.update(self._landmarks(yaw_shift=-0.08), 1.0)
        self.assertFalse(active)
        active, direction, _ = detector.update(self._landmarks(yaw_shift=-0.08), 2.8)
        self.assertTrue(active)
        self.assertEqual(direction, "LEFT")
        active, direction, _ = detector.update(neutral, 2.9)
        self.assertFalse(active)
        self.assertIsNone(direction)
        active, direction, _ = detector.update(self._landmarks(yaw_shift=0.08), 3.0)
        self.assertFalse(active)
        active, direction, _ = detector.update(self._landmarks(yaw_shift=0.08), 4.8)
        self.assertTrue(active)
        self.assertEqual(direction, "RIGHT")
        detector.update(neutral, 4.9)
        active, direction, _ = detector.update(self._landmarks(pitch_shift=0.10), 5.0)
        self.assertFalse(active)
        active, direction, _ = detector.update(self._landmarks(pitch_shift=0.10), 6.8)
        self.assertTrue(active)
        self.assertEqual(direction, "DOWN")

    def test_existing_driving_integration_uses_safety_priority(self):
        system = AIDrivingIntegration()
        system.update_ai(phone=True, drowsiness=True, distraction=True)
        parked = system.process(0)
        self.assertEqual(parked["vehicle_state"], "STOPPED")
        self.assertTrue(parked["ai_monitoring"])
        self.assertFalse(parked["driving_alerts_enabled"])
        self.assertEqual(parked["detections"], [])
        self.assertEqual(parked["alert_level"], 0)
        result = system.process(50)
        self.assertEqual(result["alert_level"], 2)
        self.assertIn("DISTRACTION", result["detections"])
        system.driving_system.emergency_mode()
        system.update_ai(accident=True)
        result = system.process(80)
        self.assertEqual(result["alert_level"], 3)
        self.assertEqual(result["speed_rule"], "SPEED OVERRIDE")
        self.assertTrue(result["ai_monitoring"])
        self.assertTrue(result["driving_alerts_enabled"])

    def test_emergency_keeps_ai_monitoring_active_while_stopped(self):
        system = AIDrivingIntegration()
        system.driving_system.emergency_mode()
        system.update_ai(phone=True)
        result = system.process(0)
        self.assertEqual(result["vehicle_state"], "STOPPED")
        self.assertTrue(result["ai_monitoring"])
        self.assertTrue(result["driving_alerts_enabled"])
        self.assertIn("PHONE", result["detections"])
        self.assertEqual(result["alert_level"], 3)

    def test_simulated_emergency_and_v2x_fanout(self):
        result = EmergencyService().trigger("EMERGENCY_DEMO", speed=0, heading=45)
        self.assertEqual(result["status"], "SIMULATED EMERGENCY NOTIFICATION")
        self.assertEqual(result["v2x"]["status"], "V2X ALERT SENT")
        self.assertEqual([item["vehicle_id"] for item in result["v2x"]["recipients"]],
                         ["CAR_B", "CAR_C", "CAR_D"])
        self.assertTrue(result["location"]["source"].startswith("SIMULATED"))

    def test_event_history_and_summary(self):
        event_logger.log_event("PHONE_DETECTED", 1, "Real camera detection")
        event_logger.log_event("DROWSINESS", 2, "Real camera detection")
        event_logger.log_event("EMERGENCY_DEMO", 3, "Simulated workflow")
        self.assertEqual(event_logger.get_summary(), {
            "total_events": 3, "warnings": 1, "high_risk": 1, "emergencies": 1,
        })
        self.assertEqual(event_logger.get_events()[0]["event_type"], "EMERGENCY_DEMO")
        self.assertEqual(event_logger.get_event_counts_by_type(), {
            "DROWSINESS": 1, "EMERGENCY_DEMO": 1, "PHONE_DETECTED": 1,
        })

    def test_mobile_dashboard_and_live_detection_counts(self):
        event_logger.log_event("PHONE_DETECTED", 1, "phone transition")
        event_logger.log_event("YAWNING", 1, "yawn transition")
        client = app.test_client()
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Recorded detection counts", page.data)
        self.assertIn(b"Recent safety events", page.data)
        status = client.get("/api/status").get_json()
        self.assertEqual(status["detection_counts"]["PHONE_DETECTED"], 1)
        history = client.get("/api/events").get_json()
        self.assertEqual(history["counts_by_type"]["YAWNING"], 1)

    def test_alarm_tone_patterns_differ_by_safety_level(self):
        from alert_manager import _tone_pcm
        warning = _tone_pcm(1)
        high_risk = _tone_pcm(2)
        emergency = _tone_pcm(3)
        self.assertGreater(len(warning), 0)
        self.assertGreater(len(high_risk), len(warning))
        self.assertGreater(len(emergency), len(high_risk))
        self.assertEqual(len({warning, high_risk, emergency}), 3)

    def test_api_status_events_emergency_and_v2x(self):
        client = app.test_client()
        self.assertEqual(client.get("/api/status").status_code, 200)
        self.assertEqual(client.get("/api/events").get_json()["summary"]["total_events"], 0)
        vehicle = client.get("/api/vehicle").get_json()
        self.assertEqual(vehicle["speed_source"], "SIMULATED GPS")
        self.assertFalse(vehicle["ai_monitoring"])
        self.assertFalse(vehicle["driving_alerts_enabled"])
        self.assertEqual(vehicle["accident_detection"], "NOT_INTEGRATED")
        status = client.get("/api/status").get_json()
        self.assertIn("vehicle_state", status)
        self.assertIn("driving_alerts_enabled", status)
        with patch("alert_manager.trigger_alert") as alarm:
            response = client.post("/api/emergency", json={"event_type": "EMERGENCY_DEMO"})
            alarm.assert_called_once()
        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.get_json()["v2x"]["message"]["simulation"])
        repeated = client.post("/api/emergency", json={"event_type": "EMERGENCY_DEMO"})
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(client.get("/api/events").get_json()["summary"]["emergencies"], 1)
        self.assertEqual(client.get("/api/v2x").get_json()["status"], "SENT")
        remote_client = app.test_client()
        response = remote_client.post("/api/emergency", json={"event_type": "EMERGENCY_DEMO"},
                                      environ_overrides={"REMOTE_ADDR": "192.168.1.25"})
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
