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
    item_dict = item.model_dump(by_alias=True, exclude_none=False)
    
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
        return Song(**item_dict)
    elif media_type == "Podcast":
        return Podcast(**item_dict)
    else:
        raise ValueError(f"Unknown media type: {media_type}")