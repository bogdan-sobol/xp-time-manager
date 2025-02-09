# activity_timer_controller.py

from PyQt6.QtCore import *
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QListWidgetItem
from ..utils.constants import MAX_ACTIVITY_NAME_SIZE

class ActivityTimerController:
    def __init__(self, main_window, timer_model):
        self.main_window = main_window
        self.timer_model = timer_model
        self.update_timer = None


    def handle_start_stop_button_clicked(self, activity_name: str) -> bool:
        """
        Handles start/stop button in timer view
        Returns False if something went wrong
        """
        # If timer is not running - start timer
        if not self.timer_model.is_timer_running:
            # Validate activity name
            activity_name = activity_name.strip()
            if not activity_name:
                self.main_window.show_error("Please enter an activity name!")
                return False
                
            if len(activity_name) > MAX_ACTIVITY_NAME_SIZE:
                self.main_window.show_error("Activity name is too long.")
                return False

            # Start timer
            if self.timer_model.start_timer(activity_name):
                self._start_update_timer()
                self.main_window.timer_view.set_timer_running_state(True)
                return True
            else:
                self.main_window.show_error("Could not create time entry")
                return False
        else:
            # Stops timer
            self.timer_model.stop_timer()
            # Stops timer display in view
            self._stop_update_timer()
            self.main_window.timer_view.set_timer_running_state(False)
            # Updates history to show newly added entry
            self.main_window.timer_view.update_history()
            # Requests information update on dashboard to display updated statistic
            self.main_window.dashboard_view.dashboard_controller.update_user_stats()
            return True


    def _start_update_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)


    def _stop_update_timer(self):
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer.deleteLater()
            self.update_timer = None
            # Makes sure timer is back to 0:00:00
            self._update_display()


    def _update_elapsed_time_display(self):
        current_duration = self.timer_model.get_current_duration()
        self.main_window.timer_view.update_timer_display(current_duration)


    def get_recent_entries(self):
        return self.timer_model.get_recent_entries()


    def handle_item_selection(self, item: QListWidgetItem) -> None:
        """Handles when user clicks on a time entry"""
        self.timer_model.show_delete_button(item)


    def delete_time_entry(self, entry_id: int, entry_widget: QWidget) -> None:
        # Deletes entry from database
        self.timer_model.delete_time_entry(entry_id)
        # Deletes entry widget
        entry_widget.deleteLater()
        # Updates user statistic
        self.timer_model.user_model.reevaluate_user_stats()
        # Updates dashboard view
        self.main_window.dashboard_controller.update_user_stats()
        # Updates selected entry variables
        self.timer_model.current_selected_item = None
        self.timer_model.current_delete_btn = None
        # Updates entry list to remove blank space
        self.main_window.timer_view.update_history()