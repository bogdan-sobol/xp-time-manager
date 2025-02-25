from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

from ...utils.logger import setup_logger
from ...utils.constants import DEBUG_MODE
from .activity_history_entry import ActivityHistoryEntry


class ActivityTimerPanel(QWidget):
    """
    Panel containing the activity timer and history of tracked activities
    """

    # Initialize

    def __init__(self, activity_timer_controller):
        super().__init__()
        self.activity_timer_controller = activity_timer_controller
        self.logger = setup_logger()
        self.initUI()

    def initUI(self) -> None:
        """Sets up the complete timer panel interface"""
        panel_layout = QVBoxLayout(self)
        self.setMinimumWidth(100)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        self.activity_history_list = self._create_activity_history_list()
        timer_controls = self._create_timer_controls()

        panel_layout.addWidget(self.activity_history_list)
        panel_layout.addWidget(timer_controls)

        self.refresh_activity_history()

    # Public interface methods

    def refresh_activity_history(self) -> None:
        """Updates the activity history list with latest data"""
        self.activity_history_list.clear()
        recent_entries = self.activity_timer_controller.get_recent_entries()

        if not recent_entries:
            self._show_empty_history_message()
            return

        for entry in recent_entries:
            self._create_activity_entry(entry)

    def refresh_activity_selector(self) -> None:
        is_timer_running = (
            self.activity_timer_controller.activity_timer_model.is_timer_running
        )

        # Save current selected item index if timer is running
        if is_timer_running:
            selected_activity_index = self.activity_selector.currentIndex()

        self.activity_selector.clear()

        activities = self.activity_timer_controller.get_activities()

        if not activities:
            self.activity_selector.addItem("Please add an activity first...")
            self.activity_selector.setDisabled(True)
            return

        # Enable selector if timer is not runnig
        if not is_timer_running:
            self.activity_selector.setDisabled(False)

        for activity in activities:
            activity_name = activity[2]
            self.activity_selector.addItem(activity_name)

        # Restore previosly selected item if time is running
        if is_timer_running:
            self.activity_selector.setCurrentIndex(selected_activity_index + 1)

    def update_timer_state(self, is_running: bool):
        """
        Updates UI elements based on timer state
        Changes start/stop button's text
        Disables or enables activity selector
        """
        self.activity_selector.setDisabled(True if is_running else False)
        self.timer_toggle_button.setText("Stop" if is_running else "Start")

    def update_elapsed_time(self, time_str: str) -> None:
        """Updates the displayed elapsed time"""
        self.elapsed_time_display.setText(time_str)

    # Event handlers

    def handle_timer_toggle(self) -> None:
        """Handles the start/stop button click event"""
        activity_name = self.activity_selector.currentText()
        self.activity_timer_controller.handle_start_stop_button_clicked(activity_name)

    # Private helper methods (with _prefix)

    def _create_activity_history_list(self) -> QWidget:
        """Creates a scrollable list view for displaying activity history"""
        activity_list = QListWidget()
        activity_list.itemClicked.connect(
            self.activity_timer_controller.handle_time_entry_selection
        )
        activity_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        activity_list.setStyleSheet(
            """
            QListWidget {
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
        """
        )

        if DEBUG_MODE:
            activity_list.setStyleSheet("background-color: gray;")

        return activity_list

    def _create_timer_controls(self) -> QWidget:
        """Creates the timer control panel with input field and buttons"""
        control_panel = QHBoxLayout()
        control_panel.setContentsMargins(0, 0, 0, 0)

        self.activity_selector = QComboBox()
        self.refresh_activity_selector()
        control_panel.addWidget(self.activity_selector, stretch=5)

        self.elapsed_time_display = QLabel("0:00:00")
        self.elapsed_time_display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        control_panel.addWidget(self.elapsed_time_display, stretch=1)

        # TO-DO: Make this button circular
        self.timer_toggle_button = QPushButton("Start")
        self.timer_toggle_button.clicked.connect(self.handle_timer_toggle)
        control_panel.addWidget(self.timer_toggle_button, stretch=2)

        # Create widget to place layout
        control_panel_widget = QWidget()
        control_panel_widget.setLayout(control_panel)
        control_panel_widget.setMinimumHeight(50)

        return control_panel_widget

    def _show_empty_history_message(self) -> None:
        """Displays a message when no activities are in database"""
        empty_list_message = QListWidgetItem("Currently there are no time entries.")
        empty_list_message.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set data to distiguish item from history entries
        empty_list_message.setData(Qt.ItemDataRole.UserRole, "not_a_history_entry")
        self.activity_history_list.addItem(empty_list_message)

    def _create_activity_entry(self, activity_data: tuple) -> None:
        """Creates and adds a new activity entry to the history list"""
        # ID of row in the time_entries table
        entry_id = activity_data[0]
        entry_widget = ActivityHistoryEntry(activity_data)
        list_item = entry_widget.list_item

        entry_widget.setup_delete_action(
            entry_id, self.activity_timer_controller.delete_time_entry
        )

        self.activity_history_list.addItem(list_item)
        self.activity_history_list.setItemWidget(list_item, entry_widget)
