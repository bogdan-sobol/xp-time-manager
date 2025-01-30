# database.py - Handles all database operations
import sqlite3
from datetime import datetime
from constants import DB_NAME, TIME_FORMAT

class Database:
    def __init__(self):
        self.create_tables()


    def create_tables(self):
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    duration TEXT,
                    duration_seconds INTEGER,
                    end_time TEXT
                );""")

    
    def add_entry(self, activity_name: str) -> int:
        """Creates a new entry and returns its ID"""
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                start_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute("""
                    INSERT INTO time_entries (activity_name, start_time)
                    VALUES (?, ?);""", (activity_name, start_time))
                # Return current entry ID
                return cur.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return -1

    def finish_entry(self, entry_id: int,
                    seconds_duration: int,
                    formatted_duration: str) -> None:
        """Adds end time and duration to current entry"""
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                end_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute("""
                    UPDATE time_entries
                    SET duration = ?, duration_seconds = ?,
                    end_time = ? WHERE id = ?;""",
                    (formatted_duration, seconds_duration, end_time, entry_id))
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return

    
    def get_recent_entries(self, limit: int = 10) -> tuple:
        """Gets most recent time entries"""
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM time_entries
                    ORDER BY id DESC
                    LIMIT ?""", (limit,))
                return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return () # Return empty tuple on error
        
    
    def get_total_duration(self) -> int:
        """Return total tracked time in seconds"""
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(duration_seconds) FROM time_entries;")
            total = cur.fetchone()[0]
            return total if total else 0 # Handle empty database