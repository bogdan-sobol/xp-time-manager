# main_window.py
# Handles the application's main user interface components and data visualization
# Uses PyQt6 for creating a desktop application with timer and dashboard features

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ..utils.logger import setup_logger
from ..utils.constants import DEBUG_MODE

class ApplicationWindow(QMainWindow):
    """
    Main application window that contains both the timer 
    and user statistics dashboard
    """
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()


    def register_controllers(self, activity_timer_controller,
                            user_stats_controller) -> None:
        """Links the window with its corresponding controllers"""
        self.activity_timer_controller = activity_timer_controller
        self.user_stats_controller = user_stats_controller


    def create_main_window(self) -> QHBoxLayout:
        """Sets up and returns the main window layout with basic configurations"""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(QSize(300, 200))
        self.setGeometry(0, 0, 700, 500)
        window_layout = QHBoxLayout()

        central_widget = QWidget()
        central_widget.setLayout(window_layout)
        self.setCentralWidget(central_widget)

        return window_layout


    def display_error_message(self, message: str) -> None:
        """Shows an error popup with the specified message"""
        QMessageBox.warning(self, "Error", message)


    def initUI(self) -> None:
        """Initializes and arranges all UI components"""
        self.window_layout = self.create_main_window()
        self.stats_panel = UserStatsPanel(self.user_stats_controller)
        self.activity_timer_panel = ActivityTimerPanel(self.activity_timer_controller)
        self.user_stats_controller.refresh_user_statistics()

        # Add panels with specific size proportions
        self.window_layout.addWidget(self.stats_panel, stretch=5)
        self.window_layout.addWidget(self.activity_timer_panel, stretch=4)


class ActivityTimerPanel(QWidget):
    """
    Panel containing the activity timer and history of tracked activities
    """
    def __init__(self, activity_timer_controller):
        super().__init__()
        self.activity_timer_controller = activity_timer_controller
        self.logger = setup_logger()
        self.initUI()


    def create_activity_history_list(self) -> QWidget:
        """Creates a scrollable list view for displaying activity history"""
        activity_list = QListWidget()
        activity_list.itemClicked.connect(
            self.timer_controller.handle_item_selection
        )
        activity_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        activity_list.setStyleSheet("""
            QListWidget {
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
        """)

        if DEBUG_MODE:
            activity_list.setStyleSheet("background-color: gray;")

        return activity_list


    def show_empty_history_message(self) -> None:
        """Displays a message when no activities are in database"""
        empty_list_item = QListWidgetItem()
        empty_message = QLabel("Currently there are no time entries.")
        empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activity_history_list.addItem(empty_list_item)
        self.activity_history_list.setItemWidget(empty_list_item, empty_message)


    def create_activity_entry(self, activity_data: tuple) -> None:
        """Creates and adds a new activity entry to the history list"""
        # ID of row in the time_entries table
        entry_id = activity_data[0]
        entry_widget = TimeEntry(activity_data)
        list_item = entry_widget.list_item

        entry_widget.setup_delete_action(
            entry_id,
            self.activity_timer_controller.delete_time_entry
        )

        self.activity_history_list.addItem(list_item)
        self.activity_history_list.setItemWidget(list_item, entry_widget)


    def refresh_activity_history(self) -> None:
        """Updates the activity history list with latest data"""
        self.activity_history_list.clear()
        recent_activities = self.activity_timer_controller.get_recent_entries()

        if not recent_activities:
            self.logger.info("No activities found in the database")
            self.show_empty_history_message()
            return

        for activity in recent_activities:
            self.create_activity_entry(activity)


    def create_timer_controls(self) -> QWidget:
        """Creates the timer control panel with input field and buttons"""
        control_panel = QHBoxLayout()
        control_panel.setContentsMargins(0, 0, 0, 0)

        self.activity_name_input = QLineEdit()
        self.activity_name_input.setPlaceholderText("Enter activity name...")
        self.activity_name_input.setMaximumWidth(300)
        control_panel.addWidget(self.activity_name_input)

        self.elapsed_time_display = QLabel("0:00:00")
        self.elapsed_time_display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        control_panel.addWidget(self.live_timer)

        # TO-DO: Make this button circular
        self.timer_toggle_button = QPushButton("Start")
        self.timer_toggle_button.clicked.connect(self.handle_timer_toggle)
        control_panel.addWidget(self.start_stop_btn)

        # Create widget to place layout
        control_panel_widget = QWidget()
        control_panel_widget.setLayout(control_panel)
        control_panel_widget.setMinimumHeight(50)
        
        return control_panel_widget


    def handle_timer_toggle(self):
        """Handles the start/stop button click event"""
        activity_name = self.activity_name_input.text()
        self.activity_timer_controller.start_stop_timer(activity_name)


    def update_timer_state(self, is_running: bool):
        """Updates UI elements based on timer state"""
        self.activity_name_input.setReadOnly(is_running)
        self.start_stop_btn.setText("Stop" if is_running else "Start")


    def update_elapsed_time(self, time_str: str) -> None:
        """Updates the displayed elapsed time"""
        self.elapsed_time_display.setText(time_str)


    def initUI(self) -> None:
        """Sets up the complete timer panel interface"""
        panel_layout = QVBoxLayout(self)
        self.setMinimumWidth(100)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        self.activity_history_list = self.create_activity_history_list()
        timer_controls = self.create_timer_controls()

        panel_layout.addWidget(self.activity_history_list)
        panel_layout.addWidget(timer_controls)

        self.refresh_activity_history()


