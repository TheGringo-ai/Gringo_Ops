"""
ChatterFix Backend User Management Logic
This file contains the core business logic for creating, managing, and authenticating users.
"""
import bcrypt
from . import database
from . import models

def get_all_users() -> list[models.User]:
    """Retrieves all users from the database."""
    all_docs = database.get_collection("users")
    # Don't expose password hashes
    for doc in all_docs:
        doc.pop('password_hash', None)
    return [models.User(**doc) for doc in all_docs]

def get_user_by_id(user_id: str) -> models.User | None:
    """Retrieves a single user by their ID."""
    data = database.get_document("users", user_id)
    if data:
        # The password_hash should not be sent to the frontend
        data.pop('password_hash', None)
        return models.User(**data)
    return None

def get_user_by_username(username: str) -> dict | None:
    """Retrieves a user by their username. Returns the full document including hash for verification."""
    users = database.get_collection_where("users", "username", "==", username)
    return users[0] if users else None

def create_user(username: str, password: str, role: str, email: str) -> str:
    """Creates a new user with a securely hashed password."""
    if get_user_by_username(username):
        raise ValueError("Username already exists.")

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user_data = {
        "username": username,
        "password_hash": hashed_password.decode('utf-8'), # Store hash as a string
        "role": role,
        "email": email,
    }

    doc_id = database.add_document("users", new_user_data)
    database.update_document("users", doc_id, {"id": doc_id})
    print(f"✅ Created user: {username} ({doc_id})")
    return doc_id

def verify_user(username: str, password: str) -> models.User | None:
    """Verifies a user's password against the stored hash."""
    user_data = get_user_by_username(username)
    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
        # Password matches, return user model (without the hash)
        user_data.pop('password_hash', None)
        return models.User(**user_data)
    # Invalid username or password
    return None

def update_user(user_id: str, updates: dict) -> None:
    """Updates user details. For security, this function cannot update the password."""
    # Ensure password is not updated directly through this function for security
    updates.pop('password', None)
    updates.pop('password_hash', None)
    database.update_document("users", user_id, updates)
    print(f"✅ Updated user {user_id}")

def delete_user(user_id: str) -> None:
    """Deletes a user from the database."""
    database.delete_document("users", user_id)
    print(f"✅ Deleted user {user_id}")
