"""
Automated Test Suite for ChatterFix Backend

This script runs a series of tests to verify the core functionality of the backend modules,
including database interactions for users, assets, parts, and work orders.

It is designed to be run from the root directory of the ChatterFix project.
"""

import sys
import os
import time

# --- Environment Setup ---
# Add the project root to the Python path to allow importing backend modules
# This allows running the test script from the project root (GringoOps)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from ChatterFix.backend import users, assets, parts, work_orders, database

# --- Test Data ---
TEST_USER = {
    "username": "test_user_12345",
    "password": "secure_password_!@#$",
    "role": "technician",
    "email": "test@example.com"
}

TEST_ASSET = {
    "name": "Test Asset - CNC Machine",
    "asset_type": "Machinery",
    "location": "Test Bay 1",
    "purchase_date": "2025-01-15",
    "purchase_price": 50000.0,
    "serial_number": "TEST-SN-98765"
}

TEST_PART = {
    "name": "Test Part - Bearing",
    "part_number": "TP-BR-54321",
    "stock_quantity": 100,
    "location": "Test Bin A1",
    "supplier": "Test Supplier Inc.",
    "category": "Bearings",
    "low_stock_threshold": 10
}

TEST_WORK_ORDER = {
    "title": "Test Work Order - Annual Inspection",
    "description": "Perform annual inspection on the test asset.",
    "priority": "medium"
}

# --- Test Runner ---

