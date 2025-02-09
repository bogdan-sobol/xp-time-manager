# user_stats_contoller.py

class UserStatsController:
    def __init__(self, app_window, user_stats_model):
        self.app_window = app_window
        self.user_stats_model = user_stats_model


    def update_user_level(self):
        """Updates user's level in GUI"""
        user_level = self.user_stats_model.user_model.current_user_level
        self.app_window.user_stats_panel.update_user_level(user_level)


    def update_user_xp(self):
        """Updates user's XP and XP leftover in GUI"""
        user_xp = self.user_stats_model.user_model.current_user_xp
        user_level = self.user_stats_model.user_model.current_user_level

        total_xp_needed = self.user_stats_model.user_model.calculate_xp_to_next_level(user_level)

        self.app_window.user_stats_panel.update_user_xp(user_xp, total_xp_needed)


    def refresh_user_statistics(self):
        """Updates level and XP in dashboard GUI"""
        self.update_user_level()
        self.update_user_xp()