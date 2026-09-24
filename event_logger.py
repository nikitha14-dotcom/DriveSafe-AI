import sqlite3
from datetime import datetime

# ============================================================
# DriveSafe AI - Event Logger
# ============================================================

DATABASE = "database/drivesafe_events.db"


# ============================================================
# CREATE DATABASE
# ============================================================

def initialize_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            safety_level INTEGER NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# LOG EVENT
# ============================================================

def log_event(event_type, safety_level, message):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO safety_events
        (event_type, safety_level, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        event_type,
        safety_level,
        message,
        timestamp
    ))

    connection.commit()
    connection.close()

    print(
        f"[LOGGED] {event_type} | "
        f"Level {safety_level} | "
        f"{timestamp}"
    )


# ============================================================
# DISPLAY EVENTS
# ============================================================

def show_events():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            event_type,
            safety_level,
            message,
            timestamp
        FROM safety_events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()

    connection.close()

    print("\n==============================================")
    print("DriveSafe AI - Safety Event History")
    print("==============================================")

    if not events:

        print("No events recorded.")

    else:

        for event in events:

            print(
                f"ID: {event[0]} | "
                f"Event: {event[1]} | "
                f"Level: {event[2]} | "
                f"{event[3]} | "
                f"{event[4]}"
            )

    print("==============================================")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("==============================================")
    print("DriveSafe AI - Event Logger")
    print("==============================================")

    initialize_database()

    print("Database initialized successfully.")

    log_event(
        "PHONE_DETECTED",
        1,
        "Driver phone usage detected"
    )

    log_event(
        "DROWSINESS",
        2,
        "Driver drowsiness detected"
    )

    log_event(
        "SEATBELT_MISSING",
        1,
        "Driver seat belt was not detected"
    )

    log_event(
        "ACCIDENT",
        3,
        "Emergency accident event detected"
    )

    show_events()

    print("\nEvent logging test completed successfully.")