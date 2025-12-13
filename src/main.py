from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from AuthManager import (
    Token,
    authenticate_user_login,
    get_current_active_user,
)
from User import User

app = FastAPI(title="StreamWave", description="Simple audio streaming application", version="0.0.1-prealpha")

"""
The following code is based on the FastAPI Security Tutorial:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Original Author: Sebastián Ramírez (tiangolo)
License: MIT License
Copyright (c) 2018 Sebastián Ramírez

FastAPI Documentation: https://fastapi.tiangolo.com/
Repository: https://github.com/tiangolo/fastapi
"""
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return authenticate_user_login(form_data)


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/")
async def root():
    return {"message": "Welcome to StreamWave!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
