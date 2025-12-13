from .Playlist import Playlist


class Album(Playlist):
    def __init__(self):
        super().__init__()
        self._ID: int = None
        self._artist: str = None
        self._cover_image: str = None
        self._title: str = None
