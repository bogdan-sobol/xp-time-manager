from ..utils.logger import setup_logger


class UserStatsModel:
    def __init__(self, database, user_model):
        self.db = database
        self.user_model = user_model

        self.currently_selected_activity_item = None

        self.logger = setup_logger()

    # User Stats Management

    def get_user_level(self) -> int:
        return self.user_model.current_user_lvl

    def get_user_xp(self) -> int:
        return self.user_model.current_user_xp

    # Activity Management

    def get_user_activities(self):
        activities = self.user_model.get_user_activities()

        if not activities:
            return None

        return activities

    def add_new_activity(self, activity_name) -> bool:
        """
        Validates activity name
        Adds activity via database.py
        Returns False if invalid activity name
        or an error occured while adding activity to database
        """
        if not isinstance(activity_name, str):
            try:
                activity_name = str(activity_name)
            except:
                self.logger.error(
                    (
                        "Passed value for creating new activity is"
                        " not a string and can't be converted"
                    )
                )
                return False

        activity_name = activity_name.strip()
        if not activity_name:
            return False

        user_id = self.user_model.current_user_id
        if self.db.add_new_activity(activity_name, user_id):
            self.logger.info(f"Added new activity: {activity_name}")
            return True

        return False

    def delete_user_activity(self, activity_id: int) -> None:
        self.user_model.delete_user_activity(activity_id)

    def set_user_xp_rate_mob(self, mob: str):
        self.logger.info(f"XP rate mob is set to: {mob}")
        self.user_model.set_user_xp_rate_mob(mob)
