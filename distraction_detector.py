"""Sustained head-direction detection from MediaPipe face landmarks."""

from collections import deque
from statistics import median


class DistractionDetector:
    """Calibrates a short neutral baseline, then flags sustained head turns."""

    def __init__(self, duration=1.7, calibration_samples=24):
        self.duration = duration
        self.calibration_samples = calibration_samples
        self._yaw_samples = deque(maxlen=calibration_samples)
        self._pitch_samples = deque(maxlen=calibration_samples)
        self._neutral_yaw = None
        self._neutral_pitch = None
        self._candidate = None
        self._candidate_since = None
        self.direction = None

    @staticmethod
    def _measure(landmarks):
        # Indices are MediaPipe Face Mesh cheek, eye, nose and chin points.
        left_cheek, right_cheek = landmarks[234], landmarks[454]
        nose = landmarks[1]
        left_eye, right_eye = landmarks[159], landmarks[386]
        chin = landmarks[152]
        face_width = max(abs(right_cheek.x - left_cheek.x), 1e-6)
        eye_y = (left_eye.y + right_eye.y) / 2.0
        face_height = max(abs(chin.y - eye_y), 1e-6)
        yaw = (nose.x - (left_cheek.x + right_cheek.x) / 2.0) / face_width
        pitch = (nose.y - eye_y) / face_height
        return yaw, pitch

    def update(self, landmarks, now):
        """Return (active, direction, calibration_complete)."""
        if not landmarks:
            self.reset()
            return False, None, False

        yaw, pitch = self._measure(landmarks)
        if self._neutral_yaw is None:
            self._yaw_samples.append(yaw)
            self._pitch_samples.append(pitch)
            if len(self._yaw_samples) >= self.calibration_samples:
                self._neutral_yaw = median(self._yaw_samples)
                self._neutral_pitch = median(self._pitch_samples)
            return False, None, self._neutral_yaw is not None

        yaw_delta = yaw - self._neutral_yaw
        pitch_delta = pitch - self._neutral_pitch
        if yaw_delta <= -0.085:
            candidate = "LEFT"
        elif yaw_delta >= 0.085:
            candidate = "RIGHT"
        elif pitch_delta >= 0.075:
            candidate = "DOWN"
        else:
            candidate = None

        if candidate is None:
            self._candidate = None
            self._candidate_since = None
            self.direction = None
            return False, None, True

        if candidate != self._candidate:
            self._candidate = candidate
            self._candidate_since = now
            self.direction = None

        if now - self._candidate_since >= self.duration:
            self.direction = candidate
        return self.direction is not None, self.direction, True

    def reset(self):
        self._yaw_samples.clear()
        self._pitch_samples.clear()
        self._neutral_yaw = None
        self._neutral_pitch = None
        self._candidate = None
        self._candidate_since = None
        self.direction = None
