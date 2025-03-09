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
from .history_time_entry import HistoryTimeEntry


class TimeTrackingPanel(QWidget):
    """
    Panel containing the activity timer and the history of tracked time entries
    """

    # Initialize

    def __init__(self, time_tracking_controller):
        super().__init__()
        self.time_tracking_controller = time_tracking_controller
        self.logger = setup_logger()
        self.initUI()

    def initUI(self) -> None:
        """Sets up the complete timer panel interface"""
        panel_layout = QVBoxLayout(self)
        self.setMinimumWidth(100)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        self.time_entries_history_list = self._create_time_entries_history_list()
        timer_controls = self._create_timer_controls()

        panel_layout.addWidget(self.time_entries_history_list)
        panel_layout.addWidget(timer_controls)

    # Public interface methods

    def show_empty_history_message(self) -> None:
        """Displays a message when no history time entries are in database"""
        empty_list_message = QListWidgetItem(
            "Currently there are no history time entries."
        )
        empty_list_message.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_entries_history_list.addItem(empty_list_message)

    def create_history_time_entry(self, time_entry_data: dict) -> None:
        """
        Creates and adds a time entry to the history list
        """
        entry_widget = HistoryTimeEntry(time_entry_data)
        list_item = entry_widget.list_item

        entry_widget.setup_delete_action(
            time_entry_data["id"], self.time_tracking_controller.delete_time_entry
        )

        self.time_entries_history_list.addItem(list_item)
        self.time_entries_history_list.setItemWidget(list_item, entry_widget)

    def create_date_item_for_time_entries_history(self, date: str):
        date_item = QListWidgetItem(date)
        date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_entries_history_list.addItem(date_item)

    def display_show_more_entries_button(self) -> None:
        show_more_button = QListWidgetItem("Show more")
        show_more_button.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        show_more_button.setData(Qt.ItemDataRole.UserRole, "show_more_entries")

        self.time_entries_history_list.addItem(show_more_button)

        return show_more_button

    def refresh_activity_selector(self) -> None:
        self.activity_selector.clear()

        activities = self.time_tracking_controller.get_activities()

        if not activities:
            self.activity_selector.addItem("Please add an activity first...")
            self.activity_selector.setDisabled(True)
            return

        for activity in activities:
            activity_name = activity[2]
            self.activity_selector.addItem(activity_name)

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
        self.time_tracking_controller.handle_start_stop_button_clicked(activity_name)

    # Private helper methods (with _prefix)

    def _create_time_entries_history_list(self) -> QWidget:
        """Creates a scrollable list view for displaying activity history"""
        time_entries_list = QListWidget()
        time_entries_list.itemClicked.connect(
            self.time_tracking_controller.handle_time_entry_selection
        )
        time_entries_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        time_entries_list.setStyleSheet(
            """
            QListWidget {
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
            QListWidget::item:selected {
                color: black;
            }
            """
        )

        if DEBUG_MODE:
            time_entries_list.setStyleSheet("background-color: gray;")

        return time_entries_list

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
