from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QListWidgetItem, QPushButton


class ActivityTimerController:
    """
    Controls the interaction between the UI and the activity timer model

    This controller manages the timer functionality, including starting/stopping activities,
    updating the display, and handling time entry operations in the UI

    Attributes:
        app_window: The main application window containing all views
        activity_timer_model: The model handling timer logic and data persistence
    """

    # Initialize

    def __init__(self, app_window, activity_timer_model):
        self.app_window = app_window
        self.activity_timer_model = activity_timer_model
        self.display_update_timer = None

    # Public interface methods

    def get_recent_entries(self, entries_quantity: int = 11) -> list:
        """
        Retrieve the list of recent time entries

        Returns:
            list: Recent time entries from the timer model
        """
        return self.activity_timer_model.get_recent_entries(entries_quantity)

    def delete_time_entry(self, entry_id: int, entry_widget: QWidget) -> None:
        """
        Delete a time entry and update all relevant views.

        Args:
            entry_id: ID of the time entry to delete
            entry_widget: Widget representing the entry in the UI

        Side Effects:
            - Removes entry from database
            - Updates UI
            - Refreshes statistics
        """
        # Delete from database and UI
        self.activity_timer_model.delete_time_entry(entry_id)
        entry_widget.deleteLater()

        # Update statistics and views
        self.activity_timer_model.user_model.reevaluate_user_stats()
        self.app_window.user_stats_controller.refresh_user_statistics()

        # Reset selection state
        self.activity_timer_model.current_selected_item = None
        self.activity_timer_model.current_delete_btn = None

        # Refresh entry list
        self.app_window.activity_timer_panel.refresh_activity_history()

    def get_activities(self):
        return self.activity_timer_model.get_user_activities()

    def refresh_activity_selector(self):
        activity_timer_panel = self.app_window.activity_timer_panel
        is_timer_running = self.activity_timer_model.is_timer_running

        # Save current selected item index if timer is running
        if is_timer_running:
            selected_activity_index = (
                activity_timer_panel.activity_selector.currentIndex()
            )

        activity_timer_panel.refresh_activity_selector()

        # Enable selector if timer is not runnig
        if not is_timer_running:
            activity_timer_panel.activity_selector.setDisabled(False)

        # Restore previosly selected item if time is running
        if is_timer_running:
            activity_timer_panel.activity_selector.setCurrentIndex(
                selected_activity_index + 1
            )

    def is_show_more_entries_button_needed(self, current_entries_count: int) -> bool:
        total_entries_count = self.activity_timer_model.total_history_entry_count

        if current_entries_count > 10:
            if current_entries_count < total_entries_count:
                return True

        return False

    # Event handlers

    def handle_start_stop_button_clicked(self, activity_name: str) -> bool:
        """
        Handle the start/stop button click event in the timer view.

        If the timer is not running, starts a new activity timer.
        If the timer is running, stops the current activity timer.

        Returns:
            bool: True if operation was successful, False otherwise

        Side Effects:
            - Updates UI state
            - Creates/stops timer
            - Updates history view
            - Updates dashboard statistics
        """
        if not self.activity_timer_model.is_timer_running:
            return self._start_new_activity(activity_name)
        else:
            return self._stop_current_activity()

    def handle_time_entry_selection(self, item: QListWidgetItem) -> None:
        """
        Handle when user selects a time entry in the list

        Args:
            item: The selected list widget item
        """
        item_data = item.data(Qt.ItemDataRole.UserRole)

        # If item data is empty
        if not item_data:
            return

        if item_data == "show_more_entries":
            activity_timer_panel = self.app_window.activity_timer_panel

            activities_count = activity_timer_panel.activity_history_list.count()

            # "Show more" item excluded
            activity_timer_panel.refresh_activity_history(activities_count + 9)
        else:
            self.activity_timer_model.show_delete_button(item)

    # Private helper methods (with _prefix)

    def _start_new_activity(self, activity_name: str) -> bool:
        """
        Start timing a new activity

        Returns:
            bool: True if activity was started successfully, False otherwise
        """
        # Check if user has activities
        if not self.activity_timer_model.user_has_activities:
            self.app_window.display_error_message(
                "Please add at least one activity first"
            )
            return False

        # Attempt to start the timer
        if self.activity_timer_model.start_timer(activity_name):
            self._start_display_updates()
            self.app_window.activity_timer_panel.update_timer_state(True)
            return True
        else:
            self.app_window.display_error_message("Could not create time entry")
            return False

    def _start_display_updates(self) -> None:
        """Start the timer that updates the elapsed time display"""
        self.display_update_timer = QTimer()
        self.display_update_timer.timeout.connect(self._update_elapsed_time_display)
        self.display_update_timer.start(1000)  # Update every second

    def _update_elapsed_time_display(self) -> None:
        """Update the elapsed time shown in the timer display"""
        current_duration = self.activity_timer_model.get_current_duration()
        self.app_window.activity_timer_panel.update_elapsed_time(current_duration)

    def _get_current_selected_mob(self) -> str:
        return self.activity_timer_model.current_selected_mob

    def _stop_current_activity(self) -> bool:
        """
        Stop the currently running activity timer and update all relevant views

        Returns:
            bool: True as operation always succeeds
        """
        self.activity_timer_model.stop_timer()
        self._stop_display_updates()
        self.app_window.activity_timer_panel.update_timer_state(False)
        self._refresh_views_after_stop()
        return True

    def _stop_display_updates(self) -> None:
        """Stop and cleanup the display update timer"""
        if self.display_update_timer:
            self.display_update_timer.stop()
            self.display_update_timer.deleteLater()
            self.display_update_timer = None
            # Reset display to 0:00:00
            self._update_elapsed_time_display()

    def _refresh_views_after_stop(self) -> None:
        """Update all relevant views after stopping an activity"""
        self.app_window.activity_timer_panel.refresh_activity_history()
        self.app_window.user_stats_controller.refresh_user_statistics()
