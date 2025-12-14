from pathlib import Path

from Auth import AuthManager
from Media import MediaManager, PlaylistManager

def main():
    base_path = Path(__file__).parent
    auth_manager = AuthManager(base_path / "users.json")
    media_manager = MediaManager(base_path / "media.json")
    playlist_manager = PlaylistManager(base_path / "playlists.json")

    print("Welcome to StreamWave Client")
    print("=" * 28)

    username = input("Username: ")
    password = input("Password: ")
    
    user = auth_manager.authenticate_user(username, password)
    
    if not user:
        print("Login failed!")
        return
    
    print(f"Logged in as {user.username} ({user.user_type})")
    print()

    print("Your playlists:")
    playlists = playlist_manager.get_playlists_by_owner(user.ID)
    for pl in playlists:
        print(f"  [{pl.ID}] {pl.name} ({len(pl.song_ids)} items)")
    print()

    query = input("Search for music: ")
    results = media_manager.search_media(query)
    
    if results:
        print(f"Found {len(results)} results:")
        for item in results:
            print(f"  [{item.id}] {item.title} - {item.artist or 'Unknown'}")
    else:
        print("No results found.")
    print()

    media_id = input("Enter media ID to play: ")
    if media_id.isdigit():
        media = media_manager.get_by_id(int(media_id))
        if media:
            print(f"Now playing: {media['title']}")
            print(f"URL: {media['url']}")
        else:
            print("Media not found.")

    print("Goodbye!")


if __name__ == "__main__":
    main()
