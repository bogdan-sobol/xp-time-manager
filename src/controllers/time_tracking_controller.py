from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QListWidgetItem

from ..utils.constants import DEFAULT_HISTORY_ENTRIES_DISPLAYED


class TimeTrackingController:
    """
    Controls the interaction between the UI and the time tracking model

    This controller manages the timer functionality
    including starting/stopping time entry,
    updating the elapsed time display
    and handling time entry operations in the UI

    Attributes:
        app_window: The main application window containing all views
        time_tracking_model: The model handling timer logic and data persistence
    """

    # Initialize

    def __init__(self, app_window, time_tracking_model):
        self.app_window = app_window
        self.model = time_tracking_model
        # Stores QTimer for elapsed time updates
        self.qtimer = None
        self.app_window.ui_initialized.connect(self._on_ui_initialized)

    # Public interface methods

    def get_history_time_entries(
        self, entries_quantity: int = DEFAULT_HISTORY_ENTRIES_DISPLAYED
    ) -> list:
        """Retrieves the list of history time entries"""
        return self.model.get_history_time_entries(entries_quantity)

    def delete_history_time_entry(self, entry_id: int, entry_widget: QWidget) -> None:
        """
        Delete a time entry and update all relevant views

        Args:
            entry_id: ID of the time entry to delete in the database
            entry_widget: Widget representing the history entry in the UI

        Side Effects:
            - Removes the history entry from database
            - Updates UI
            - Refreshes statistics
        """
        # Delete from database and UI
        self.model.delete_history_time_entry(entry_id)
        entry_widget.deleteLater()

        # Update statistics and views
        self.model.user_model.reevaluate_user_stats()
        self.app_window.user_stats_controller.refresh_user_statistics()

        # Reset selection state
        self.model.current_selected_item = None
        self.model.current_delete_btn = None

        # Refresh entry list
        self.refresh_time_entries_history()

    def get_activities(self):
        return self.model.get_user_activities()

    def refresh_time_entries_history(
        self, entries_quantity: int = DEFAULT_HISTORY_ENTRIES_DISPLAYED
    ):
        """Updates the time entries history list"""
        self.view.time_entries_history_list.clear()

        time_entries = self.get_history_time_entries(entries_quantity)

        if not time_entries:
            self.view.show_empty_history_message()
            return

        previous_entry_date = None
        for entry in time_entries:
            # If time entry has duration (meaning it was completed)
            if entry["duration"]:
                entry_date = self.model.convert_start_time_to_history_date(
                    entry["start_time"]
                )

                if entry_date != previous_entry_date:
                    self.view.create_date_item_for_time_entries_history(entry_date)

                self.view.create_history_time_entry(entry)

                previous_entry_date = entry_date

        if self.is_show_more_entries_button_needed(len(time_entries)):
            self.view.display_show_more_entries_button()

    def is_show_more_entries_button_needed(self, current_entries_count: int) -> bool:
        total_entries_count = self.model.total_history_entries_count

        if current_entries_count < total_entries_count:
            return True

        return False

    def refresh_activity_selector(self):
        """
        Refreshes activity selector with fresh data
        Saves currently selected item if timer tracking is ON
        """
        is_timer_running = self.model.is_timer_running

        # Save current selected item index if timer is running
        if is_timer_running:
            selected_activity_index = self.view.activity_selector.currentIndex()

        self.view.refresh_activity_selector()

        # Enable selector if timer is not runnig
        if not is_timer_running:
            self.view.activity_selector.setDisabled(False)

        # Restore previosly selected item if time is running
        if is_timer_running:
            self.view.activity_selector.setCurrentIndex(selected_activity_index + 1)

    # Event handlers

    def handle_start_stop_button_clicked(self, activity_name: str) -> bool:
        """
        Handle the start/stop button click event in the timer view

        If the timer is not running, starts a new time entry
        If the timer is running, stops the current time entry

        Returns:
            bool: True if operation was successful, False otherwise

        Side Effects:
            - Updates UI state
            - Creates/stops timer
            - Updates history view (when stopped)
            - Updates dashboard statistics (when stopped)
        """
        if not self.model.is_timer_running:
            return self._start_new_time_entry(activity_name)
        else:
            return self._stop_current_time_entry()

    def handle_time_entry_selection(self, item: QListWidgetItem) -> None:
        """
        Handle when user selects a time entry in the history list

        Args:
            item: The selected list widget item
        """
        item_data = item.data(Qt.ItemDataRole.UserRole)

        # If item data is empty
        if not item_data:
            return

        if item_data == "show_more_entries":
            entries_count = self.view.time_entries_history_list.count()

            # (entries_count - 1) excludes the "Show more" button itself
            self.refresh_time_entries_history(
                (entries_count - 1) + DEFAULT_HISTORY_ENTRIES_DISPLAYED
            )
        else:
            self.model.show_delete_button(item)

    # Private helper methods

    def _on_ui_initialized(self) -> None:
        """
        Manipulation that can be done only after
        the app window UI is initialized
        """
        self.view = self.app_window.time_tracking_panel
        # Display first time entries in the history list
        self.refresh_time_entries_history(DEFAULT_HISTORY_ENTRIES_DISPLAYED)

    def _start_new_time_entry(self, activity_name: str) -> bool:
        """
        Start time tracking

        Returns:
            bool: True if activity was started successfully, False otherwise
        """
        # Check if user has activities
        if not self.model.user_has_activities:
            self.app_window.display_error_message(
                "Please add at least one activity first"
            )
            return False

        # Attempt to start the timer
        if self.model.start_time_tracking(activity_name):
            self._start_elapsed_time_updates()
            self.view.update_timer_state(True)
            return True
        else:
            self.app_window.display_error_message(
                "Something went wrong when starting time tracking"
            )
            return False

    def _start_elapsed_time_updates(self) -> None:
        """Start the timer that updates the elapsed time display"""
        self.qtimer = QTimer()
        self.qtimer.timeout.connect(self._update_elapsed_time_display)
        self.qtimer.start(1000)  # Update every second

    def _update_elapsed_time_display(self) -> None:
        """Update the elapsed time shown in the time tracking panel"""
        current_duration = self.model.get_formatted_elapsed_time_since_start()
        self.view.update_elapsed_time(current_duration)

    def _get_current_selected_mob(self) -> str:
        return self.model.current_selected_mob

    def _stop_current_time_entry(self) -> None:
        """
        Stop the currently running time tracking

        Side effects:
            - Updates the time entries history
            - Updates user's statistic
            - Stops updating the elapsed time display
        """
        self.model.stop_time_tracking()
        self._stop_elapsed_time_updates()
        self.view.update_timer_state(False)
        self._refresh_views_after_stop()

    def _stop_elapsed_time_updates(self) -> None:
        """Stop and cleanup the QTimer for elapsed time updates"""
        if self.qtimer:
            self.qtimer.stop()
            self.qtimer.deleteLater()
            self.qtimer = None
            # Reset elapsed time to 0:00:00
            self._update_elapsed_time_display()

    def _refresh_views_after_stop(self) -> None:
        """Update relevant views after stopping time tracking"""
        self.refresh_time_entries_history()
        self.app_window.user_stats_controller.refresh_user_statistics()
