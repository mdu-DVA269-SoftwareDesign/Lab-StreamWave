"""
OAuth2 Authentication Manager

This code is based on the FastAPI Security Tutorial:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Original Author: Sebastián Ramírez (tiangolo)
License: MIT License
Copyright (c) 2018 Sebastián Ramírez

FastAPI Documentation: https://fastapi.tiangolo.com/
Repository: https://github.com/tiangolo/fastapi
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
import json
from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from .RegisteredUser import RegisteredUser
from .User import User
from .Artist import Artist
from .Admin import Admin


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class AuthManager:
    # to get a string like this run:
    # openssl rand -hex 32
    DEFAULT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    DEFAULT_ALGORITHM = "HS256"
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def __init__(
        self,
        users_file: Optional[Path] = None,
        secret_key: str = DEFAULT_SECRET_KEY,
        algorithm: str = DEFAULT_ALGORITHM,
        access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        self.users_file = users_file or Path(__file__).parent / "users.json"
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.password_hash = PasswordHash.recommended()
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self._db = self._load()
    
    def _load(self) -> dict:
        with open(self.users_file, "r") as f:
            return json.load(f)
    
    def _save(self) -> None:
        with open(self.users_file, "w") as f:
            json.dump(self._db, f, indent=4)
    
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
        if username in self._db:
            user_dict = self._db[username]
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
    
    def authenticate_user_login(self, form_data: OAuth2PasswordRequestForm) -> Token:
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    # We use closures here to capture self in the dependency functions,
    # otherwise first argument self would be required in the FastAPI dependency call.
    def get_current_user_dependency(self):
        async def get_current_user(token: Annotated[str, Depends(self.oauth2_scheme)]):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                username = payload.get("sub")
                if username is None:
                    raise credentials_exception
                token_data = TokenData(username=username)
            except InvalidTokenError:
                raise credentials_exception
            user = self.get_user(username=token_data.username)
            if user is None:
                raise credentials_exception
            return user
        return get_current_user
    
    def get_current_active_user_dependency(self):
        get_current_user = self.get_current_user_dependency()
        
        async def get_current_active_user(
            current_user: Annotated[User, Depends(get_current_user)],
        ):
            if current_user.disabled:
                raise HTTPException(status_code=400, detail="Inactive user")
            return current_user
        return get_current_active_user
    
    def get_artist_or_admin_dependency(self):
        get_current_active_user = self.get_current_active_user_dependency()
        
        async def get_artist_or_admin(
            current_user: Annotated[User, Depends(get_current_active_user)],
        ):
            if not isinstance(current_user, (Artist, Admin)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You dont have enough privileges.",
                )
            return current_user
        return get_artist_or_admin
