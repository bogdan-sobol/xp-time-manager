# dashboard_contoller.py
# coordinates between main_window.py and dashboard_model.py

class DashboardController:
    def __init__(self, main_window, dashboard_model):
        self.main_window = main_window
        self.dashboard_model = dashboard_model
        self.update_timer = None


    def update_user_lvl(self):
        user_lvl = self.dashboard_model.user_model.current_user_lvl
        self.main_window.dashboard_view.update_user_lvl(user_lvl)


    def update_user_xp(self):
        user_xp = self.dashboard_model.user_model.current_user_xp
        user_lvl = self.dashboard_model.user_model.current_user_lvl
        xp_leftover = self.dashboard_model.user_model.calculate_xp_leftover(user_lvl)
        total_xp_need = self.dashboard_model.user_model.calculate_total_xp_to_next_lvl(user_xp, xp_leftover)
        self.main_window.dashboard_view.update_user_xp(user_xp, total_xp_need)


    def update_user_stats(self):
        self.update_user_lvl()
        self.update_user_xp()