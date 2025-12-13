from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import json
from pathlib import Path
from .MediaContent import MediaContent
from .Song import Song
from .Podcast import Podcast
 
def load_media_db():
    media_file = Path(__file__).parent / "media.json"
    if not media_file.exists():
        with open(media_file, "w") as f:
            json.dump([], f)
        return []
    with open(media_file, "r") as f:
        return json.load(f)

fake_media_db = load_media_db()

def add_media_item(item: MediaContent):
    item_dict = {
        "id": item._ID,
        "title": item._title,
        "url": item._url,
        "length": item._length,
        "genre": item._genre,
        "cover_image": item._cover_image,
        "artist": item._artist,
        "media_type": item.__class__.__name__,
    }
    
    if isinstance(item, Podcast):
        item_dict["episode"] = item._episode
    
    fake_media_db.append(item_dict)
    with open(Path(__file__).parent / "media.json", "w") as f:
        json.dump(fake_media_db, f, indent=4)

def get_media_by_id(media_id: int) -> MediaContent:
    for item_dict in fake_media_db:
        if item_dict.get("id") == media_id:
            return dictionary_to_media(item_dict)
    return None

def search_media(query: str) -> List[MediaContent]:
    results = []
    for item_dict in fake_media_db:
        if query.lower() in item_dict.get("title", "").lower() or query.lower() in item_dict.get("artist", "").lower():
            results.append(dictionary_to_media(item_dict))
    return results

def get_all_media() -> List[MediaContent]:
    return [dictionary_to_media(item_dict) for item_dict in fake_media_db]

def get_all_songs() -> List[Song]:
    return [dictionary_to_media(item_dict) for item_dict in fake_media_db if item_dict.get("media_type") == "Song"]

def get_all_podcasts() -> List[Podcast]:
    return [dictionary_to_media(item_dict) for item_dict in fake_media_db if item_dict.get("media_type") == "Podcast"]

def dictionary_to_media(item_dict: dict) -> MediaContent:
    media_type = item_dict.get("media_type")
    
    if media_type == "Song":
        media = Song()
    elif media_type == "Podcast":
        media = Podcast()
        media._episode = item_dict.get("episode")
    else:
        raise ValueError(f"Unknown media type: {media_type}")
    
    media._ID = item_dict.get("id")
    media._title = item_dict.get("title")
    media._url = item_dict.get("url")
    media._length = item_dict.get("length")
    media._genre = item_dict.get("genre")
    media._cover_image = item_dict.get("cover_image")
    media._artist = item_dict.get("artist")
    
    return media