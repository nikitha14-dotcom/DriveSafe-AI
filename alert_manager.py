"""Transition-triggered, risk-level audio alerts with a generated-tone fallback."""

from array import array
import math
import sys

_pygame = None
_audio_backend = None
_sounds = {}

try:
    import pygame as _pygame
    _pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    _pygame.mixer.set_num_channels(8)
    _audio_backend = "pygame"
except Exception as exc:
    print("Pygame audio unavailable; using the system alert sound when possible:", exc)
    _pygame = None
    if sys.platform == "win32":
        try:
            import winsound
            _audio_backend = "winsound"
        except Exception:
            pass


def _tone_pcm(level, sample_rate=22050):
    """Build a short, distinct beep pattern for warning/high/emergency levels."""
    patterns = {
        1: ((740, 0.13), (0, 0.09), (740, 0.13)),
        2: ((880, 0.16), (0, 0.07), (880, 0.16), (0, 0.07), (880, 0.16)),
        3: ((1046, 0.13), (0, 0.05), (1046, 0.13), (0, 0.05),
            (1046, 0.13), (0, 0.05), (1046, 0.13), (0, 0.05), (1046, 0.13)),
    }
    level = max(1, min(3, int(level)))
    samples = array("h")
    for frequency, seconds in patterns[level]:
        count = int(sample_rate * seconds)
        if frequency == 0:
            samples.extend([0] * count)
        else:
            amplitude = 7800
            samples.extend(int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                           for i in range(count))
    return samples.tobytes()


def play_alarm(level=1):
    level = max(1, min(3, int(level)))
    if _audio_backend == "pygame":
        try:
            sound = _sounds.get(level)
            if sound is None:
                sound = _pygame.mixer.Sound(buffer=_tone_pcm(level))
                _sounds[level] = sound
            channel = _pygame.mixer.Channel(0)
            channel.stop()
            channel.play(sound)
            return True
        except Exception as exc:
            print("Alarm playback failed:", exc)
    elif _audio_backend == "winsound":
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            return True
        except Exception as exc:
            print("System alert sound failed:", exc)
    else:
        print(f"[ALARM LEVEL {level}] No audio output device is available.")
    return False


def trigger_alert(message, cooldown=1.0, level=1):
    """Call once for each new detection transition or safety-level escalation."""
    level = max(1, min(3, int(level)))
    print(f"[SAFETY LEVEL {level}] {message}")
    return play_alarm(level)


def stop_alert():
    if _audio_backend == "pygame" and _pygame is not None:
        try:
            _pygame.mixer.Channel(0).stop()
        except Exception:
            pass


def close_alert_system():
    stop_alert()
    if _pygame is not None:
        try:
            _pygame.mixer.quit()
        except Exception:
            pass
