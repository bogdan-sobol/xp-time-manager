from datetime import datetime
from database import Database
# TO-DO: Replace print wiht logging
import logging
from constants import MAX_ACTIVITY_NAME_SIZE

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer_on = False
        self.no_entries = None
        self.current_entry_id = 0

        self.db = Database()
        self.initUI()


    def initUI(self):
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
        history_container = QWidget()
        self.time_entries_list = QVBoxLayout(history_container)
        # Align entries to top
        self.time_entries_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Remove side margins
        self.time_entries_list.setContentsMargins(0, 5, 0, 5)
        # Spacing between entries
        self.time_entries_list.setSpacing(5)

        # Setup scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(history_container)

        # TMP: Gray color of container to see broders better
        history_container.setStyleSheet("background-color: gray;")

        self.main_layout.addWidget(scroll_area)


    def create_bottom_bar(self) -> None:
        """Creates and places bottom bar"""
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)

        self.activity_name = QLineEdit()
        self.activity_name.setPlaceholderText("Enter activity name...")
        self.activity_name.setMaximumWidth(300)
        bottom_bar.addWidget(self.activity_name)

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
        """Renders finished time entries to the application"""
        # Clear existing entries from UI
        for i in reversed(range(self.time_entries_list.count())): 
            self.time_entries_list.itemAt(i).widget().deleteLater()

        entry_list = self.db.get_recent_entries()

        # No entries in database or error
        if not entry_list:
            # TMP
            print("No entries in the database.")

            self.no_entries = QLabel("Currently there are no time entries.")
            self.no_entries.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.time_entries_list.addWidget(self.no_entries)
            return
        
        # Delete message if displayed
        if self.no_entries:
            self.no_entries.deleteLater()
        
        for entry in entry_list:
            frame = QHBoxLayout()

            name = QLabel(entry[1])
            duration = QLabel(entry[3])
            duration.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

            frame.addWidget(name)
            frame.addWidget(duration)

            frame_widget = QWidget()
            frame_widget.setLayout(frame)
            frame_widget.setMinimumHeight(50)
            frame_widget.setStyleSheet("background-color: white; border-radius: 15px;")

            # Add widget to layout
            self.time_entries_list.addWidget(frame_widget)
    

    def start_stop_timer(self) -> None:
        """Handles starting and stopping timer"""        
        # Start tracking
        if self.timer_on == False:
            # Removes space at the beggining and end
            activity_name = self.activity_name.text().strip()

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
            self.activity_name.setReadOnly(True)

            self.start_time_entry()
        # Stop tracking
        else:
            self.timer_on = False
            self.start_stop_btn.setText("Start")
            # Enable changing activity name
            self.activity_name.setReadOnly(False)

            self.stop_time_entry()

    
    def start_time_entry(self) -> None:
        self.start_time = datetime.now().timestamp()
        activity_name = self.activity_name.text().strip()
        self.current_entry_id = self.db.add_entry(activity_name)

        if self.current_entry_id == -1:
            QMessageBox.critical(self, "Error", "Could not create time entry")
            self.timer_on = False
            self.start_stop_btn.setText("Start")
            return

        self.start_live_timer()

        # TMP
        print()
        print("START ENTRY:")
        print("Entry ID: " + str(self.current_entry_id))
        print("Activity name: " + activity_name)
        print("Start time: " + str(self.start_time))


    def stop_time_entry(self) -> None:
        end_time = datetime.now().timestamp()
        duration = int(end_time - self.start_time) # Total seconds
        formatted_duration = self.format_seconds(duration)
        self.db.finish_entry(self.current_entry_id, duration, formatted_duration)

        # Stop and delete timer
        self.timer.stop()
        self.timer.deleteLater()

        # Refresh history
        self.render_history()

        # TMP
        print()
        print("END ENTRY:")
        print("Duration: " + formatted_duration)
        total = self.format_seconds(self.db.get_total_duration())
        print("Total time: " + total)


    def start_live_timer(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_timer)
        self.timer.start(1000)
            
    
    def update_live_timer(self) -> None:
        if self.timer_on == False:
            self.live_timer.setText("0:00:00")
            self.timer.stop()
            return
            
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