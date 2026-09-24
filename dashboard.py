import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# ============================================================
# DriveSafe AI - Safety Monitoring Dashboard
# ============================================================

DATABASE = "database/drivesafe_events.db"


# ============================================================
# DATABASE
# ============================================================

def get_events():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, event_type, safety_level, message, timestamp
        FROM safety_events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()

    connection.close()

    return events


# ============================================================
# COLORS / STATUS
# ============================================================

def level_text(level):

    if level == 0:
        return "NORMAL"

    if level == 1:
        return "WARNING"

    if level == 2:
        return "HIGH RISK"

    if level == 3:
        return "EMERGENCY"

    return "UNKNOWN"


# ============================================================
# DASHBOARD
# ============================================================

root = tk.Tk()

root.title("DriveSafe AI - Safety Monitoring Dashboard")

root.geometry("1100x650")

root.minsize(900, 550)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    root,
    bg="#17202A",
    height=80
)

header.pack(
    fill="x"
)

title = tk.Label(
    header,
    text="DriveSafe AI",
    font=("Arial", 26, "bold"),
    fg="white",
    bg="#17202A"
)

title.pack(
    pady=(12, 0)
)

subtitle = tk.Label(
    header,
    text="Intelligent Driver Safety Monitoring System",
    font=("Arial", 12),
    fg="#D5D8DC",
    bg="#17202A"
)

subtitle.pack()


# ============================================================
# STATUS
# ============================================================

status_frame = tk.Frame(
    root,
    bg="#F4F6F7"
)

status_frame.pack(
    fill="x",
    padx=20,
    pady=15
)


# ============================================================
# STATISTICS
# ============================================================

events = get_events()

total_events = len(events)

warning_count = sum(
    1 for e in events if e[2] == 1
)

high_risk_count = sum(
    1 for e in events if e[2] == 2
)

emergency_count = sum(
    1 for e in events if e[2] == 3
)


def create_stat(parent, title_text, value):

    frame = tk.Frame(
        parent,
        bg="white",
        bd=1,
        relief="solid",
        width=220,
        height=90
    )

    frame.pack(
        side="left",
        padx=8,
        expand=True,
        fill="both"
    )

    frame.pack_propagate(False)

    label = tk.Label(
        frame,
        text=title_text,
        font=("Arial", 11, "bold"),
        bg="white"
    )

    label.pack(
        pady=(12, 2)
    )

    value_label = tk.Label(
        frame,
        text=str(value),
        font=("Arial", 22, "bold"),
        bg="white"
    )

    value_label.pack()


create_stat(
    status_frame,
    "TOTAL EVENTS",
    total_events
)

create_stat(
    status_frame,
    "WARNINGS",
    warning_count
)

create_stat(
    status_frame,
    "HIGH RISK",
    high_risk_count
)

create_stat(
    status_frame,
    "EMERGENCIES",
    emergency_count
)


# ============================================================
# CURRENT STATUS
# ============================================================

current_frame = tk.Frame(
    root,
    bg="#E8F8F5",
    bd=1,
    relief="solid"
)

current_frame.pack(
    fill="x",
    padx=30,
    pady=5
)

current_label = tk.Label(
    current_frame,
    text="SYSTEM STATUS: MONITORING",
    font=("Arial", 15, "bold"),
    fg="#117A65",
    bg="#E8F8F5"
)

current_label.pack(
    pady=10
)


# ============================================================
# EVENT TABLE
# ============================================================

table_frame = tk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=15
)


columns = (
    "ID",
    "Event",
    "Safety Level",
    "Message",
    "Timestamp"
)


tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


tree.heading(
    "ID",
    text="ID"
)

tree.heading(
    "Event",
    text="EVENT"
)

tree.heading(
    "Safety Level",
    text="SAFETY LEVEL"
)

tree.heading(
    "Message",
    text="MESSAGE"
)

tree.heading(
    "Timestamp",
    text="TIMESTAMP"
)


tree.column(
    "ID",
    width=50,
    anchor="center"
)

tree.column(
    "Event",
    width=180,
    anchor="center"
)

tree.column(
    "Safety Level",
    width=120,
    anchor="center"
)

tree.column(
    "Message",
    width=350
)

tree.column(
    "Timestamp",
    width=170,
    anchor="center"
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)


tree.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# ============================================================
# INSERT EVENTS
# ============================================================

for event in events:

    event_id = event[0]
    event_type = event[1]
    safety_level = event[2]
    message = event[3]
    timestamp = event[4]

    tree.insert(
        "",
        "end",
        values=(
            event_id,
            event_type,
            level_text(safety_level),
            message,
            timestamp
        )
    )


# ============================================================
# FOOTER
# ============================================================

footer = tk.Label(
    root,
    text="DriveSafe AI | Real-time Driver Safety Monitoring Prototype",
    font=("Arial", 9),
    fg="#566573"
)

footer.pack(
    pady=8
)


# ============================================================
# START DASHBOARD
# ============================================================

root.mainloop()