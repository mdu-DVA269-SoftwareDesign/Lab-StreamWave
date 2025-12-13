from pathlib import Path
from typing import List, Optional

from JsonDataManager import JsonDataManager
from .MediaContent import MediaContent
from .Podcast import Podcast
from .Song import Song


class MediaManager(JsonDataManager):
    def __init__(self, media_file: Optional[Path] = None):
        data_file = media_file or Path(__file__).parent / "media.json"
        super().__init__(data_file, default_data=[])

    def add_media_item(self, item: MediaContent) -> None:
        item_dict = item.model_dump(by_alias=True, exclude_none=False)
        self._db.append(item_dict)
        self._save()

    def get_media_by_id(self, media_id: int) -> Optional[MediaContent]:
        for item_dict in self._db:
            if item_dict.get("id") == media_id:
                return self._dictionary_to_media(item_dict)
        return None

    def search_media(self, query: str) -> List[MediaContent]:
        q = query.lower()
        results = []
        for item_dict in self._db:
            title_match = q in (item_dict.get("title") or "").lower()
            artist_match = q in (item_dict.get("artist") or "").lower()
            if title_match or artist_match:
                results.append(self._dictionary_to_media(item_dict))
        return results

    def get_all_media(self) -> List[MediaContent]:
        return [self._dictionary_to_media(item_dict) for item_dict in self._db]

    def get_all_songs(self) -> List[Song]:
        return [self._dictionary_to_media(item_dict) for item_dict in self._db if item_dict.get("media_type") == "Song"]

    def get_all_podcasts(self) -> List[Podcast]:
        return [self._dictionary_to_media(item_dict) for item_dict in self._db if item_dict.get("media_type") == "Podcast"]

    @staticmethod
    def _dictionary_to_media(item_dict: dict) -> MediaContent:
        media_type = item_dict.get("media_type")

        if media_type == "Song":
            return Song(**item_dict)
        if media_type == "Podcast":
            return Podcast(**item_dict)
        raise ValueError(f"Unknown media type: {media_type}")
