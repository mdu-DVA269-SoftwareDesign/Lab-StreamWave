from typing import List
from pydantic import BaseModel, Field


class Playlist(BaseModel):
    id: int = Field(..., description="The playlist ID")
    name: str = Field(..., description="The name of the playlist")
    song_ids: List[int] = Field(
        default_factory=list, description="List of song IDs in the playlist")
    owner_id: int = Field(...,
                          description="The ID of the user who owns this playlist")

    def add_song(self, song_id: int) -> None:
        if song_id not in self.song_ids:
            self.song_ids.append(song_id)

    def remove_song(self, song_id: int) -> None:
        if song_id in self.song_ids:
            self.song_ids.remove(song_id)
