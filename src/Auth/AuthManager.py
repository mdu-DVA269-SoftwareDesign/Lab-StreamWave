from datetime import datetime, timedelta, timezone
from typing import Optional
from pathlib import Path

import jwt
from pwdlib import PasswordHash
from pydantic import BaseModel

from JsonDataManager import JsonDataManager
from .RegisteredUser import RegisteredUser
from .User import User
from .Artist import Artist
from .Admin import Admin

# to get a string like this run:
# openssl rand -hex 32
DEFAULT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
DEFAULT_ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class AuthManager(JsonDataManager):
    def __init__(
        self,
        users_file: Optional[Path] = None,
        secret_key: str = DEFAULT_SECRET_KEY,
        algorithm: str = DEFAULT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        data_file = users_file or Path(__file__).parent / "users.json"
        super().__init__(data_file, default_data=[], id_field="id")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.password_hash = PasswordHash.recommended()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.password_hash.hash(password)
    
    @staticmethod
    def _dictionary_to_user(user_dict: dict) -> User:
        user_type = user_dict.get("user_type", "RegisteredUser")
        
        if user_type == "RegisteredUser":
            return RegisteredUser(**user_dict)
        elif user_type == "Artist":
            return Artist(**user_dict)
        elif user_type == "Admin":
            return Admin(**user_dict)
        else:
            return RegisteredUser(**user_dict)
    
    def get_user(self, username: str) -> Optional[User]:
        for user_dict in self.get_all():
            if user_dict.get("username") == username:
                return self._dictionary_to_user(user_dict)
        return None
    
    def authenticate_user(self, username: str, password: str) -> User | bool:
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
    
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
