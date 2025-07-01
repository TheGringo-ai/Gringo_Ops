"""
ChatterFix Backend Authentication Logic
This file contains the core business logic for user authentication 
and management using Firebase Authentication.
"""

import firebase_admin
from firebase_admin import auth
from . import database
from . import models


def create_user_with_email_and_password(email, password, username, role):
    """Creates a new user in Firebase Auth and a corresponding user document in Firestore."""
    try:
        # Create user in Firebase Authentication
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=username,
            disabled=False
        )
        
        # Create user document in Firestore
        user_data = models.User(
            id=user_record.uid,
            username=username,
            email=email,
            role=role
        )
        database.set_document("users", user_record.uid, user_data.__dict__)
        
        print(f"✅ Successfully created new user: {user_record.uid}")
        return user_record
    except Exception as e:
        print(f"❌ Error creating new user: {e}")
        raise e

def sign_in_with_email_and_password(email, password):
    """
    This is a placeholder function. In a real web app, you would verify the password.
    For a Streamlit app, we can't easily and securely get a custom token from the client-side.
    So, we'll find the user by email and assume the password is correct for this demo.
    WARNING: THIS IS NOT SECURE FOR PRODUCTION.
    """
    try:
        # In a real app, you'd get an ID token from the client, verify it, and then get the user.
        # For this Streamlit example, we'll just look up the user by email.
        user = auth.get_user_by_email(email)
        # Here you would typically verify the password, but Firebase Admin SDK doesn't do that.
        # This must be handled by a client-side SDK or a custom auth flow.
        # We are proceeding with the user object as if the password was verified.
        return user
    except auth.UserNotFoundError:
        raise ValueError("User not found. Please check the email address.")
    except Exception as e:
        raise e

def get_user_from_firestore(uid: str) -> models.User | None:
    """Retrieves user details from Firestore by UID."""
    user_data = database.get_document("users", uid)
    if user_data:
        return models.User(**user_data)
    return None