class ActivityHistoryEntry(QWidget):
    """
    Widget representing a single activity entry in the history list.
    Displays activity name, duration, and provides delete functionality.
    """
    def __init__(self, activity_data: tuple):
        super().__init__()
        # Create container with proper spacing for the entry
        container_layout = self._create_entry_container()
        entry_widget = self._create_entry_background()

       # Set up the main layout for entry content
        entry_content_layout = self._create_entry_content_layout()
        entry_widget.setLayout(entry_content_layout)

        activity_name = activity_data[2]
        duration = activity_data[4]

        # Create and configure entry components
        activity_label = self._create_activity_name_label(activity_name)
        duration_label = self._create_duration_label(duration)
        self.delete_button = self._create_delete_button()
        
        # Arrange components in the layout
        entry_content_layout.addWidget(activity_label)
        entry_content_layout.addWidget(duration_label)
        entry_content_layout.addWidget(self.delete_btn)

        # Add the complete entry to the container
        container_layout.addWidget(entry_widget)

        # Create and configure list item for this entry
        self.list_item = self._create_list_item()
        # Store delete button reference for event handling
        self.list_item.setData(Qt.ItemDataRole.UserRole, self.delete_button)


    def _create_entry_container(self) -> QVBoxLayout:
        """Creates main layout"""
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(container_layout)
        return container_layout


    def _create_entry_background(self) -> QWidget:
        """Creates the visual container for the entry with styling"""
        background = QWidget()
        background.setMinimumHeight(50)
        background.setStyleSheet("background-color: white; border-radius: 15px;")
        return background


    def _create_entry_content_layout(self) -> QHBoxLayout:
        """Creates the horizontal layout for entry content"""
        return QHBoxLayout()


    def _create_activity_name_label(self, activity_name: str) -> QLabel:
        """Creates a label displaying the activity name"""
        return QLabel(activity_name)


    def _create_duration_label(self, formatted_duration: str) -> QLabel:
        """Creates a fixed-width label displaying activity duration"""
        duration_label = QLabel(formatted_duration)

        # Align text and fix the label width
        duration_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
        )
        duration_label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Minimum
        )

        return duration_label


    def _create_delete_button(self):
        """Creates a circular delete button with hover effects"""
        delete_button = QPushButton("X")

        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: gray;
            }
        """)

        delete_button.hide()
        return delete_button


    def setup_delete_action(self, entry_id: int, delete_callback):
        """
        Connects the delete button to its corresponding action
        
        Args:
            entry_id: Database ID of the activity
            delete_callback: Function to call when delete is clicked
        """
        self.delete_button.clicked.connect(
            lambda: delete_callback(entry_id, self)
        )


    def _create_list_item(self) -> QListWidgetItem:
        """Creates a list item sized to match the entry widget"""
        list_item = QListWidgetItem()
        list_item.setSizeHint(self.sizeHint())
        return list_item


class UserStatsPanel(QWidget):
    """
    Panel displaying user statistics including level and experience points.
    Provides visual feedback on user progress.
    """
    def __init__(self, stats_controller):
        super().__init__()
        self.stats_controller = stats_controller
        self.logger = setup_logger()
        self.initUI()


    def initUI(self) -> None:
        """Sets up the complete statistics panel interface"""
        self.setup_panel_layout()
        stats_display = self.create_stats_display()
        self.panel_layout.addWidget(stats_display)


    def setup_panel_layout(self):
        """Configures the basic panel layout and styling"""
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(150)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        if DEBUG_MODE:
            self.setStyleSheet("background-color: blue;")


    def create_stats_display(self) -> QWidget:
        """Creates the display widget for user statistics"""
        # Initialize stat labels with empty text
        self.level_display = QLabel("")
        self.xp_display = QLabel("")

        # Configure label alignments
        self.level_display.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )
        self.xp_display.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )

        # Create widget to hold stat displays
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)

        # Add displays to layout
        stats_layout.addWidget(self.level_display)
        stats_layout.addWidget(self.xp_display)

        return stats_widget


    def update_user_level(self, level: int):
        """Updates the displayed user level"""
        self.logger.debug(f"Updating level display to: {level}")
        self.level_display.setText(f"Level: {level}")


    def update_user_xp(self, current_xp: float, xp_needed: int):
        """
        Updates the displayed XP
        
        Args:
            current_xp: Current XP points
            xp_needed: XP needed for next level
        """
        self.logger.debug(f"Updating XP display to: {current_xp}/{xp_needed}")
        self.xp_display.setText(f"XP: {current_xp}/{xp_needed}")