import pygame
import time

ALARM_PATH = "sounds/alert.wav"

pygame.mixer.init()

try:
    pygame.mixer.music.load(ALARM_PATH)
    alarm_available = True
    print("Alarm loaded successfully.")
except Exception as e:
    print("Alarm loading error:", e)
    alarm_available = False


last_alert_time = 0


def trigger_alert(message, cooldown=1.0):

    global last_alert_time

    current_time = time.time()

    if current_time - last_alert_time < cooldown:
        return

    print(f"[ALERT] {message}")

    if alarm_available:
        pygame.mixer.music.play()

    last_alert_time = current_time


def stop_alert():

    if alarm_available:
        pygame.mixer.music.stop()


def close_alert_system():

    stop_alert()
    pygame.quit()