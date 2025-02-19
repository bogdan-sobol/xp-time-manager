from PyQt6.QtWidgets import QApplication

from src.views.main_window import ApplicationWindow
from src.models.database import Database
from src.models.user_model import UserModel
from src.models.activity_timer_model import ActivityTimerModel
from src.models.user_stats_model import UserStatsModel
from src.controllers.activity_timer_controller import ActivityTimerController
from src.controllers.user_stats_controller import UserStatsController
from src.views.debug_window import DebugWindow
from src.utils.constants import DEBUG_MODE


def initialize_models(database: Database) -> tuple:
    """
    Initialize all models.
    Returns tuple with ActivityTimerModel and UserStatsModel instances
    """
    user_model = UserModel(database)
    activity_timer_model = ActivityTimerModel(database, user_model)
    user_stats_model = UserStatsModel(database, user_model)
    return activity_timer_model, user_stats_model


def initialize_controllers(
    app_window: ApplicationWindow,
    activity_timer_model: ActivityTimerModel,
    user_stats_model: UserStatsModel,
) -> tuple:
    """
    Initializes all controllers
    Returns activity timer controller and user stats controller
    """
    activity_timer_controller = ActivityTimerController(
        app_window, activity_timer_model
    )
    user_stats_controller = UserStatsController(app_window, user_stats_model)
    return activity_timer_controller, user_stats_controller


def main():
    # Initialize application and database
    app = QApplication([])
    database = Database()

    # Create main window
    app_window = ApplicationWindow()

    # Initialize models and controllers
    activity_timer_model, user_stats_model = initialize_models(database)
    activity_timer_controller, user_stats_controller = initialize_controllers(
        app_window, activity_timer_model, user_stats_model
    )

    # Setup main window
    app_window.register_controllers(activity_timer_controller, user_stats_controller)
    app_window.initUI()
    app_window.show()

    if DEBUG_MODE:
        debug_window = DebugWindow()
        debug_window.initialize_model_access(activity_timer_model)
        debug_window.initUI()
        debug_window.show()

    app.exec()


if __name__ == "__main__":
    main()
