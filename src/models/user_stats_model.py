# dashboard_model.py

from ..utils.logger import setup_logger

class UserStatsModel:
    def __init__(self, database, user_model):
        self.db = database
        self.user_model = user_model
        self.logger = setup_logger()


    def get_user_level(self) -> int:
        return self.user_model.current_user_lvl


    def get_user_xp(self) -> int:
        return self.user_model.current_user_xp
    
    


