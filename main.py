from PyQt6.QtWidgets import QApplication

from src.views.main_window import ApplicationWindow
from src.models.database import Database
from src.models.user_model import UserModel
from src.models.time_tracking_model import TimeTrackingModel
from src.models.user_stats_model import UserStatsModel
from src.controllers.time_tracking_controller import TimeTrackingController
from src.controllers.user_stats_controller import UserStatsController
from src.views.debug_window import DebugWindow
from src.utils.constants import DEBUG_MODE


def initialize_models(database: Database) -> tuple:
    user_model = UserModel(database)
    time_tracking_model = TimeTrackingModel(database, user_model)
    user_stats_model = UserStatsModel(database, user_model)
    return time_tracking_model, user_stats_model


def initialize_controllers(
    app_window: ApplicationWindow,
    time_tracking_model: TimeTrackingModel,
    user_stats_model: UserStatsModel,
) -> tuple:
    time_tracking_controller = TimeTrackingController(app_window, time_tracking_model)
    user_stats_controller = UserStatsController(app_window, user_stats_model)
    return time_tracking_controller, user_stats_controller


def run_debug_window(time_tracking_model):
    debug_window = DebugWindow()
    debug_window.initialize_model_access(time_tracking_model)
    debug_window.initUI()
    debug_window.show()


def main():
    # Initialize application and database
    app = QApplication([])
    database = Database()

    # Create main window
    app_window = ApplicationWindow()

    # Initialize models and controllers
    time_tracking_model, user_stats_model = initialize_models(database)
    time_tracking_controller, user_stats_controller = initialize_controllers(
        app_window, time_tracking_model, user_stats_model
    )

    # Setup main window
    app_window.register_controllers(time_tracking_controller, user_stats_controller)
    app_window.initUI()

    app_window.show()

    if DEBUG_MODE:
        run_debug_window(time_tracking_model)

    app.exec()


if __name__ == "__main__":
    main()
