"""
FastAPI OAuth2 Authentication Manager

This code is based on the FastAPI Security Tutorial:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Original Author: Sebastián Ramírez (tiangolo)
License: MIT License
Copyright (c) 2018 Sebastián Ramírez

FastAPI Documentation: https://fastapi.tiangolo.com/
Repository: https://github.com/tiangolo/fastapi
"""

from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from .AuthManager import AuthManager, Token, TokenData
from .User import User
from .Artist import Artist
from .Admin import Admin


class FastAPIAuthManager(AuthManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    # otherwise first argument "self" would be required in the FastAPI dependency call.
    def get_dependency_for(self, selected_dependency: str):
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

        async def get_current_active_user(
            current_user: Annotated[User, Depends(get_current_user)],
        ):
            if current_user.disabled:
                raise HTTPException(status_code=400, detail="Inactive user")
            return current_user

        async def get_artist_or_admin(
            current_user: Annotated[User, Depends(get_current_active_user)],
        ):
            if not isinstance(current_user, (Artist, Admin)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You dont have enough privileges.",
                )
            return current_user

        async def get_admin(
            current_user: Annotated[User, Depends(get_current_active_user)],
        ):
            if not isinstance(current_user, Admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required.",
                )
            return current_user

        dependencies = {
            "current_user": get_current_user,
            "active_user": get_current_active_user,
            "artist_or_admin": get_artist_or_admin,
            "admin": get_admin,
        }

        if selected_dependency not in dependencies:
            raise ValueError(
                f"Unknown dependency: '{selected_dependency}'. "
                f"Available options: {list(dependencies.keys())}"
            )

        return dependencies[selected_dependency]
