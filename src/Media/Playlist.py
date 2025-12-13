from typing import List
from MediaContent import MediaContent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Song import Song


class Playlist:
    def __init__(self):
        self._ID: int = None
        self._name: str = None
        self._songs: List[MediaContent] = None

    def add_song(self, song: 'Song'):
        pass

    def remove_song(self, song: 'Song'):
        pass

    def get_songs(self) -> List[MediaContent]:
        return None
