from .RegisteredUser import RegisteredUser
from .User import User


class Admin(RegisteredUser):
    def add_user(self, user: RegisteredUser, auth_manager) -> RegisteredUser:
        return auth_manager.add(user)
    
    def delete_user(self, user_id: int, auth_manager) -> bool:
        return auth_manager.delete(user_id)

    def update_user(self, user_id: int, data: dict, auth_manager) -> User | None:
        return auth_manager.update(user_id, data)

    def disable_user(self, user_id: int, auth_manager) -> User | None:
        return auth_manager.update(user_id, {"disabled": True})

    def enable_user(self, user_id: int, auth_manager) -> User | None:
        return auth_manager.update(user_id, {"disabled": False})

    def delete_media(self, media_id: int, media_manager) -> bool:
        return media_manager.delete(media_id)

    def set_user_premium(self, user_id: int, is_premium: bool, auth_manager) -> User | None:
        return auth_manager.update(user_id, {"is_premium": is_premium})
