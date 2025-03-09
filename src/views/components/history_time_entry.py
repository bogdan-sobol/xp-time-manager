from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt


class HistoryTimeEntry(QWidget):
    """
    Widget representing a single history time entry in the history list
    Displays activity name, duration, and provides delete functionality
    """

    # Initialize

    def __init__(self, time_entry_data: dict):
        super().__init__()
        self.time_entry_data: dict = time_entry_data
        # Create container with proper spacing for the entry
        container_layout = self._create_entry_container()
        entry_widget = self._create_entry_background()

        # Set up the main layout for entry content
        entry_content_layout = self._create_entry_content_layout()
        entry_widget.setLayout(entry_content_layout)

        # Create and configure entry components
        activity_label = self._create_activity_name_label(
            time_entry_data["activity_name"]
        )
        duration_label = self._create_duration_label(time_entry_data["duration"])
        self.delete_button = self._create_delete_button()

        # Arrange components in the layout
        entry_content_layout.addWidget(activity_label)
        entry_content_layout.addWidget(duration_label)
        entry_content_layout.addWidget(self.delete_button)

        # Add the complete entry to the container
        container_layout.addWidget(entry_widget)

        # Create and configure empty list item for entry widget
        self.list_item = self._create_list_item()
        # Store delete button reference for event handling
        self.list_item.setData(Qt.ItemDataRole.UserRole, self.delete_button)

    # Public interface methods

    def setup_delete_action(self, entry_id: int, delete_callback):
        """
        Connects the delete button to its corresponding action

        Args:
            entry_id: Database ID of the activity
            delete_callback: Function to call when delete is clicked
        """
        self.delete_button.clicked.connect(lambda: delete_callback(entry_id, self))

    # Private helper methods (with _prefix)

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
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )

        return duration_label

    def _create_delete_button(self) -> QPushButton:
        """Creates a circular delete button with hover effects"""
        delete_button = QPushButton("X")

        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet(
            """
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
        """
        )

        delete_button.hide()
        return delete_button

    def _create_list_item(self) -> QListWidgetItem:
        """Creates a list item sized to match the entry widget"""
        list_item = QListWidgetItem()
        list_item.setSizeHint(self.sizeHint())
        return list_item
