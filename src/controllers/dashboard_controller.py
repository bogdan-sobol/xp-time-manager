# dashboard_contoller.py
# coordinates between main_window.py and dashboard_model.py

class DashboardController:
    def __init__(self, main_window, dashboard_model):
        self.main_window = main_window
        self.dashboard_model = dashboard_model


    def update_user_level(self):
        """Updates user's level in GUI"""
        user_level = self.dashboard_model.user_model.current_user_level
        self.main_window.dashboard_view.update_user_level(user_level)


    def update_user_xp(self):
        """Updates user's XP and XP leftover in GUI"""
        user_xp = self.dashboard_model.user_model.current_user_xp
        user_level = self.dashboard_model.user_model.current_user_level

        total_xp_needed = self.dashboard_model.user_model.calculate_xp_to_next_level(user_level)

        self.main_window.dashboard_view.update_user_xp(user_xp, total_xp_needed)


    def update_user_stats(self):
        """Updates level and XP in dashboard GUI"""
        self.update_user_level()
        self.update_user_xp()