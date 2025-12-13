from .RegisteredUser import RegisteredUser


class Admin(RegisteredUser):
    def manage_users(self):
        pass

    def manage_content(self):
        pass

    def configure_tiers(self):
        pass
