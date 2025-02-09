# activity_timer_model.py

from datetime import datetime
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QListWidgetItem
from ..utils.logger import setup_logger
from ..utils.constants import SECONDS_UNTIL_REWARD, XP_REWARD

class ActivityTimerModel:
    def __init__(self, database, user_model):
        self.db = database
        self.user_model = user_model

        self.is_timer_running = False
        self.current_entry_id = 0
        self.start_time = None

        # Keeps track of currently selected item and its delete button
        self.current_selected_item = None
        self.current_delete_btn = None

        self.logger = setup_logger()


    def start_timer(self, activity_name: str) -> bool:
        if self.is_timer_running:
            return False

        user_id = self.user_model.current_user_id
        self.start_time = datetime.now().timestamp()
        self.current_entry_id = self.db.start_time_entry(activity_name, user_id)

        if self.current_entry_id == -1:
            self.logger.error("Error in timer_model: returned user's ID is -1")
            return False
        
        self.is_timer_running = True
        return True


    def stop_timer(self) -> None:
        if not self.is_timer_running:
            return
        
        end_time = datetime.now().timestamp()
        duration_seconds = int(end_time - self.start_time)
        formatted_duration = self._format_duration(duration_seconds)

        self.db.stop_time_entry(
            self.current_entry_id,
            duration_seconds,
            formatted_duration
        )

        xp_earned = self.calculate_earned_xp(duration_seconds)
        self.give_time_session_reward(xp_earned, self.current_entry_id)

        self.start_time = None
        self.current_entry_id = None
        self.is_timer_running = False


    def get_current_duration(self) -> str:
        if not self.is_timer_running:
            return "0:00:00"
        
        current_duration = datetime.now().timestamp() - self.start_time
        return self._format_duration(current_duration)


    def get_recent_entries(self, limit: int = 10) -> list:
        return self.db.get_recent_entries(self.user_model.current_user_id, limit)


    def give_time_session_reward(self, earned_xp: int, entry_id: int) -> None:
        """
        Calculates user's statistic based on earned XP
        Sets new value in the users and xp_transactions tables
        """
        user_id = self.user_model.current_user_id
        user_total_xp = self.user_model.current_user_xp
        self.logger.debug(f"XP amount before reward: {user_total_xp}")

        # Updates user's XP
        new_xp_amount = user_total_xp + earned_xp
        self.logger.debug(f"New XP amount: {new_xp_amount}")
        self.user_model.set_user_xp(new_xp_amount)

        # Adds entry to xp_transactions table
        self.db.insert_into_xp_transactions(
            xp_amount=earned_xp,
            source_type="time_session",
            source_id=entry_id,
            user_id=user_id)

        # Updates user's level
        self.logger.debug(f"User level before reward: {self.user_model.current_user_level}")
        new_user_level = self.user_model.evaluate_level(new_xp_amount)
        self.user_model.set_user_level(new_user_level, user_id)
        self.logger.debug(f"New user level: {new_user_level}")


    def show_delete_button(self, item: QListWidgetItem):
        """
        Hides previosly showed delete button if any
        Shows delete button of the selected item in the list
        """
        # Hide delete button of previously selected item
        if self.current_selected_item and self.current_delete_button:
            self.current_delete_button.hide()

        # Get the delete button associated with clicked item
        delete_button = item.data(Qt.ItemDataRole.UserRole)
        
        # Show delete button of newly selected item
        if delete_button:
            delete_button.show()
            self.current_selected_item = item
            self.current_delete_button = delete_button


    def delete_time_entry(self, entry_id) -> None:
        # Deletes entry from database
        self.db.delete_time_entry(entry_id, self.user_model.current_user_id)


    def calculate_earned_xp(self, duration_seconds: int) -> float:
        """Calculates earned XP for a time session and returns it"""
        if duration_seconds <= 0:
            return 0
        
        self.logger.info(f"Evaluating XP to give...")
        self.logger.debug(f"XP reward is {XP_REWARD} per {SECONDS_UNTIL_REWARD} seconds")

        earned_xp = (duration_seconds / SECONDS_UNTIL_REWARD) * XP_REWARD

        # Round to 1 decimal place
        earned_xp = "{:.1f}".format(earned_xp)
        self.logger.info(f"XP reward is: {earned_xp} XP")

        return float(earned_xp)


    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Converts exact seconds to formated hours, minutes and seconds"""
        if seconds <= 0:
            return "0:00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    