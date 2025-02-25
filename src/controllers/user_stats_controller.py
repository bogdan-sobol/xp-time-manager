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
        self.user_stats_model = user_stats_model

    # Level and XP panel

    def update_user_level(self) -> None:
        """Updates user's level in GUI"""
        user_level = self.user_stats_model.user_model.current_user_level
        self.app_window.user_stats_panel.update_user_level(user_level)

    def update_user_xp(self) -> None:
        """Updates user's XP and XP leftover in GUI"""
        user_xp = self.user_stats_model.user_model.current_user_xp
        user_level = self.user_stats_model.user_model.current_user_level

        total_xp_needed = self.user_stats_model.user_model.calculate_xp_to_next_level(
            user_level
        )

        self.app_window.user_stats_panel.update_user_xp(user_xp, total_xp_needed)

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
            # Shorter reference to the activity list
            self.activity_list: QListWidget = (
                self.app_window.user_stats_panel.activity_list
            )

            # Save references to "Add new activity" to return it back later
            self.add_activity_item_row = self.activity_list.row(item)
            self.add_activity_item = self.activity_list.takeItem(
                self.add_activity_item_row
            )

            # Widget with QLineEdit
            create_new_activity_widget: QWidget = (
                self.app_window.user_stats_panel.create_activity_creation_widget()
            )

            empty_list_item = QListWidgetItem()
            empty_list_item.setSizeHint(create_new_activity_widget.sizeHint())

            # Put creation widget into empty item inside the activity list
            self.activity_list.insertItem(self.add_activity_item_row, empty_list_item)
            self.activity_list.setItemWidget(
                empty_list_item, create_new_activity_widget
            )

            self.activity_creation_input: QLineEdit = (
                self.app_window.user_stats_panel.activity_creation_input
            )
            self.activity_creation_input.setFocus()
            self.activity_creation_input.focusOutEvent = (
                self.handle_focusout_activity_creation_input
            )
            self.activity_creation_input.keyPressEvent = (
                self.handle_keypress_activity_creation_input
            )
        else:
            self.user_stats_model.currently_selected_activity_item = item

    def handle_focusout_activity_creation_input(self, event) -> None:
        """
        Removes QLineEdit item for activity creation
        Places back "Add new activity" item
        Cleans up used variables
        """
        # Remove activity creation item
        self.activity_list.takeItem(self.add_activity_item_row)
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
            activity_timer_controller = (
                self.app_window.activity_timer_panel.activity_timer_controller
            )
            is_timer_running = (
                activity_timer_controller.activity_timer_model.is_timer_running
            )

            # Make sure timer is not running
            if is_timer_running:
                self.app_window.display_error_message(
                    "You can't delete activities when tracking time"
                )
                return

            if self.app_window.show_activity_deletion_conformation():
                self._delete_activity()

        # Handle event properly
        activity_list: QListWidget = self.app_window.user_stats_panel.activity_list
        QListWidget.keyPressEvent(activity_list, event)

    # Activities manipulations

    def get_activities(self):
        return self.user_stats_model.get_user_activities()

    def add_activity(self, activity_name) -> bool:
        # If successfully added activity to database
        if self.user_stats_model.add_new_activity(activity_name):
            # Refresh activity list and activity selector
            self.app_window.user_stats_panel.refresh_activity_list()
            self.app_window.activity_timer_panel.refresh_activity_selector()
            return True
        return False

    def place_add_new_activity_item_back(self) -> None:
        """
        After an activity has been added or canceled
        Puts "Add new activity" item back
        to the beginning of the activity list
        """
        self.app_window.user_stats_panel.activity_list.insertItem(
            0, self.add_activity_item
        )

    def cleanup_after_new_activity_creation(self) -> None:
        self.activity_list = None
        self.add_activity_item = None
        self.add_activity_item_row = None
        self.activity_creation_input = None

    def _delete_activity(self) -> None:
        activity_list: QListWidget = self.app_window.user_stats_panel.activity_list
        selected_item: QListWidgetItem = (
            self.user_stats_model.currently_selected_activity_item
        )
        activity_id = selected_item.data(Qt.ItemDataRole.UserRole)["activity_id"]

        # Remove item from list
        item_row = activity_list.row(selected_item)
        activity_list.takeItem(item_row)

        # Remove activity from database
        self.user_stats_model.delete_user_activity(activity_id)

        self.refresh_after_activity_update()

    def refresh_after_activity_update(self) -> None:
        """
        Updates activity list and activity selector
        Preserves "Add new activity" item
        """
        activity_list: QListWidget = self.app_window.user_stats_panel.activity_list
        add_new_activity_item = activity_list.takeItem(0)

        self.app_window.user_stats_panel.refresh_activity_list()
        self.app_window.activity_timer_panel.refresh_activity_selector()

        activity_list.insertItem(0, add_new_activity_item)

    # XP rate manipulations

    def set_selected_mob(self, mob: str):
        self.user_stats_model.set_user_xp_rate_mob(mob)
