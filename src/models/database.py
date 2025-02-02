# database.py - Handles all database operations
import sqlite3
from datetime import datetime
from ..utils.constants import DB_NAME, TIME_FORMAT
from ..utils.logger import setup_logger

class Database:
    def __init__(self):
        self.logger = setup_logger()
        self.create_tables()

    def initialize_default_user(self) -> int:
        """
        Creates default user if it doesn't exist
        Returns default user's ID
        Returns -1 in case of an error
        """
        query = """
            INSERT OR IGNORE INTO users
            (username, current_level, total_xp)
            VALUES ('default_user', 0, 0);"""
        
        id = "SELECT id FROM users WHERE username = ?"
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query)
                cur.execute(id, ("default_user",))
                return cur.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while initializing default user: {e}")
            return -1

    def create_tables(self) -> None:
        """Creates the necessary database tables if they don't exist"""
        time_entries = """
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration TEXT,
                duration_seconds INTEGER,
                end_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );"""
        
        users = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                current_level INTEGER DEFAULT 0,
                total_xp INTEGER DEFAULT 0
            );"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(time_entries)
                cur.execute(users)
        except sqlite3.Error as e:
            self.logger.error(f"Database error while creating tables: {e}")

    def add_entry(self, activity_name: str,
                    user_id: int = 1) -> int:
        """Creates a new entry and returns its ID"""
        query = """
            INSERT INTO time_entries
            (user_id, activity_name, start_time)
            VALUES (?, ?, ?);"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                start_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute(query, (user_id, activity_name, start_time))
                # Return entry ID
                return cur.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Database error while adding time entry: {e}")
            return -1

    def finish_entry(self, entry_id: int,
                    seconds_duration: int,
                    formatted_duration: str,
                    user_id: int = 1) -> None:
        """Adds end time and duration to current entry"""
        query = """
            UPDATE time_entries
            SET user_id = ?,
            duration = ?, duration_seconds = ?,
            end_time = ? WHERE id = ?;"""

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                end_time = datetime.now().strftime(TIME_FORMAT)
                cur.execute(query, (user_id, formatted_duration,
                    seconds_duration, end_time, entry_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while finishing time entry: {e}")
            return

    def get_recent_entries(self, user_id: int = 1,
                            limit: int = 10) -> list:
        """Gets most recent time entries
        And returns them as a list of tuples"""
        query = """
            SELECT * FROM time_entries
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?"""

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id, limit))
                return cur.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error while getting recent entries: {e}")
            return [] # Return empty list on error

    def get_total_duration(self, user_id: int = 1) -> int:
        """Return total tracked time in seconds"""
        query = """
            SELECT SUM(duration_seconds)
            FROM time_entries
            WHERE user_id = ?;"""

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id,))
                total = cur.fetchone()[0]
                return total if total else 0 # Handle empty database
        except sqlite3.Error as e:
            self.logger.error(f"Database error while getting total duration: {e}")
            return 0