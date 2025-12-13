from .MediaContent import MediaContent


class Podcast(MediaContent):
    def __init__(self):
        super().__init__()
        self._episode: int = None
