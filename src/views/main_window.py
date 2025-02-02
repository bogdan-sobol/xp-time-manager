# main_window.py
# deals with UI elements and displaying data

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ..controllers.timer_controller import TimerController
from ..utils.logger import setup_logger
from ..utils.constants import DEBUG_MODE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.controller = TimerController(self)
        self.initUI()

    def initUI(self) -> None:
        self.main_layout = self.setup_main_window()
        self.create_timer()

    def setup_main_window(self) -> QHBoxLayout:
        """Returns main layout"""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(QSize(300, 400))
        main_layout = QHBoxLayout()

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        return main_layout

    def create_history_view(self) -> QWidget:
        """Creates and returns history UI as a widget"""
        time_entries_list = QListWidget()
        time_entries_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        time_entries_list.setStyleSheet("""
            QListWidget {
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
        """)

        if DEBUG_MODE:
            time_entries_list.setStyleSheet("background-color: gray;")

        return time_entries_list

    def create_bottom_bar(self) -> QWidget:
        """Creates and returns timer's bottom bar as a widget"""
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)

        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Enter activity name...")
        self.activity_input.setMaximumWidth(300)
        bottom_bar.addWidget(self.activity_input)

        self.live_timer = QLabel("0:00:00")
        self.live_timer.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        bottom_bar.addWidget(self.live_timer)

        # TO-DO: Make this button circular
        self.start_stop_btn = QPushButton("Start")
        self.start_stop_btn.clicked.connect(self.start_stop_button_clicked)
        bottom_bar.addWidget(self.start_stop_btn)

        # Create widget to place layout
        bottom_bar_widget = QWidget()
        bottom_bar_widget.setLayout(bottom_bar)
        bottom_bar_widget.setMinimumHeight(50)
        
        return bottom_bar_widget

    def update_history(self) -> None:
        # Clear existing entries from UI
        self.time_entries_list.clear()

        entry_list = self.controller.get_recent_entries()

        # No entries in database or error
        if not entry_list:
            self.logger.info("No entries in the database.")
            self.no_entries()
            return

        for entry in entry_list:
            self.create_time_entry(entry)
    
    def create_time_entry(self, entry: tuple) -> None:
        """Creates and places time entry"""
        # Create container widget with margins
        container = QWidget()
        container_layout = QVBoxLayout()
        # Add spacing
        container_layout.setContentsMargins(3, 3, 3, 3)
        container.setLayout(container_layout)

        item_widget = QWidget()
        item_widget.setMinimumHeight(50)
        item_widget.setStyleSheet("background-color: white; border-radius: 15px;")

        # Layout for name and duration
        layout = QHBoxLayout()
        # Padding for multi-line text
        layout.setContentsMargins(10, 10, 10, 10)
        item_widget.setLayout(layout)

        # Create and configure activity name label
        activity_name = QLabel(entry[2])

        # Create and configure duration label
        duration = QLabel(entry[4])
        duration.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        # Fix the width of duration label so it doesn't expand
        duration.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        layout.addWidget(activity_name)
        layout.addWidget(duration)

        # Add item widget to container
        container_layout.addWidget(item_widget)

        # Create list item and add to QListWidget
        list_item = QListWidgetItem()
        # Let the item adjust its height based on content
        list_item.setSizeHint(container.sizeHint())
        self.time_entries_list.addItem(list_item)
        self.time_entries_list.setItemWidget(list_item, container)

    def no_entries(self) -> None:
        no_entries_item = QListWidgetItem()
        no_entries_label = QLabel("Currently there are no time entries.")
        no_entries_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add item to the list
        self.time_entries_list.addItem(no_entries_item)
        # Put widget in item
        self.time_entries_list.setItemWidget(no_entries_item, no_entries_label)

    def create_timer(self) -> None:
        """Creates and places timer GUI"""
        timer = QWidget()
        timer_layout = QVBoxLayout(timer)
        timer_layout.setContentsMargins(0, 0, 0, 0)

        self.time_entries_list = self.create_history_view()
        bottom_bar = self.create_bottom_bar()

        timer_layout.addWidget(self.time_entries_list)
        timer_layout.addWidget(bottom_bar)

        self.update_history()

        self.main_layout.addWidget(timer)

    def start_stop_button_clicked(self):
        activity_name = self.activity_input.text().strip()
        self.controller.start_stop_timer(activity_name)

    def set_timer_running_state(self, is_running: bool):
        self.activity_input.setReadOnly(is_running)
        self.start_stop_btn.setText("Stop" if is_running else "Start")

    def update_timer_display(self, time_str: str):
        self.live_timer.setText(time_str)

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Error", message)