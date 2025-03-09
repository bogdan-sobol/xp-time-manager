from datetime import datetime
from random import randint
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QListWidgetItem

from ..utils.logger import setup_logger
from ..utils.constants import (
    MOB_XP_RATES,
    TIME_FORMAT,
    DEFAULT_HISTORY_ENTRIES_DISPLAYED,
)


class TimeTrackingModel:
    def __init__(self, database, user_model):
        self.db = database
        self.logger = setup_logger()
        self.user_model = user_model

        self.is_timer_running = False
        # Stores ID of currently tracked time entry
        # to insert duration after stopping time tracking
        self.current_entry_id = 0
        # Stores the start time of currenly tracked time entry
        self.start_time = None

        # Keeps track of currently selected item
        # and its delete button in the history list
        self.current_selected_item = None
        self.current_delete_btn = None

        self.user_has_activities = None

        self.total_history_entries_count = self.count_history_time_entries()

    # Timer Core Functions

    def start_time_tracking(self, activity_name: str) -> bool:
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

    def stop_time_tracking(self) -> None:
        if not self.is_timer_running:
            return False

        end_time = datetime.now().timestamp()
        duration_seconds = int(end_time - self.start_time)
        formatted_duration = self._format_duration(duration_seconds)

        formatted_start_time = datetime.fromtimestamp(self.start_time).strftime(
            TIME_FORMAT
        )
        formatted_end_time = datetime.fromtimestamp(end_time).strftime(TIME_FORMAT)

        self.db.stop_time_entry(
            self.current_entry_id,
            formatted_start_time,
            duration_seconds,
            formatted_duration,
            formatted_end_time,
        )

        earned_xp = self._calculate_earned_xp_for_time_session(duration_seconds)
        self.give_time_session_reward(earned_xp, self.current_entry_id)

        self.start_time = None
        self.current_entry_id = None
        self.is_timer_running = False
        self.total_history_entries_count += 1

    def get_formatted_elapsed_time_since_start(self) -> str:
        """
        Calculate elapsed time based on start time and current time
        Returns result as a string of the following format: "1:23:45"
        """
        if not self.is_timer_running:
            return "0:00:00"

        duration = datetime.now().timestamp() - self.start_time
        return self._format_duration(duration)

    # Data Management Functions

    def get_history_time_entries(
        self, entries_quantity: int = DEFAULT_HISTORY_ENTRIES_DISPLAYED
    ) -> list:
        """
        Retrieve certain number of history time entries from the database
        """
        self.logger.debug(
            f"Attempting to retrieve {entries_quantity} history time entries"
        )

        time_entries: list = self.db.get_history_time_entries(
            entries_quantity, self.user_model.current_user_id
        )

        if not time_entries:
            self.logger.info(
                f"No time entries found for user with ID: {self.user_model.current_user_id}"
            )
            return None

        self.logger.debug(
            f"{len(time_entries)} time entries were returned from the database"
        )
        return time_entries

    def get_user_activities(self):
        """
        Returns:
            List of tuples with activities if any
            None if no activities were found
        """
        activities = self.user_model.get_user_activities()

        if not activities:
            self.user_has_activities = False
            return None

        self.user_has_activities = True
        return activities

    def delete_time_entry(self, entry_id) -> None:
        """Delete a time entry from database"""
        self.db.delete_time_entry(entry_id, self.user_model.current_user_id)
        # Update total entries count
        self.total_history_entries_count -= 1

    def count_history_time_entries(self) -> int:
        """Count all the history time entries in the database"""
        user_id = self.user_model.current_user_id

        entries_count = self.db.count_user_history_entries(user_id)

        if entries_count:
            # Extract from tuple
            entries_count = entries_count[0]
        else:
            entries_count = 0

        self.logger.debug(
            f"Current user has {entries_count} history time entries stored in the database"
        )

        return entries_count

    # XP and Rewards Functions

    def give_time_session_reward(self, earned_xp: int, entry_id: int) -> None:
        """
        Calculate user's statistic based on earned XP
        Set new value in the 'users' table
        Add a new entry to the 'xp_transactions' table
        """
        self.logger.debug("Attempting to give user a time tracking reward")
        user_id = self.user_model.current_user_id
        user_total_xp = self.user_model.current_user_xp

        # Update user's XP
        new_xp_amount = user_total_xp + earned_xp
        self.user_model.set_user_xp(new_xp_amount)

        self.logger.debug(f"User's total XP before the reward: {user_total_xp}")
        self.logger.debug(f"User's total XP after the reward: {new_xp_amount}")

        # Add entry to xp_transactions table
        self.db.insert_into_xp_transactions(
            xp_amount=earned_xp,
            source_type="time_session",
            source_id=entry_id,
            user_id=user_id,
        )

        # Update user's level
        new_user_level = self.user_model.evaluate_level(new_xp_amount)

        self.logger.debug(
            f"User's level before the reward: {self.user_model.current_user_level}"
        )
        self.logger.debug(f"User's level after the reward: {new_user_level}")

        self.user_model.set_user_level(new_user_level, user_id)

    def _calculate_earned_xp_for_time_session(self, duration_seconds: int) -> int:
        self.logger.debug("Calculating earned XP for the time session")
        earned_xp = 0

        if duration_seconds <= 59:
            return earned_xp

        # Convert seconds to minutes
        minutes_spent = int(duration_seconds / 60)

        selected_mob = self._get_selected_mob()
        xp_rate = MOB_XP_RATES[selected_mob]

        # If XP rate is a range
        if isinstance(xp_rate, list):
            self.logger.debug(
                f"XP rate is randomly selected between {xp_rate[0]} and {xp_rate[1]}"
            )
            for _ in range(minutes_spent):
                earned_xp += randint(xp_rate[0], xp_rate[1])
        # If XP rate is static
        else:
            self.logger.debug(f"XP rate is: {xp_rate}")
            earned_xp = minutes_spent * xp_rate

        self.logger.info(f"XP reward for the time session: {earned_xp} XP")
        return earned_xp

    # UI Related Functions

    def show_delete_button(self, item: QListWidgetItem):
        """
        Show delete button of the selected item in the history list
        Hide previosly showed delete button if any
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

    # Helper Functions

    def _get_selected_mob(self) -> str:
        return self.user_model.current_selected_mob

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Converts exact seconds to formated hours, minutes and seconds"""
        if seconds <= 0:
            return "0:00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"
