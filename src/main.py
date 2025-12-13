from pathlib import Path
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from Media.MediaManager import MediaManager
from Media.Song import Song
from Media.Podcast import Podcast

from Auth.AuthManager import AuthManager, Token
from Auth.User import User
from Auth.RegisteredUser import RegisteredUser
from Auth.Artist import Artist
from Auth.Admin import Admin
from Media.PlaylistManager import PlaylistManager

app = FastAPI(title="StreamWave", description="Simple audio streaming application", version="0.0.1-prealpha")
media_manager = MediaManager(Path(__file__).parent / "media.json")
auth_manager = AuthManager(Path(__file__).parent / "users.json")
playlist_manager = PlaylistManager(Path(__file__).parent / "playlists.json")

# Create the dependency functions from auth_manager instance
# to be used in route definitions below.
get_current_active_user = auth_manager.get_current_active_user_dependency()
get_artist_or_admin = auth_manager.get_artist_or_admin_dependency()
get_admin = auth_manager.get_admin_dependency()

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
    return auth_manager.authenticate_user_login(form_data)


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    media_items = media_manager.get_all()
    return {"user": current_user, "media_items": media_items}


@app.get("/users/me/playlists/")
async def read_own_playlists(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    playlists = playlist_manager.get_playlists_by_owner(current_user.ID)
    return {"user": current_user, "playlists": playlists}


@app.get("/users/me/playlists/{playlist_id}")
async def read_playlist_by_id(
    playlist_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    playlist = playlist_manager.get_by_id(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.get("owner_id") != current_user.ID:
        raise HTTPException(status_code=403, detail="Not your playlist")
    return playlist


@app.get("/media/{media_id}")
async def get_media_stream_url(media_id: int):
    media = media_manager.get_by_id(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"id": media_id, "title": media.get("title"), "url": media.get("url")}


@app.get("/media/search/{query}")
async def search_media_endpoint(query: str):
    results = media_manager.search_media(query)
    return {"results": results}

@app.post("/media/add_item/")
async def add_media_item_endpoint(
    item: Union[Song, Podcast],
    current_user: Annotated[User, Depends(get_artist_or_admin)]
):
    media_manager.add(item)
    return {"message": "Media item added successfully", "media_type": item.media_type, "added_by": current_user.username}


@app.post("/admin/users/")
async def create_user_endpoint(
    user: Union[RegisteredUser, Artist, Admin],
    password: str,
    current_user: Annotated[User, Depends(get_admin)]
):
    if auth_manager.get_user(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' already exists"
        )
    user.hashed_password = auth_manager.get_password_hash(password)
    
    auth_manager.add(user)
    return {"message": "User created successfully", "username": user.username, "user_type": user.user_type}

@app.get("/")
async def root():
    return {"message": "Welcome to StreamWave!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
