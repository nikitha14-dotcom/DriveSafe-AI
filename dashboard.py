"""Tkinter dashboard reading the real SQLite event history and local API."""

import json
import tkinter as tk
from tkinter import ttk
from urllib.request import urlopen

from event_logger import get_events, get_summary
import runtime_state


def _live_status():
    try:
        with urlopen("http://127.0.0.1:5000/api/status", timeout=0.35) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return runtime_state.snapshot()


def build_dashboard():
    root = tk.Tk()
    root.title("DriveSafe AI - Safety Monitoring Dashboard")
    root.geometry("1120x720")
    root.minsize(800, 560)
    root.configure(bg="#f3f6fa")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)

    tk.Label(root, text="DriveSafe AI", font=("Segoe UI", 24, "bold"),
             bg="#17202a", fg="white", pady=12).grid(row=0, column=0, sticky="ew")
    tk.Label(root, text="Driver safety prototype | camera AI is real; GPS/V2X/emergency are simulated",
             font=("Segoe UI", 10), bg="#17202a", fg="#d5d8dc", pady=4).grid(row=1, column=0, sticky="ew")

    stats = tk.Frame(root, bg="#f3f6fa", padx=12, pady=12)
    stats.grid(row=2, column=0, sticky="ew")
    for column in range(4):
        stats.columnconfigure(column, weight=1)
    stat_values = {}
    for column, (key, label) in enumerate((
        ("total_events", "TOTAL EVENTS"), ("warnings", "WARNINGS"),
        ("high_risk", "HIGH RISK"), ("emergencies", "EMERGENCIES")
    )):
        card = tk.Frame(stats, bg="white", bd=1, relief="solid", padx=8, pady=8)
        card.grid(row=0, column=column, sticky="ew", padx=5)
        tk.Label(card, text=label, bg="white", fg="#52616b", font=("Segoe UI", 9, "bold")).pack()
        stat_values[key] = tk.Label(card, text="0", bg="white", font=("Segoe UI", 21, "bold"))
        stat_values[key].pack()

    live = tk.Label(root, text="Waiting for camera/API status", anchor="w", justify="left",
                    bg="#e8f8f5", fg="#123", padx=14, pady=10, font=("Segoe UI", 10))
    live.grid(row=3, column=0, sticky="new", padx=18, pady=(0, 10))

    table_frame = tk.Frame(root, padx=18, pady=8)
    table_frame.grid(row=4, column=0, sticky="nsew")
    root.rowconfigure(4, weight=1)
    columns = ("id", "event", "level", "message", "timestamp")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    for key, label, width in (("id", "ID", 55), ("event", "EVENT", 190),
                              ("level", "SAFETY", 110), ("message", "MESSAGE", 470),
                              ("timestamp", "TIMESTAMP (UTC)", 190)):
        tree.heading(key, text=label)
        tree.column(key, width=width, anchor="w" if key == "message" else "center")
    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def refresh():
        summary = get_summary()
        for key, label in stat_values.items():
            label.configure(text=str(summary[key]))
        status = _live_status()
        if "detections" in status:
            detections = status.get("detections", {})
            gps = status.get("gps") or {}
            loc = (f"{gps.get('latitude', '—')}, {gps.get('longitude', '—')}"
                   if gps else "not available")
            lines = [f"Camera: {status.get('camera', 'UNKNOWN')}    Driver: {status.get('driver_status', 'UNKNOWN')}    "
                     f"Safety: {status.get('safety_level', '—')}    Mode: {status.get('mode', '—')}",
                     f"Phone {detections.get('phone', False)} | Drowsiness {detections.get('drowsiness', False)} | "
                     f"Yawning {detections.get('yawning', False)} | Distraction {detections.get('distraction', False)} | "
                     f"Accident detection: {status.get('accident_detection', 'NOT_INTEGRATED')}",
                     f"Speed: {status.get('speed', '—')} km/h ({status.get('speed_source', 'SIMULATED GPS')}) | "
                     f"Location: {loc} (SIMULATED)"]
            live.configure(text="\n".join(lines))
        else:
            live.configure(text=(f"Camera: {status.get('camera', 'UNKNOWN')}    "
                                 f"Driver: {status.get('driver_status', 'UNKNOWN')}    "
                                 f"Safety: {status.get('safety_level', '—')}    Mode: {status.get('mode', '—')}\n"
                                 f"Phone {status.get('detections', {}).get('phone', False)} | "
                                 f"Drowsiness {status.get('detections', {}).get('drowsiness', False)} | "
                                 f"Yawning {status.get('detections', {}).get('yawning', False)} | "
                                 f"Distraction {status.get('detections', {}).get('distraction', False)} | "
                                 f"Accident detection: {status.get('accident_detection', 'NOT_INTEGRATED')}"))
        for item in tree.get_children():
            tree.delete(item)
        for event in get_events(limit=200):
            level = {0: "NORMAL", 1: "WARNING", 2: "HIGH RISK", 3: "EMERGENCY"}.get(event["safety_level"], "UNKNOWN")
            tree.insert("", "end", values=(event["id"], event["event_type"], level,
                                             event["message"], event["timestamp"]))
        root.after(2500, refresh)

    refresh()
    root.mainloop()


if __name__ == "__main__":
    build_dashboard()
