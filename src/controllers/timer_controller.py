# timer_controller.py
# coordinates between main_window.py and timer_model.py
# and handles user actions

from PyQt6.QtCore import QTimer
from ..models.timer_model import TimerModel
from ..utils.constants import MAX_ACTIVITY_NAME_SIZE

class TimerController:
    def __init__(self, view):
        self.view = view
        self.model = TimerModel()
        self.update_timer = None

    def start_stop_timer(self, activity_name: str) -> bool:
        if not self.model.is_timer_running:
            # Validate activity name
            if not activity_name.strip():
                self.view.show_error("Please enter an activity name!")
                return False
                
            if len(activity_name) > MAX_ACTIVITY_NAME_SIZE:
                self.view.show_error("Activity name is too long.")
                return False

            # Start the timer
            if self.model.start_timer(activity_name):
                self._start_update_timer()
                self.view.set_timer_running_state(True)
                return True
            else:
                self.view.show_error("Could not create time entry")
                return False
        else:
            # Stop the timer
            self.model.stop_timer()
            self._stop_update_timer()
            self.view.set_timer_running_state(False)
            self.view.update_history()
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

    def _update_display(self):
        current_duration = self.model.get_current_duration()
        self.view.update_timer_display(current_duration)

    def get_recent_entries(self):
        return self.model.get_recent_entries()