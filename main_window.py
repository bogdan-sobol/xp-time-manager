from datetime import datetime
from database import Database
from constants import MAX_ACTIVITY_NAME_SIZE
from logger import setup_logger

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer_on = False
        self.current_entry_id = 0
        self.logger = setup_logger()

        self.db = Database()
        self.initUI()


    def initUI(self) -> None:
        self.main_layout = self.setup_main_window()
        self.create_history_view()
        self.create_bottom_bar()
        self.render_history()


    def setup_main_window(self) -> QVBoxLayout:
        """Returns main layout"""
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(QSize(300, 400))
        main_layout = QVBoxLayout()

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        return main_layout


    def create_history_view(self) -> None:
        """Creates and places history UI"""
        self.time_entries_list = QListWidget()
        self.time_entries_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.time_entries_list.setStyleSheet("""
            QListWidget {
                background-color: gray;
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
        """)

        self.main_layout.addWidget(self.time_entries_list)


    def create_bottom_bar(self) -> None:
        """Creates and places bottom bar"""
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
        self.start_stop_btn.clicked.connect(self.start_stop_timer)
        bottom_bar.addWidget(self.start_stop_btn)

        # Create widget to place layout
        bottom_bar_widget = QWidget()
        bottom_bar_widget.setLayout(bottom_bar)
        bottom_bar_widget.setMinimumHeight(50)
        
        self.main_layout.addWidget(bottom_bar_widget)


    def render_history(self) -> None:
        """Renders finished time entries using QListWidget"""
        # Clear existing entries from UI
        self.time_entries_list.clear()

        entry_list = self.db.get_recent_entries()

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
        activity_name = QLabel(entry[1])

        # Create and configure duration label
        duration = QLabel(entry[3])
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
        # Add item
        self.time_entries_list.addItem(no_entries_item)
        # Place widget in item
        self.time_entries_list.setItemWidget(no_entries_item, no_entries_label)


    def start_stop_timer(self) -> None:
        """Handles starting and stopping timer"""        
        # Start tracking
        if self.timer_on == False:
            # Removes space at the beggining and end
            activity_name = self.activity_input.text().strip()

            # Is there activity name
            if not activity_name: 
                QMessageBox.warning(self, "Warning", "Please enter an activity name!")
                return
        
            # Is activity name not too long
            if len(activity_name) > MAX_ACTIVITY_NAME_SIZE:
                QMessageBox.warning(self, "Warning", "Activity name is too long.")
                return

            self.timer_on = True
            self.start_stop_btn.setText("Stop")
            # Disable changing activity name during tracking
            self.activity_input.setReadOnly(True)

            self.start_time_entry()
        # Stop tracking
        else:
            self.timer_on = False
            self.start_stop_btn.setText("Start")
            # Enable changing activity name
            self.activity_input.setReadOnly(False)

            self.stop_time_entry()

    
    def start_time_entry(self) -> None:
        self.start_time = datetime.now().timestamp()
        activity_name = self.activity_input.text().strip()
        self.current_entry_id = self.db.add_entry(activity_name)

        if self.current_entry_id == -1:
            self.logging.error("Failed to create time entry in database")
            QMessageBox.critical(self, "Error", "Could not create time entry")
            self.timer_on = False
            self.start_stop_btn.setText("Start")
            return

        self.start_live_timer()

        self.logger.info("Started new time entry")
        self.logger.info(f"Activity name: {activity_name}")
        self.logger.info(f"ID: {self.current_entry_id}")
        self.logger.debug(f"Start time: {self.start_time}")


    def stop_time_entry(self) -> None:
        end_time = datetime.now().timestamp()
        duration = int(end_time - self.start_time) # Total seconds
        formatted_duration = self.format_seconds(duration)
        self.db.finish_entry(self.current_entry_id, duration, formatted_duration)

        # Stop and delete timer
        self.timer.stop()
        self.timer.deleteLater()
        self.live_timer.setText("0:00:00")

        # Refresh history
        self.render_history()

        self.logger.info("Stopped time entry")
        self.logger.info(f"Formatted duration: {formatted_duration}")
        self.logger.debug(f"Duration seconds: {duration}")
        self.logger.debug(f"End time: {end_time}")


    def start_live_timer(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_timer)
        self.timer.start(1000)
            
    
    def update_live_timer(self) -> None:
        duration = datetime.now().timestamp() - self.start_time
        self.live_timer.setText(self.format_seconds(duration))

    
    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Converts exact seconds to formated hours, minutes and seconds"""
        if seconds <= 0:
            return "0:00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"


def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()