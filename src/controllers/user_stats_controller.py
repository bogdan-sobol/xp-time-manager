from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QWidget,
)
from PyQt6.QtCore import Qt


class UserStatsController:
    def __init__(self, app_window, user_stats_model):
        self.app_window = app_window
        self.model = user_stats_model

        self.app_window.ui_initialized.connect(self._on_ui_initialized)

    # Level and XP panel

    def update_user_level(self) -> None:
        """Updates user's level in GUI"""
        user_level = self.model.user_model.current_user_level
        self.view.update_user_level(user_level)

    def update_user_xp(self) -> None:
        """Updates user's XP and XP leftover in GUI"""
        user_xp = self.model.user_model.current_user_xp
        user_level = self.model.user_model.current_user_level

        total_xp_needed = self.model.user_model.calculate_xp_to_next_level(user_level)

        self.view.update_user_xp(user_xp, total_xp_needed)

    def refresh_user_statistics(self) -> None:
        """Updates level and XP in dashboard GUI"""
        self.update_user_level()
        self.update_user_xp()

    # Event handlers

    def handle_xp_rate_change(self, button) -> None:
        selected_mob = button.text()
        self.set_selected_mob(selected_mob)

    def handle_activity_item_selection(self, item: QListWidgetItem) -> None:
        if item.data(Qt.ItemDataRole.UserRole) == "add_activity":
            # Save references to "Add new activity" item
            # to return it back on place later
            self.add_activity_item_row = self.view.activity_list.row(item)
            self.add_activity_item = self.view.activity_list.takeItem(
                self.add_activity_item_row
            )

            # Widget with QLineEdit to type new activity name
            widget_for_creating_new_activities: QWidget = (
                self.view.create_activity_creation_widget()
            )

            empty_list_item = QListWidgetItem()
            empty_list_item.setSizeHint(widget_for_creating_new_activities.sizeHint())

            # Put creation widget into empty item inside the activity list
            self.view.activity_list.insertItem(
                self.add_activity_item_row, empty_list_item
            )
            self.view.activity_list.setItemWidget(
                empty_list_item, widget_for_creating_new_activities
            )

            self.activity_creation_input: QLineEdit = self.view.activity_creation_input
            self.activity_creation_input.setFocus()
            self.activity_creation_input.focusOutEvent = (
                self.handle_focusout_activity_creation_input
            )
            self.activity_creation_input.keyPressEvent = (
                self.handle_keypress_activity_creation_input
            )
        else:
            self.model.currently_selected_activity_item = item

    def handle_focusout_activity_creation_input(self, event) -> None:
        """
        Removes QLineEdit item for activity creation
        Places back "Add new activity" item
        Cleans up used variables
        """
        # Remove activity creation item
        self.view.activity_list.takeItem(self.add_activity_item_row)
        # Place "Add new activity" item back
        self.place_add_new_activity_item_back()
        # Call focusOut event to handle it properly
        QLineEdit.focusOutEvent(self.activity_creation_input, event)
        # Clean up variables
        self.cleanup_after_new_activity_creation()

    def handle_keypress_activity_creation_input(self, event) -> None:
        """
        If Escape is pressed = clears focus from activity creation input
        If Enter is pressed = calls add_activity function
        """
        key = event.key()
        if key == Qt.Key.Key_Escape:
            # Removing focus triggers handle_focusout function
            self.activity_creation_input.clearFocus()
        elif key == Qt.Key.Key_Return:
            self.handle_return_press_in_activity_creation_input()
        else:
            # If none of keys above, handle event usually
            QLineEdit.keyPressEvent(self.activity_creation_input, event)

    def handle_return_press_in_activity_creation_input(self) -> None:
        """
        Adds new activity if valid activity_name
        Shows message if activity name is invallid
        Puts "Add new activity" item back
        Cleans up used variables
        """
        activity_name = self.activity_creation_input.text()

        # If activity wasn't added
        if not self.add_activity(activity_name):
            self.app_window.display_error_message("Please enter valid activity name.")

        self.place_add_new_activity_item_back()
        self.cleanup_after_new_activity_creation()

    def handle_delete_press_activity_list(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete:
            time_tracking_controller = self.app_window.time_tracking_panel.controller
            is_timer_running = time_tracking_controller.model.is_timer_running

            # Make sure timer is not running
            if is_timer_running:
                self.app_window.display_error_message(
                    "You can't delete activities when tracking time"
                )
                return

            if self.app_window.show_activity_deletion_conformation():
                self._delete_activity()

        # Handle event properly
        QListWidget.keyPressEvent(self.view.activity_list, event)

    # Activities manipulations

    def get_activities(self):
        return self.model.get_user_activities()

    def add_activity(self, activity_name) -> bool:
        # If successfully added activity to database
        if self.model.add_new_activity(activity_name):
            # Refresh the activity list
            self.view.refresh_activity_list()
            # Refesh activity selector in the time tracking panel
            time_tracking_panel = self.app_window.time_tracking_panel
            time_tracking_panel.controller.refresh_activity_selector()
            return True
        return False

    def place_add_new_activity_item_back(self) -> None:
        """
        After an activity has been added or canceled
        Puts "Add new activity" item back
        to the beginning of the activity list
        """
        self.view.activity_list.insertItem(0, self.add_activity_item)

    def cleanup_after_new_activity_creation(self) -> None:
        self.add_activity_item = None
        self.add_activity_item_row = None
        self.activity_creation_input = None

    def _delete_activity(self) -> None:
        selected_item = self.model.currently_selected_activity_item
        activity_id = selected_item.data(Qt.ItemDataRole.UserRole)["activity_id"]

        # Remove item from list
        item_row = self.view.activity_list.row(selected_item)
        self.view.activity_list.takeItem(item_row)

        # Remove activity from database
        self.model.delete_user_activity(activity_id)

        self.refresh_after_activity_update()

    def refresh_after_activity_update(self) -> None:
        """
        Updates activity list and activity selector
        Preserves "Add new activity" item
        """
        add_new_activity_item = self.view.activity_list.takeItem(0)

        self.view.refresh_activity_list()
        self.app_window.time_tracking_panel.controller.refresh_time_entries_history()

        self.view.activity_list.insertItem(0, add_new_activity_item)

    # XP rate manipulations

    def set_selected_mob(self, mob: str):
        self.model.set_user_xp_rate_mob(mob)

    # Private helper methods

    def _on_ui_initialized(self):
        self.view = self.app_window.user_stats_panel
        self.refresh_user_statistics()
