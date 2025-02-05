# main_window.py
# deals with UI elements and displaying data

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ..utils.logger import setup_logger
from ..utils.constants import DEBUG_MODE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()

    def initialize_controllers(self,
                            timer_contoller,
                            dashboard_controller) -> None:
        self.timer_controller = timer_contoller
        self.dashboard_controller = dashboard_controller

    def setup_main_window(self) -> QHBoxLayout:
        """Returns main layout"""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(QSize(300, 200))
        self.setGeometry(0, 0, 700, 500)
        main_layout = QHBoxLayout()

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        return main_layout

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Error", message)

    def initUI(self) -> None:
        self.main_layout = self.setup_main_window()
        self.dashboard_view = DashboardView(self.dashboard_controller)
        self.timer_view = TimerView(self.timer_controller)
        self.dashboard_controller.update_user_stats()

        self.main_layout.addWidget(self.dashboard_view, stretch=5)
        self.main_layout.addWidget(self.timer_view, stretch=4)


class TimerView(QWidget):
    def __init__(self, timer_controller):
        super().__init__()
        self.timer_controller = timer_controller
        self.logger = setup_logger()
        self.initUI()

    def create_history_view(self) -> QWidget:
        """Creates and returns history UI as a widget"""
        time_entries_list = QListWidget()
        time_entries_list.itemClicked.connect(
            self.timer_controller.handle_item_selection
        )
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
    
    def no_entries(self) -> None:
        no_entries_item = QListWidgetItem()
        no_entries_label = QLabel("Currently there are no time entries.")
        no_entries_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add item to the list
        self.time_entries_list.addItem(no_entries_item)
        # Put widget in item
        self.time_entries_list.setItemWidget(no_entries_item, no_entries_label)

    def create_delete_btn(self, entry_id: int, entry_widget: QWidget):
        delete_btn = QPushButton("X")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
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
        delete_btn.clicked.connect(lambda: self.timer_controller.delete_time_entry(entry_id, entry_widget))
        delete_btn.hide()

        return delete_btn

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

        # Create a delete button (hidden by default)
        delete_btn = self.create_delete_btn(entry[0], container)

        layout.addWidget(activity_name)
        layout.addWidget(duration)
        layout.addWidget(delete_btn)

        # Add item widget to container
        container_layout.addWidget(item_widget)

        # Create list item and add to QListWidget
        list_item = QListWidgetItem()
        # Let the item adjust its height based on content
        list_item.setSizeHint(container.sizeHint())

        # Store the delete button reference in the item as user data
        list_item.setData(Qt.ItemDataRole.UserRole, delete_btn)

        self.time_entries_list.addItem(list_item)
        self.time_entries_list.setItemWidget(list_item, container)

    def update_history(self) -> None:
        # Clear existing entries from UI
        self.time_entries_list.clear()

        entry_list = self.timer_controller.get_recent_entries()

        # No entries in database or error
        if not entry_list:
            self.logger.info("No entries in the database.")
            self.no_entries()
            return

        for entry in entry_list:
            self.create_time_entry(entry)

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

    def start_stop_button_clicked(self):
        activity_name = self.activity_input.text().strip()
        self.timer_controller.start_stop_timer(activity_name)

    def set_timer_running_state(self, is_running: bool):
        self.activity_input.setReadOnly(is_running)
        self.start_stop_btn.setText("Stop" if is_running else "Start")

    def update_timer_display(self, time_str: str):
        self.live_timer.setText(time_str)

    def initUI(self) -> None:
        """Creates and places timer GUI"""
        timer_layout = QVBoxLayout(self)
        self.setMinimumWidth(100)
        timer_layout.setContentsMargins(0, 0, 0, 0)

        self.time_entries_list = self.create_history_view()
        bottom_bar = self.create_bottom_bar()

        timer_layout.addWidget(self.time_entries_list)
        timer_layout.addWidget(bottom_bar)

        self.update_history()


class DashboardView(QWidget):
    def __init__(self, dashboard_controller):
        super().__init__()
        self.dashboard_controller = dashboard_controller
        self.logger = setup_logger()
        self.initUI()

    def initUI(self) -> None:
        """Creates and places dashboard"""
        self.setup_widget()
        stats = self.create_stats_view()

        self.dashboard_layout.addWidget(stats)

    def setup_widget(self):
        self.dashboard_layout = QVBoxLayout(self)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if DEBUG_MODE:
            self.setStyleSheet("background-color: blue;")

    def create_stats_view(self):
        self.user_lvl = QLabel("")
        self.user_xp = QLabel("")

        self.user_lvl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.user_xp.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        stats = QWidget()
        stats_layout = QHBoxLayout(stats)

        stats_layout.addWidget(self.user_lvl)
        stats_layout.addWidget(self.user_xp)

        return stats

    def update_user_lvl(self, level: int):
        self.logger.debug("Updating level label in dashboard view...")
        self.logger.debug(f"New level value is: {level}")
        self.user_lvl.setText(f"Level: {level}")

    def update_user_xp(self, current_xp: float, xp_left: int):
        self.logger.debug("Updating XP label in dashboard view...")
        self.logger.debug(f"New XP value is: {current_xp}/{xp_left}")
        self.user_xp.setText(f"XP: {current_xp}/{xp_left}")