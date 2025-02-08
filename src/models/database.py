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
        insert_default_user_query = """
            INSERT OR IGNORE INTO users
            (username, level, total_xp)
            VALUES ('default_user', 0, 0);"""
        
        select_user_id_query = "SELECT id FROM users WHERE username = ?"
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(insert_default_user_query)
                cur.execute(select_user_id_query, ("default_user",))
                return cur.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while initializing default user: {e}")
            return -1


    def select_and_fetchone(self, query: str, parameters: tuple):
        """
        Executes select query and returns its result
        Returs None if nothing were found or an error occured
        """
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(query, parameters)
                result = cur.fetchone()

                if result == None:
                    return None
                
                return result[0]
        except sqlite3.Error as e:
            self.logger.error(f"Database error while executing and fetching one result: {e}")
            return None


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


    def start_time_entry(self, activity_name: str,
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


    def stop_time_entry(self, entry_id: int,
                    seconds_duration: int,
                    formatted_duration: str) -> None:
        """Adds end time and duration to current entry"""
        query = """
            UPDATE time_entries
            SET duration = ?,
            duration_seconds = ?,
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


    def delete_time_entry(self, entry_id: int, user_id: int = 1) -> None:
        """
        Deletes time entry of a user
        In both time_entries and xp_transactions tables
        """
        delete_time_entry = """
            DELETE FROM time_entries
            WHERE user_id = ?
            AND id = ?"""
        delete_xp_transaction = """
            DELETE FROM xp_transactions
            WHERE user_id = ? 
            AND source_type = 'time_session'
            AND source_id = ?"""
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(delete_time_entry, (user_id, entry_id))
                cur.execute(delete_xp_transaction, (user_id, entry_id))
        except sqlite3.Error as e:
            self.logger.error(f"Database error while deleting time entry: {e}")
            return


    def get_recent_entries(self, user_id: int = 1,
                            limit: int = 10) -> list:
        """
        Gets most recent time entries
        Returns them in descending order 
        As a list of tuples
        """
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
        
        total_duration = self.select_and_fetchone(query, (user_id,))

        if total_duration == None:
            return 0
        
        return total_duration


    def get_user_level(self, user_id: int = 1) -> int:
        """
        Fetches user's level by user's ID
        Returns 0 if nothing found or an error occured
        """
        query = "SELECT level FROM users WHERE id = ?"

        user_level = self.select_and_fetchone(query, (user_id,))

        if user_level == None:
            self.logger.warning("get_user_level function in database.py returned None")
            return 0
        
        if not isinstance(user_level, int):
            self.logger.error("get_user_level function in database.py returned not an integer")
            return 0
        
        return user_level


    def get_user_xp(self, user_id: int = 1) -> float:
        """
        Fetches user's XP by user's ID
        Returns 0.0 if nothing found or an error occured
        """
        query = "SELECT total_xp FROM users WHERE id = ?"

        user_xp = self.select_and_fetchone(query, (user_id,))

        if user_xp == None:
            self.logger.warning("get_user_xp function in database.py returned None")
            return 0.0
        
        if not isinstance(user_xp, float):
            self.logger.error("get_user_xp function in database.py returned not a float")
            return 0.0
        
        return user_xp


    def set_user_level(self, level: int, user_id: int = 1) -> None:
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


    def get_total_xp(self, user_id: int = 1) -> float:
        """
        Summorazies all XP transactions of one user and returns it
        Returns 0.0 if the result is None
        """
        query = """
            SELECT SUM(xp_amount)
            FROM xp_transactions
            WHERE user_id = ?"""
        
        # The xp_amount rows are stored as float, so the sum is a float
        total_xp = self.select_and_fetchone(query, (user_id,))

        if total_xp == None:
            self.logger.warning("get_total_xp function in database.py returned None")
            return 0.0
        
        if not isinstance(total_xp, float):
            self.logger.warning("get_total_xp returned not a float, trying to convert it...")
            try:
                total_xp = float(total_xp)
                return total_xp
            except:
                self.logger.error("Failed to convert total XP from get_total_xp in database.py into a float")
                return 0.0
        
        return total_xp


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