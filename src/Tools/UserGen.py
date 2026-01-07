from pwdlib import PasswordHash
import json

password_hash = PasswordHash.recommended()

username = input("Username: ")
password = input("Password: ")
full_name = input("Full Name: ")
email = input("Email: ")
user_id = int(input("User ID: "))
is_premium = input("Premium account? (y/n): ").lower() == 'y'

hashed_password = password_hash.hash(password)

user_entry = {
    username: {
        "id": user_id,
        "username": username,
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_password,
        "disabled": False,
        "is_premium": is_premium
    }
}

print(json.dumps(user_entry, indent=2))
