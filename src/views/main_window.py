from PyQt6.QtWidgets import QWidget, QMessageBox, QMainWindow, QHBoxLayout
from PyQt6.QtCore import QSize, pyqtSignal

from ..utils.logger import setup_logger
from .components.time_tracking_panel import TimeTrackingPanel
from .components.user_stats_panel import UserStatsPanel


class ApplicationWindow(QMainWindow):
    """
    Main application window that contains all of the UI components
    """

    # Initialize

    ui_initialized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logger = setup_logger()

    def initUI(self) -> None:
        """Initializes and arranges all UI components"""
        self.window_layout = self._create_main_window()
        self.user_stats_panel = UserStatsPanel(self.user_stats_controller)
        self.time_tracking_panel = TimeTrackingPanel(self.time_tracking_controller)

        # Add panels with specific size proportions
        self.window_layout.addWidget(self.user_stats_panel, stretch=5)
        self.window_layout.addWidget(self.time_tracking_panel, stretch=4)

        # Send signal to contoller that UI is initialized
        self.ui_initialized.emit()

    def register_controllers(
        self, time_tracking_controller, user_stats_controller
    ) -> None:
        """Links the window with its corresponding controllers"""
        self.time_tracking_controller = time_tracking_controller
        self.user_stats_controller = user_stats_controller

    # Public interface methods

    def display_error_message(self, message: str) -> None:
        """Shows an error popup with the specified message"""
        QMessageBox.warning(self, "Error", message)

    def show_activity_deletion_conformation(self) -> bool:
        answer = QMessageBox.question(
            self, "Item Deletion", "Are you sure you want to delete this item?"
        )

        if answer == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    # Private helper methods (with _prefix)

    def _create_main_window(self) -> QHBoxLayout:
        """Sets up and returns the main window layout with basic configurations"""
        self.setWindowTitle("XP Time Manager")
        self.setMinimumSize(QSize(300, 200))
        self.setGeometry(0, 0, 700, 500)
        window_layout = QHBoxLayout()

        central_widget = QWidget()
        central_widget.setLayout(window_layout)
        self.setCentralWidget(central_widget)

        return window_layout
