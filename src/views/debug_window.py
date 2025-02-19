from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt


class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def initUI(self) -> None:
        self.setWindowTitle("Debug")
        self.setGeometry(0, 0, 300, 300)

        central_widget = QWidget()
        self.window_layout = QVBoxLayout(central_widget)
        self.window_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._create_timer_debuger()

        self.setCentralWidget(central_widget)

    def initialize_model_access(self, activity_timer_model):
        self.activity_timer_model = activity_timer_model

    def _create_timer_debuger(self):
        label = QLabel("Timer debugger:")

        input_with_button_widget = QWidget()
        input_with_button_layout = QHBoxLayout(input_with_button_widget)
        input_with_button_layout.setContentsMargins(0, 0, 0, 0)

        self.seconds_input = QLineEdit()
        self.seconds_input.setPlaceholderText("Enter seconds to add or subtract..")
        button = QPushButton("Confirm")
        button.clicked.connect(self.handle_button_click)

        input_with_button_layout.addWidget(self.seconds_input)
        input_with_button_layout.addWidget(button)

        self.window_layout.addWidget(label)
        self.window_layout.addWidget(input_with_button_widget)

    def handle_button_click(self):
        seconds = int(self.seconds_input.text())

        old_start_time = self.activity_timer_model.start_time

        if seconds <= 0:
            # Decrease time if negative number
            new_start_time = old_start_time + abs(seconds)
        else:
            # Increases time if positive number
            new_start_time = old_start_time - seconds

        self.activity_timer_model.start_time = new_start_time
