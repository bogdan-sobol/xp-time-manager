# user_model.py
import math
from ..utils.logger import setup_logger

class UserModel:
    def __init__(self, database):
        self.db = database
        self.logger = setup_logger()
        
        self.current_user_id = None
        self.current_user_xp = None
        self.current_user_level = None

        self.initialize_user()


    def initialize_user(self):
        """Initializes default user and returns current user ID"""
        self.current_user_id = self.db.initialize_default_user()

        if self.current_user_id == -1:
            self.logger.error("Failed to initialize default user")
            raise RuntimeError("Failed to initialize default user")
        
        self.logger.info(f"Initialized user with ID: {self.current_user_id}")
        # Update user's statistic
        self.update_user_stats()
        self.logger.info(f"Current user's level: {self.current_user_level}")
        self.logger.info(f"Current user's XP: {self.current_user_xp}")


    def update_user_level(self) -> int:
        """Gets current user's level from the users table in database"""
        return self.db.get_user_level(self.current_user_id)


    def update_user_xp(self) -> float:
        """Gets current user's XP from the users table in database"""
        return self.db.get_user_xp(self.current_user_id)


    def update_user_stats(self):
        """
        Gets user's XP and level from database
        Assigns them to the user_model variables
        """
        self.current_user_xp = self.update_user_xp()
        self.current_user_level = self.update_user_level()


    def set_user_xp(self, new_xp_amount: float, user_id: int = 1) -> None:
        self.db.set_user_xp(new_xp_amount, user_id)
        self.current_user_xp = new_xp_amount


    def set_user_level(self, level: int, user_id: int = 1) -> None:
        self.db.set_user_level(level, user_id)
        self.current_user_level = level


    def reevaluate_user_xp(self) -> float:
        """
        Summorizes earned XP from xp_transactions table of current user
        Returns the result
        """
        total_xp = self.db.get_total_xp(self.current_user_id)
        return total_xp


    def reevaluate_user_stats(self):
        """
        Reevaluates user statiscic
        via summorizing xp from the xp_transactions table
        and calculating user level based on it
        Updates users table with this information
        """
        self.logger.info("Reevaluating user's statistic...")
        self.logger.debug(f"Previous user's level: {self.current_user_level}")
        self.logger.debug(f"Previous user's XP: {self.current_user_xp} XP")
        # Summorizes xp amounts from the xp_transactions table for current user
        self.current_user_xp = self.reevaluate_user_xp()
        # Updates users table with the new XP value
        self.set_user_xp(self.current_user_xp, self.current_user_id)
        # Calculates new level based on new XP
        self.current_user_level = self.evaluate_level(self.current_user_xp)
        # Also update database with the new level value
        self.set_user_level(self.current_user_level, self.current_user_id)

        self.logger.info("Finished statistic's reevaluation")
        self.logger.debug(f"New user's level: {self.current_user_level}")
        self.logger.debug(f"New user's XP: {self.current_user_xp} XP")


    @staticmethod
    def evaluate_level(total_xp) -> int:
        """Evaluates level based on total XP amount and returns it"""
        if total_xp == None:
            return 0
        
        if total_xp <= 0:
            return 0

        if total_xp <= 352:
            lvl = math.sqrt(total_xp + 9) - 3
        elif total_xp <= 1507:
            lvl = 81 / 10 + math.sqrt(2 / 5 * (total_xp - 7839 / 40))
        else:
            lvl = 325 / 18 + math.sqrt(2 / 9 * (total_xp - 54215 / 72))

        return int(lvl)


    @staticmethod
    def calculate_xp_leftover(user_level: int) -> int:
        """
        Calculates how much XP is needed to advance to the next level.
        Returns amount of XP needed to reach the next level
        Returns 0 if user_level is None
            
        Examples:
            Level 0 -> returns 7 (need 7 XP to reach level 1 from level 0)
            Level 1 -> returns 9 (need 9 XP to reach level 2 from level 1)
            Level 2 -> returns 11 (need 11 XP to reach level 3 from level 2)
        """
        if user_level == None:
            return 0
        
        # Formulas are taken from:
        # https://minecraft.fandom.com/wiki/Experience
        if user_level <= 15:
            xp_lefover = 2 * user_level + 7
        elif user_level <= 30:
            xp_lefover = 5 * user_level - 38
        else:
            xp_lefover = 9 * user_level - 158
        
        # Unlike user XP, XP leftover is an integer, not a float
        return int(xp_lefover)


    @staticmethod
    def calculate_xp_collected(user_level: int) -> int:
        """
        Calculates how much experience has been collected to reach a level
        """
        # Formulas are taken from:
        # https://minecraft.fandom.com/wiki/Experience
        if user_level <= 16:
            xp = user_level ** 2 + 6 * user_level
        elif user_level <= 31:
            xp = 2.5 * user_level ** 2 - 40.5 * user_level + 360
        else:
            xp = 4.5 * user_level ** 2 - 162.5 * user_level + 2220
        return int(xp)


    def calculate_xp_to_next_level(self, user_level: int) -> int:
        """
        Calculates how much XP is need to progress to the next level
        """
        # Works according to functions of XP calculations in Minecraft
        # Converts level to exact XP amount needed to reach it
        xp_collected = self.calculate_xp_collected(user_level)
        # Calculates how much XP is needed to reach the next level
        xp_to_next_level = self.calculate_xp_leftover(user_level)
        # Gives total XP amount needed to have the next level
        return int(xp_collected + xp_to_next_level)