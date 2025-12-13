from pydantic import Field
from User import User


class RegisteredUser(User):
    hashed_password: str = Field(..., description="A hash of the password")
    is_premium: bool = Field(default=False, description="True if account is premium")

    def upgrade_to_premium(self):
        self.is_premium = True
