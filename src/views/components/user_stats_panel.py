from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from ...utils.logger import setup_logger
from ...utils.constants import DEBUG_MODE


class UserStatsPanel(QWidget):
    """
    Panel displaying user statistics
    including level and experience points
    Also contains activity managment section
    and buttons for changing XP rate
    """

    # Initialize

    def __init__(self, user_stats_controller):
        super().__init__()
        self.user_stats_controller = user_stats_controller
        self.logger = setup_logger()
        self.initUI()

    def initUI(self) -> None:
        """Sets up the complete statistics panel interface"""
        self._setup_panel_layout()
        stats_display = self._create_stats_display()
        activity_control_panel = self._create_activity_control_panel()

        self.panel_layout.addWidget(activity_control_panel)
        self.panel_layout.addWidget(stats_display)

    # Public interface methods

    def refresh_activity_list(self) -> None:
        self.activity_list.clear()

        activities = self.user_stats_controller.get_activities()

        for activity in activities:
            activity_id = activity[0]
            activity_name = activity[2]

            item = QListWidgetItem(activity_name)
            item.setData(Qt.ItemDataRole.UserRole, {"activity_id": activity_id})

            self.activity_list.addItem(item)

    def update_user_level(self, level: int) -> None:
        """Updates the displayed user level"""
        self.level_display.setText(f"Level: {level}")

    def update_user_xp(self, current_xp: int, xp_needed: int) -> None:
        """
        Updates the displayed XP

        Args:
            current_xp: Current XP points
            xp_needed: total XP amount needed for next level
        """
        self.xp_display.setText(f"XP: {current_xp}/{xp_needed}")

    def create_activity_creation_widget(self) -> QWidget:
        """Creates QLineEdit inside of a widget"""
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)
        widget_layout.setContentsMargins(3, 3, 3, 3)

        self.activity_creation_input = QLineEdit()
        self.activity_creation_input.setPlaceholderText("Please enter activity name...")

        widget_layout.addWidget(self.activity_creation_input)

        return widget

    # Private helper methods (with _prefix)

    def _setup_panel_layout(self) -> None:
        """Configures the basic panel layout and styling"""
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if DEBUG_MODE:
            self.setStyleSheet("background-color: blue;")

    def _create_activity_control_panel(self) -> QWidget:
        """
        Creates a panel for managing activities and XP rate settings.
        The panel includes:
        - Activity list management
        - XP rate selection (Chicken: 1-3 XP, Zombie: 5 XP, Blaze: 10 XP)

        Returns:
            QWidget: Panel containing activity controls and XP settings
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Activity list section
        activity_list_section = self._create_activity_list_section()
        layout.addWidget(activity_list_section)

        # XP Rate selection section
        xp_selection_section = self._create_xp_rate_section()
        layout.addWidget(xp_selection_section)

        return panel

    def _create_activity_list_section(self) -> QWidget:
        """
        Creates the activity list management section
        Returns it as a QWidget
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        activities_label = QLabel("Activities:")
        layout.addWidget(activities_label)

        # Activity list
        self.activity_list = QListWidget()
        layout.addWidget(self.activity_list)

        self.activity_list.itemClicked.connect(
            self.user_stats_controller.handle_activity_item_selection
        )
        self.activity_list.keyPressEvent = (
            self.user_stats_controller.handle_delete_press_activity_list
        )

        # Add activities from database if any
        self.refresh_activity_list()

        # Item for adding new activities
        add_new_activity_item = QListWidgetItem("Add new activity")
        add_new_activity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add data to this item to distinguish it from
        # others activities in the list
        add_new_activity_item.setData(Qt.ItemDataRole.UserRole, "add_activity")
        # Place it at the beginnig of the list
        self.activity_list.insertItem(0, add_new_activity_item)

        return section

    def _create_xp_rate_section(self) -> QWidget:
        """
        Creates the XP rate selection section
        with Minecraft-themed buttons
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        xp_rate_label = QLabel("How much XP per minute?")
        layout.addWidget(xp_rate_label)

        # XP rate buttons
        xp_buttons = self._create_xp_rate_buttons()
        layout.addWidget(xp_buttons)

        # XP rate labels
        xp_labels = self._create_xp_rate_labels()
        layout.addWidget(xp_labels)

        return section

    def _create_xp_rate_buttons(self) -> QWidget:
        """Creates the mob-themed XP rate selection toggle buttons"""
        button_container = QWidget()
        layout = QHBoxLayout(button_container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a button group to manage mutual exclusivity
        self.xp_rate_group = QButtonGroup(self)
        # Make the button group exclusive
        self.xp_rate_group.setExclusive(True)

        # Define XP rate buttons with consistent size policy
        mob_options = ["Chicken", "Zombie", "Blaze"]

        for mob_name in mob_options:
            # Create a container for each button to control its proportions
            button_wrapper = QWidget()
            wrapper_layout = QVBoxLayout(button_wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)

            button = QToolButton()
            button.setIcon(QIcon(f"src/views/img/{mob_name.lower()}_icon.png"))
            button.setIconSize(QSize(60, 60))
            # Sets text for handle function to identify XP rate
            button.setText(mob_name)
            # Make button toggleable
            button.setCheckable(True)
            # Only one button can be checked at a time
            button.setAutoExclusive(True)

            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            button.setMinimumSize(80, 80)

            button.setStyleSheet(
                """
                QToolButton {
                    border: 2px solid #8f8f91;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                }
                QToolButton:checked {
                    background-color: #c0c0c1;
                    border: 3px solid #4a4a4b;
                }
                QToolButton:hover {
                    border: 3px solid #4a4a4b;
                }
            """
            )

            # Add button to wrapper layout
            wrapper_layout.addWidget(button)

            # Make wrapper expand horizontally but maintain aspect ratio
            button_wrapper.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

            # Add wrapper to main layout
            layout.addWidget(button_wrapper, stretch=1)
            self.xp_rate_group.addButton(button)

            # Set Zombie as default selection
            if mob_name == "Zombie":
                button.setChecked(True)
                self.user_stats_controller.set_selected_mob(mob_name)

        # Connect button group to handler
        self.xp_rate_group.buttonClicked.connect(
            self.user_stats_controller.handle_xp_rate_change
        )

        return button_container

    def _create_xp_rate_labels(self) -> QWidget:
        """Creates labels showing XP rates for each mob"""
        label_container = QWidget()
        layout = QHBoxLayout(label_container)
        layout.setContentsMargins(0, 0, 0, 0)

        xp_rates = ["1-3 XP", "5 XP", "10 XP"]

        for rate in xp_rates:
            label = QLabel(rate)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        return label_container

    def _create_stats_display(self) -> QWidget:
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
