from pathlib import Path
from typing import Annotated, Union, Optional
import random

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from Media import MediaManager, Song, Podcast, PlaylistManager, Playlist
from Auth import FastAPIAuthManager, Token, User, RegisteredUser, Artist, Admin

app = FastAPI(title="StreamWave",
              description="Simple audio streaming application", version="0.0.1-prealpha")
media_manager = MediaManager(Path(__file__).parent / "media.json")
auth_manager = FastAPIAuthManager(Path(__file__).parent / "users.json")
playlist_manager = PlaylistManager(Path(__file__).parent / "playlists.json")

# Create the dependency functions from auth_manager instance
# to be used in route definitions below.
get_current_active_user = auth_manager.get_dependency_for("active_user")
get_artist_or_admin = auth_manager.get_dependency_for("artist_or_admin")
get_admin = auth_manager.get_dependency_for("admin")

"""
The following code is based on the FastAPI Security Tutorial:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Original Author: Sebastián Ramírez (tiangolo)
License: MIT License
Copyright (c) 2018 Sebastián Ramírez

FastAPI Documentation: https://fastapi.tiangolo.com/
Repository: https://github.com/tiangolo/fastapi
"""


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None


@app.post("/register")
async def register_user(request: RegisterRequest):
    if auth_manager.get_user(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{request.username}' already exists"
        )

    all_users = auth_manager.get_all()
    max_id = max((u.get("id", 0) for u in all_users), default=0)

    hashed_password = auth_manager.get_password_hash(request.password)
    user = RegisteredUser(
        id=max_id + 1,
        username=request.username,
        full_name=request.full_name,
        email=request.email,
        hashed_password=hashed_password,
        disabled=False,
        is_premium=False
    )

    auth_manager.add(user)
    return {"message": "User created successfully", "username": user.username}


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return auth_manager.authenticate_user_login(form_data)


@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)]):
    media_items = media_manager.get_all()
    return {"user": current_user, "media_items": media_items}


@app.get("/users/me/playlists/")
async def read_own_playlists(
        current_user: Annotated[User, Depends(get_current_active_user)]):
    playlists = playlist_manager.get_playlists_by_owner(current_user.id)
    return {"user": current_user, "playlists": playlists}


@app.get("/users/me/playlists/{playlist_id}")
async def read_playlist_by_id(
        playlist_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)]):
    playlist = playlist_manager.get_by_id(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not your playlist")
    return playlist


@app.get("/media/{media_id}")
async def get_media_stream_url(
    media_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    media = media_manager.get_by_id(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    user_playlists = playlist_manager.get_playlists_by_owner(current_user.id)
    history_playlist = None
    for pl in user_playlists:
        if pl.name == "listening_history_playlist":
            history_playlist = pl
            break

    if not history_playlist:
        all_playlists = playlist_manager.get_all()
        max_id = max((p.get("id", 0) for p in all_playlists), default=0)
        history_playlist = Playlist(
            id=max_id + 1,
            name="listening_history_playlist",
            song_ids=[],
            owner_id=current_user.id
        )
        playlist_manager.add(history_playlist)

    history_playlist.add_song(media_id)
    playlist_manager.update(history_playlist.id, {
                            "song_ids": history_playlist.song_ids})

    return {"id": media_id, "title": media.get("title"), "url": media.get("url")}


@app.get("/media/search/{query}")
async def search_media_endpoint(query: str):
    results = media_manager.search_media(query)
    return {"results": results}


@app.get("/recommendations")
async def get_recommendations(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    user_playlists = playlist_manager.get_playlists_by_owner(current_user.id)
    history_playlist = None
    for pl in user_playlists:
        if pl.name == "listening_history_playlist":
            history_playlist = pl
            break

    if not history_playlist or not history_playlist.song_ids:
        all_media = media_manager.get_all()
        if all_media:
            return random.choice(all_media)
        return {}

    genre_counts: dict[str, int] = {}
    for song_id in history_playlist.song_ids:
        media = media_manager.get_by_id(song_id)
        if media:
            genre = media.get("genre", "Unknown")
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    if not genre_counts:
        all_media = media_manager.get_all()
        if all_media:
            return random.choice(all_media)
        return {}

    max_genre = max(genre_counts.items(), key=lambda x: x[1])[0]
    all_media = media_manager.get_all()
    filtered_media = [m for m in all_media if m.get("genre") == max_genre]

    if filtered_media:
        return random.choice(filtered_media)

    return {}


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
