from pathlib import Path
from typing import List, Optional

from JsonDataManager import JsonDataManager
from .Playlist import Playlist


class PlaylistManager(JsonDataManager):
    def __init__(self, playlist_file: Optional[Path] = None):
        data_file = playlist_file or Path(__file__).parent / "playlists.json"
        super().__init__(data_file, default_data=[], id_field="ID")

    def get_playlists_by_owner(self, owner_id: int) -> List[Playlist]:
        return [
            Playlist(**item_dict) 
            for item_dict in self.get_all() 
            if item_dict.get("owner_id") == owner_id
        ]

    def search_playlists(self, query: str) -> List[Playlist]:
        q = query.lower()
        return [
            Playlist(**item_dict)
            for item_dict in self.get_all()
            if q in (item_dict.get("name") or "").lower()
        ]
