import requests

BASE_URL = "http://localhost:8000"

def main():
    print("Welcome to StreamWave Client")
    print("=" * 28)

    token = None

    while True:
        print()
        print("(1) Register Account")
        print("(2) Login")
        choice = input("Select an option: ").strip()

        if choice == "1":
            print()
            print("Register Account")
            print("-" * 28)
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            full_name = input("Full name (optional): ").strip() or None
            email = input("Email (optional): ").strip() or None

            response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password, "full_name": full_name, "email": email})
            if response.status_code == 400:
                print(f"Error: {response.json()['detail']}")
                continue
            response.raise_for_status()
            print("Account created successfully! Please login with your new account.")
            continue

        elif choice == "2":
            print()
            print("Login")
            print("-" * 28)
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
            if response.status_code != 200:
                print("Login failed!")
                continue
            
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            user = requests.get(f"{BASE_URL}/users/me/", headers=headers).json()
            print(f"Logged in as {user['username']} ({user['user_type']})")
            print()

            print("Your playlists:")
            playlists_data = requests.get(f"{BASE_URL}/users/me/playlists/", headers=headers).json()
            playlists = playlists_data["playlists"]
            for pl in playlists:
                print(f"  [{pl['id']}] {pl['name']} ({len(pl['song_ids'])} items)")
            print()

            query = input("Search for music: ")
            results = requests.get(f"{BASE_URL}/media/search/{query}").json()["results"]

            if results:
                print(f"Found {len(results)} results:")
                for item in results:
                    print(f"  [{item['id']}] {item['title']} - {item.get('artist', 'Unknown')}")
            else:
                print("No results found.")
            print()

            media_id = input("Enter media ID to play: ")
            if media_id.isdigit():
                media = requests.get(f"{BASE_URL}/media/{media_id}", headers=headers).json()
                if media.get("title"):
                    print(f"Now playing: {media['title']}")
                    print(f"URL: {media['url']}")
                else:
                    print("Media not found.")

            print("Goodbye!")
            break

        else:
            print("Invalid option. Please select 1 or 2.")


if __name__ == "__main__":
    main()
