from abc import ABC


class MediaContent(ABC):
    def __init__(self):
        self._ID: int = None
        self._title: str = None
        self._url: str = None
        self._length: int = None
        self._genre: str = None
        self._cover_image: str = None
        self._artist: str = None
