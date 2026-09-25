"""Transition-triggered pygame alarm with a silent fallback."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ALARM_PATH = PROJECT_ROOT / "sounds" / "alert.wav"

_pygame = None
_alarm_available = False

try:
    import pygame as _pygame
    if ALARM_PATH.is_file():
        _pygame.mixer.init()
        _pygame.mixer.music.load(str(ALARM_PATH))
        _alarm_available = True
except Exception as exc:
    print("Alarm audio unavailable:", exc)


def play_alarm():
    if _alarm_available and not _pygame.mixer.music.get_busy():
        _pygame.mixer.music.play()


def trigger_alert(message, cooldown=1.0):
    # Called by the application only when an event becomes active.
    print(f"[ALERT] {message}")
    play_alarm()


def stop_alert():
    if _alarm_available:
        _pygame.mixer.music.stop()


def close_alert_system():
    stop_alert()
    if _pygame is not None:
        try:
            _pygame.mixer.quit()
        except Exception:
            pass