def run_test(test_function):
    """Decorator to run a test function and print its status."""
    test_name = test_function.__name__
    print(f"\n--- Running: {test_name} ---")
    try:
        test_function()
        print(f"✅ PASSED: {test_name}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Test Definitions ---

@run_test
def test_user_module():
    """Tests the full lifecycle (CRUD) of a user."""
    user_id = None
    try:
        # 1. Create User
        print("Step 1: Creating user...")
        user_id = users.create_user(**TEST_USER)
        assert user_id is not None, "create_user should return an ID."
        print(f"   -> Created user with ID: {user_id}")

        # 2. Verify User
        print("Step 2: Verifying user...")
        verified_user = users.verify_user(TEST_USER["username"], TEST_USER["password"])
        assert verified_user is not None, "verify_user should return a user object."
        assert verified_user.username == TEST_USER["username"], "Verified username should match."
        print("   -> User verified successfully.")

        # 3. Get User by ID
        print("Step 3: Fetching user by ID...")
        fetched_user = users.get_user_by_id(user_id)
        assert fetched_user is not None
        assert fetched_user.id == user_id
        print("   -> Fetched user by ID successfully.")

        # 4. Update User
        print("Step 4: Updating user...")
        updates = {"email": "updated.email@example.com"}
        users.update_user(user_id, updates)
        updated_user = users.get_user_by_id(user_id)
        assert updated_user.email == "updated.email@example.com", "Email should be updated."
        print("   -> User updated successfully.")

    finally:
        # 5. Cleanup
        if user_id:
            print(f"Step 5: Cleaning up user {user_id}...")
            users.delete_user(user_id)
            # Verify deletion
            deleted_user = users.get_user_by_id(user_id)
            assert deleted_user is None, "User should be deleted."
            print("   -> Cleanup successful.")

@run_test
def test_asset_module():
    """Tests the lifecycle of an asset."""
    asset_id = None
    try:
        # 1. Create Asset
        print("Step 1: Creating asset...")
        asset_id = assets.create_asset(**TEST_ASSET)
        assert asset_id is not None, "create_asset should return an ID."
        print(f"   -> Created asset with ID: {asset_id}")

        # 2. Get Asset
        print("Step 2: Fetching asset...")
        fetched_asset = assets.get_asset(asset_id)
        assert fetched_asset is not None
        assert fetched_asset.id == asset_id
        assert fetched_asset.name == TEST_ASSET["name"]
        assert fetched_asset.qr_code_url, "QR code should be generated."
        print("   -> Fetched asset successfully.")

    finally:
        # 3. Cleanup
        if asset_id:
            print(f"Step 3: Cleaning up asset {asset_id}...")
            database.delete_document("assets", asset_id)
            deleted_asset = assets.get_asset(asset_id)
            assert deleted_asset is None, "Asset should be deleted."
            print("   -> Cleanup successful.")

@run_test
def test_part_module():
    """Tests the lifecycle of a part."""
    part_id = None
    try:
        # 1. Create Part
        print("Step 1: Creating part...")
        part_id = parts.create_part(**TEST_PART)
        assert part_id is not None, "create_part should return an ID."
        print(f"   -> Created part with ID: {part_id}")

        # 2. Get Part
        print("Step 2: Fetching part...")
        fetched_part = parts.get_part(part_id)
        assert fetched_part is not None
        assert fetched_part.id == part_id
        assert fetched_part.name == TEST_PART["name"]
        assert fetched_part.qr_code_url, "QR code should be generated."
        print("   -> Fetched part successfully.")

    finally:
        # 3. Cleanup
        if part_id:
            print(f"Step 3: Cleaning up part {part_id}...")
            database.delete_document("parts", part_id)
            deleted_part = parts.get_part(part_id)
            assert deleted_part is None, "Part should be deleted."
            print("   -> Cleanup successful.")

@run_test
def test_work_order_module():
    """Tests the lifecycle of a work order."""
    wo_id = None
    try:
        # 1. Create Work Order
        print("Step 1: Creating work order...")
        wo_id = work_orders.create_work_order(**TEST_WORK_ORDER)
        assert wo_id is not None, "create_work_order should return an ID."
        print(f"   -> Created work order with ID: {wo_id}")

        # 2. Get Work Order
        print("Step 2: Fetching work order...")
        fetched_wo = work_orders.get_work_order(wo_id)
        assert fetched_wo is not None
        assert fetched_wo.id == wo_id
        assert fetched_wo.title == TEST_WORK_ORDER["title"]
        print("   -> Fetched work order successfully.")

        # 3. Update Status
        print("Step 3: Updating work order status...")
        work_orders.update_work_order_status(wo_id, "in_progress", "test_runner")
        updated_wo = work_orders.get_work_order(wo_id)
        assert updated_wo.status == "in_progress", "Status should be updated."
        assert len(updated_wo.history) > 0, "History should be logged."
        print("   -> Status updated successfully.")

    finally:
        # 4. Cleanup
        if wo_id:
            print(f"Step 4: Cleaning up work order {wo_id}...")
            database.delete_document("work_orders", wo_id)
            deleted_wo = work_orders.get_work_order(wo_id)
            assert deleted_wo is None, "Work order should be deleted."
            print("   -> Cleanup successful.")


if __name__ == "__main__":
    print("=======================================")
    print("    Running ChatterFix Backend Tests   ")
    print("=======================================")

    # Initialize Firestore
    # This assumes you have your Google Cloud credentials set up in your environment
    try:
        print("Initializing Firestore...")
        database.get_db()
        print("Firestore initialized successfully.")
    except Exception as e:
        print("❌ CRITICAL: Failed to initialize Firestore.")
        print(f"   Error: {e}")
        print("   Please ensure your GOOGLE_APPLICATION_CREDENTIALS are set correctly.")
        sys.exit(1)

    results = {
        "passed": 0,
        "failed": 0
    }

    tests_to_run = [
        test_user_module,
        test_asset_module,
        test_part_module,
        test_work_order_module
    ]

    for test in tests_to_run:
        if test(): # The decorator returns True on pass, False on fail
            results["passed"] += 1
        else:
            results["failed"] += 1

    print("\n=======================================")
    print("             Test Summary            ")
    print("=======================================")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print("=======================================")

    if results["failed"] > 0:
        sys.exit(1) # Exit with a non-zero code to indicate failure
