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
            (username, level, total_xp)
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
                level INTEGER DEFAULT 0,
                total_xp REAL DEFAULT 0.0
            );"""
        
        xp = """
            CREATE TABLE IF NOT EXISTS xp_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                xp_amount REAL NOT NULL,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(time_entries)
                cur.execute(users)
                cur.execute(xp)
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


    def delete_time_entry(self, entry_id: int, user_id: int = 1) -> None:
        """
        Deletes time entry of a user
        In both time_entries and xp_transactions tables
        """
        delete_time_entry = """
            DELETE FROM time_entries
            WHERE user_id = ?
            AND id = ?"""
        delete_xp_transation = """
            DELETE FROM xp_transactions
            WHERE user_id = ? 
            AND source_type = 'time_session'
            AND source_id = ?"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(delete_time_entry, (user_id, entry_id))
                cur.execute(delete_xp_transation, (user_id, entry_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while deleting time entry: {e}")
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


    def get_user_level(self, user_id: int = 1) -> int:
        """Fetches user's level by user's ID
        Returns -1 if error occured"""
        query = "SELECT level FROM users WHERE id = ?"

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id,))
                return cur.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while retrieving user's level: {e}")
            return -1


    def get_user_xp(self, user_id: int = 1) -> int:
        """Fetches user's XP by user's ID
        Returns -1 if error occured"""
        query = "SELECT total_xp FROM users WHERE id = ?"

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id,))
                return cur.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while retrieving user's XP: {e}")
            return -1


    def set_user_lvl(self, level: int, user_id: int = 1) -> None:
        query = "UPDATE users SET level = ? WHERE id = ?;"

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (level, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while retrieving user's XP: {e}")


    def set_user_xp(self, xp: int, user_id: int = 1) -> None:
        query = "UPDATE users SET total_xp = ? WHERE id = ?;"

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (xp, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while updating user's XP: {e}")


    def get_total_xp(self, user_id: int = 1):
        query = """
            SELECT SUM(xp_amount)
            FROM xp_transactions
            WHERE user_id = ?"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, (user_id,))
                xp = cur.fetchone()
                if not xp:
                    return 0
                return xp[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while getting total XP earned: {e}")


    def insert_into_xp_transactions(self,
                                xp_amount: float,
                                source_type: str,
                                source_id: int,
                                user_id: int = 1):
        query = """
            INSERT INTO xp_transactions (
            user_id, xp_amount, source_type, source_id)
            VALUES(?, ?, ?, ?);"""
        values = (user_id, xp_amount, source_type, source_id)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, values)
        except sqlite3.Error as e:
            self.logger.error(f"Database error while inserting into xp_transactions table: {e}")