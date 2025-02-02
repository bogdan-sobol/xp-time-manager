# timer_model.py
# handles all business logic like timer calculations,
# XP tracking, and database operations

from datetime import datetime
from ..utils.logger import setup_logger
from ..utils.constants import SECONDS_UNTIL_REWARD, XP_REWARD
from ..models.database import Database

class TimerModel:
    def __init__(self):
        self.is_timer_running = False
        self.current_entry_id = 0
        self.start_time = None

        self.db = Database()
        self.logger = setup_logger()
        self.current_user_id = self.db.initialize_default_user()
        self.logger.info(f"Current user ID: {self.current_user_id}")

    def start_timer(self, activity_name: str) -> bool:
        if self.is_timer_running:
            return False

        self.start_time = datetime.now().timestamp()
        self.current_entry_id = self.db.add_entry(activity_name, self.current_user_id)

        if self.current_entry_id != -1:
            self.is_timer_running = True
            return True
        self.logger.error("Error in timer_model: returned user's ID is -1")
        return False

    def stop_timer(self) -> None:
        if not self.is_timer_running:
            return
        
        end_time = datetime.now().timestamp()
        duration_seconds = int(end_time - self.start_time)
        formatted_duration = self._format_duration(duration_seconds)

        self.db.finish_entry(
            self.current_entry_id,
            duration_seconds,
            formatted_duration,
            self.current_user_id
        )

        self.start_time = None
        self.current_entry_id = None
        self.is_timer_running = False

    def get_current_duration(self) -> str:
        if not self.is_timer_running:
            return "0:00:00"
        
        current_duration = datetime.now().timestamp() - self.start_time
        return self._format_duration(current_duration)

    def get_recent_entries(self, limit: int = 10) -> list:
        return self.db.get_recent_entries(self.current_user_id, limit)

    def calculate_xp(self, duration_seconds: int) -> int:
        """Calculates XP based on duration and returns it"""
        if duration_seconds <= 0:
            return 0
        
        earned_xp = int((duration_seconds / SECONDS_UNTIL_REWARD) * XP_REWARD)
        return earned_xp

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Converts exact seconds to formated hours, minutes and seconds"""
        if seconds <= 0:
            return "0:00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"