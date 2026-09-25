"""SQLite event storage shared by the camera app, API and dashboard."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get(
    "DRIVESAFE_DB_PATH", PROJECT_ROOT / "database" / "drivesafe_events.db"
))


@contextmanager
def _connect():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE), timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with _connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS safety_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                safety_level INTEGER NOT NULL,
                message TEXT,
                timestamp TEXT NOT NULL
            )
        """)
    return str(DATABASE)


def log_event(event_type, safety_level, message=""):
    """Record one event transition; callers should only call on state changes."""
    initialize_database()
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO safety_events(event_type, safety_level, message, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (str(event_type), int(safety_level), str(message), timestamp),
        )
        event_id = cursor.lastrowid
    return {"id": event_id, "event_type": str(event_type),
            "safety_level": int(safety_level), "message": str(message),
            "timestamp": timestamp}


def get_events(limit=100):
    initialize_database()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id, event_type, safety_level, message, timestamp "
            "FROM safety_events ORDER BY id DESC LIMIT ?", (int(limit),)
        ).fetchall()
    return [dict(row) for row in rows]


def get_summary():
    initialize_database()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT safety_level, COUNT(*) AS count FROM safety_events GROUP BY safety_level"
        ).fetchall()
        total = connection.execute("SELECT COUNT(*) FROM safety_events").fetchone()[0]
    counts = {int(row["safety_level"]): int(row["count"]) for row in rows}
    return {"total_events": int(total), "warnings": counts.get(1, 0),
            "high_risk": counts.get(2, 0), "emergencies": counts.get(3, 0)}


def show_events():
    events = get_events(limit=1000)
    if not events:
        print("No events recorded.")
        return
    for event in events:
        print("{id} | {event_type} | Level {safety_level} | {message} | {timestamp}".format(**event))


if __name__ == "__main__":
    print("Database initialized:", initialize_database())
    show_events()


def get_event_counts_by_type():
    """Return persistent detection totals by type, counting event transitions."""
    initialize_database()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT event_type, COUNT(*) AS count FROM safety_events "
            "GROUP BY event_type ORDER BY event_type"
        ).fetchall()
    return {str(row["event_type"]): int(row["count"]) for row in rows}
