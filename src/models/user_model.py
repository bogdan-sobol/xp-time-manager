# user_model.py
import math
from ..utils.logger import setup_logger

class UserModel:
    def __init__(self, database):
        self.db = database
        self.logger = setup_logger()
        
        self.current_user_id = None
        self.current_user_lvl = None
        self.current_user_xp = None

        self.initialize_user()


    def initialize_user(self):
        """Initialize default user and return current user ID"""
        self.current_user_id = self.db.initialize_default_user()
        if self.current_user_id == -1:
            self.logger.error("Failed to initialize user")
            raise RuntimeError("Failed to initialize user")
        self.logger.info(f"Initialized user with ID: {self.current_user_id}")

        # Update user's statistic
        self.update_user_stats()
        self.logger.info(f"Current user's level: {self.current_user_lvl}")
        self.logger.info(f"Current user's XP: {self.current_user_xp}")


    def update_user_lvl(self) -> int:
        """Get current user's level"""
        return self.db.get_user_level(self.current_user_id)


    def update_user_xp(self) -> int:
        """Get current user XP"""
        return self.db.get_user_xp(self.current_user_id)


    def update_user_stats(self):
        """Gets user's XP and level and assigns them to the variables"""
        self.current_user_xp = self.update_user_xp()
        self.current_user_lvl = self.update_user_lvl()


    def set_user_xp(self, new_xp_amount: float, user_id: int = 1) -> None:
        self.db.set_user_xp(new_xp_amount, user_id)
        self.current_user_xp = new_xp_amount


    def set_user_lvl(self, lvl: int, user_id: int = 1) -> None:
        self.db.set_user_lvl(lvl, user_id)
        self.current_user_lvl = lvl


    def reevaluate_user_xp(self):
        """
        Summorizes all xp transactions of one user
        Sets this xp value to users table
        """
        self.logger.debug("Reevaluating user XP by summorizing all XP transactions")
        total_xp = self.db.get_total_xp(self.current_user_id)
        self.logger.debug(f"Reevaluated XP = {total_xp}")
        if total_xp == None:
            total_xp = 0
        # Set this value to users table
        self.set_user_xp(total_xp, self.current_user_id)
        # Update the variable with the same value
        self.current_user_xp = total_xp


    def reevaluate_user_stats(self):
        """
        Reevaluates user statiscic
        via summorizing xp transactions
        and calculating user level based on it
        """
        # Updates current_user_xp variable
        self.reevaluate_user_xp()

        # Calculate level based on new XP
        self.current_user_lvl = self.evaluate_level(self.current_user_xp)


    def evaluate_level(self, total_xp) -> int:
        """Evaluates level based on total XP amount and returns it"""
        if total_xp == None:
            return 0
        
        if total_xp <= 0:
            return 0
        
        lvl = None
        if total_xp <= 352:
            lvl = math.sqrt(total_xp + 9) - 3
        elif total_xp <= 1507:
            lvl = 81 / 10 + math.sqrt(2 / 5 * (total_xp - 7839 / 40))
        else:
            lvl = 325 / 18 + math.sqrt(2 / 9 * (total_xp - 54215 / 72))

        return int(lvl)


    def calculate_xp_leftover(self, user_lvl: int) -> int:
        """Calculate and return how much XP is left to the next level"""
        if user_lvl <= 15:
            return 2 * user_lvl + 7
        elif user_lvl <= 30:
            return 5 * user_lvl - 38
        else:
            return 9 * user_lvl - 158


    def calculate_total_xp_to_next_lvl(self, user_xp: int, xp_leftover: int) -> int:
        """Calculates total XP needed for the next level"""
        return int(user_xp + xp_leftover)

    
