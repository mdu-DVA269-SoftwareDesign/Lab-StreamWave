from pydantic import BaseModel, Field

class User(BaseModel):
    ID: int | None = Field(default=None, description="The ID of the User")
    username: str = Field(..., description="The username used during login")
    full_name: str | None = Field(default=None, description="The full display name")
    email: str | None = Field(default=None, description="The email address")
    disabled: bool = Field(default=False, description="The account disabled status")