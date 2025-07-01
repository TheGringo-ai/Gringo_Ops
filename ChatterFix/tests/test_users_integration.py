"""
Integration Tests for ChatterFix User Management using Firebase Emulator
"""
import os
import sys
import pytest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import users, database, models

@pytest.mark.integration
class TestUserIntegration:
    """
    Integration tests for the user management functions, using a real Firestore backend (emulator).
    """
    created_user_ids = []
    test_username = "test_user_integration"

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, firestore_client):
        """
        Fixture to set up the database client for each test and clean up created data afterwards.
        """
        database.db_client = firestore_client
        self.cleanup()
        yield
        self.cleanup()

    def cleanup(self):
        """Deletes all documents created during tests."""
        if not database.db_client:
            return
        # Clean up users with the specific test username
        query = database.db_client.collection("users").where("username", "==", self.test_username)
        for doc in query.stream():
            print(f"Cleaning up user: {doc.id}")
            doc.reference.delete()
        self.created_user_ids = []

    def test_create_and_verify_user(self):
        """
        Tests creating a new user and then verifying their credentials.
        """
        password = "SecurePassword123!"
        user_id = users.create_user(
            username=self.test_username,
            password=password,
            role="technician",
            email="test@example.com"
        )
        self.created_user_ids.append(user_id)

        # Verify user with correct password
        verified_user = users.verify_user(self.test_username, password)
        assert verified_user is not None
        assert verified_user.id == user_id
        assert verified_user.username == self.test_username
        assert verified_user.role == "technician"

        # Verify user with incorrect password
        unverified_user = users.verify_user(self.test_username, "WrongPassword")
        assert unverified_user is None

    def test_prevent_duplicate_username(self):
        """
        Tests that creating a user with an existing username raises an error.
        """
        # 1. Create an initial user
        users.create_user(self.test_username, "pass1", "admin", "admin@test.com")

        # 2. Attempt to create another user with the same username
        with pytest.raises(ValueError, match="Username already exists."):
            users.create_user(self.test_username, "pass2", "manager", "manager@test.com")

    def test_update_and_delete_user(self):
        """
        Tests updating a user's role and email, and then deleting the user.
        """
        # 1. Create a user
        user_id = users.create_user(self.test_username, "password", "manager", "original@example.com")

        # 2. Update user's role and email
        updates = {"role": "admin", "email": "updated@example.com"}
        users.update_user(user_id, updates)

        updated_user = users.get_user_by_id(user_id)
        assert updated_user.role == "admin"
        assert updated_user.email == "updated@example.com"

        # 3. Delete the user
        users.delete_user(user_id)
        deleted_user = users.get_user_by_id(user_id)
        assert deleted_user is None
