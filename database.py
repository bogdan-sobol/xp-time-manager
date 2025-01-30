# database.py - Handles all database operations
import sqlite3
from datetime import datetime
from constants import DB_NAME, TIME_FORMAT
from logger import setup_logger

class Database:
    def __init__(self):
        self.logger = setup_logger()
        self.create_tables()


    def create_tables(self):
        """Creates the necessary database tables if they don't exist"""
        query = """
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration TEXT,
                duration_seconds INTEGER,
                end_time TEXT
            );"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query)
        except sqlite3.Error as e:
            self.logger.error(f"Database error while creating tables: {e}")

    
    def add_entry(self, activity_name: str) -> int:
        """Creates a new entry and returns its ID"""
        query = """
            INSERT INTO time_entries
            (activity_name, start_time)
            VALUES (?, ?);"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                start_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute(query, (activity_name, start_time))
                # Return current entry ID
                return cur.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error while adding time entry: {e}")
            return -1


    def finish_entry(self, entry_id: int,
                    seconds_duration: int,
                    formatted_duration: str) -> None:
        """Adds end time and duration to current entry"""
        query = """
            UPDATE time_entries
            SET duration = ?, duration_seconds = ?,
            end_time = ? WHERE id = ?;"""

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                end_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute(query, (formatted_duration,
                    seconds_duration, end_time, entry_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while finishing time entry: {e}")
            return

    
    def get_recent_entries(self, limit: int = 10) -> tuple:
        """Gets most recent time entries"""
        query = """
            SELECT * FROM time_entries
            ORDER BY id DESC
            LIMIT ?"""

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (limit,))
                return cur.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error while getting recent entries: {e}")
            return () # Return empty tuple on error
        
    
    def get_total_duration(self) -> int:
        """Return total tracked time in seconds"""
        query = "SELECT SUM(duration_seconds) FROM time_entries;"

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query)
                total = cur.fetchone()[0]
                return total if total else 0 # Handle empty database
        except sqlite3.Error as e:
            self.logger.error(f"Database error while getting total duration: {e}")
            return 0