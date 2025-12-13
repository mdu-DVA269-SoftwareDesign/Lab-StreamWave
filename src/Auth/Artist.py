from .RegisteredUser import RegisteredUser
from Media.MediaManager import MediaManager
from Media.Song import Song
from Media.Podcast import Podcast
from Media.Album import Album


class Artist(RegisteredUser):
    def upload_song(self, song: Song, media_manager: MediaManager) -> Song:
        return media_manager.add(song)

    def upload_podcast(self, podcast: Podcast, media_manager: MediaManager) -> Podcast:
        return media_manager.add(podcast)

    def manage_album(self, album: Album):
        pass
