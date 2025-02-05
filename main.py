from PyQt6.QtWidgets import QApplication
from src.models.database import Database
from src.views.main_window import MainWindow
from src.models.user_model import UserModel
from src.models.timer_model import TimerModel
from src.models.dashboard_model import DashboardModel
from src.controllers.timer_controller import TimerController
from src.controllers.dashboard_controller import DashboardController

def initialize_models(database: Database):
    """
    Initialize all models.
    
    Args:
        database: Database instance used by all models
        
    Returns:
        tuple: Contains initialized TimerModel and DashboardModel instances
    """
    user_model = UserModel(database)
    timer_model = TimerModel(database, user_model)
    dashboard_model = DashboardModel(database, user_model)
    return timer_model, dashboard_model


def initialize_controllers(main_window: MainWindow, 
                         timer_model: TimerModel,
                         dashboard_model: DashboardModel):
    """Initializes all controllers"""
    timer_controller = TimerController(main_window, timer_model)
    dashboard_controller = DashboardController(main_window, dashboard_model)
    return timer_controller, dashboard_controller


def main():
    # Initialize application and database
    app = QApplication([])
    database = Database()

    # Create main window
    main_window = MainWindow()

    # Initialize models and controllers
    timer_model, dashboard_model = initialize_models(database)
    timer_controller, dashboard_controller = initialize_controllers(
        main_window,
        timer_model,
        dashboard_model
    )

    # Setup main window
    main_window.initialize_controllers(timer_controller, dashboard_controller)
    main_window.initUI()
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()