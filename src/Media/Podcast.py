from .MediaContent import MediaContent
from typing import Optional


class Podcast(MediaContent):
    episode: Optional[int] = None
