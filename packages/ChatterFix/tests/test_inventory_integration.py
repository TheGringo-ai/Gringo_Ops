"""
Integration Tests for ChatterFix Inventory Management using Firebase Emulator
"""
import os
import sys
import pytest
from unittest.mock import patch

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from backend import inventory, database, models

@pytest.mark.integration
class TestInventoryIntegration:
    """
    Integration tests for the inventory management functions, using a real Firestore backend (emulator).
    """
    test_part_id = "TEST-PN-12345"
    created_docs = []

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, firestore_client):
        """
        Fixture to set up the database client for each test and clean up created data afterwards.
        """
        database.db = firestore_client
        # Cleanup before the test runs to ensure a clean slate
        self.cleanup()
        yield
        # Cleanup after the test runs
        self.cleanup()

    def cleanup(self):
        """Deletes all documents created during tests."""
        if not database.db:
            return

        # Clean up parts collection
        parts_ref = database.db.collection("parts")
        docs = parts_ref.where("part_number", "==", self.test_part_id).stream()
        for doc in docs:
            print(f"Cleaning up part: {doc.id}")
            doc.reference.delete()

        # Also clean up any explicitly tracked documents
        for doc_ref in self.created_docs:
            try:
                doc_ref.delete()
            except Exception as e:
                print(f"Error cleaning up doc: {e}")
        self.created_docs = []


    def test_add_and_get_part(self):
        """
        Tests adding a new part and then retrieving it to verify its properties.
        """
        # 1. Add a new part
        part_details = {
            "name": "Flux Capacitor",
            "part_number": self.test_part_id,
            "stock_quantity": 1,
            "location": "Shelf A-1",
            "category": "Time Travel Components",
            "low_stock_threshold": 2,
            "supplier": "Gringo Starr"
        }
        
        doc_id = inventory.add_part(**part_details, invoked_by_user="test_runner")
        assert doc_id == self.test_part_id
        
        # Track for cleanup
        doc_ref = database.db.collection("parts").document(doc_id)
        self.created_docs.append(doc_ref)

        # 2. Retrieve the part and verify
        retrieved_part = inventory.get_part_by_id(doc_id)
        assert retrieved_part is not None
        assert retrieved_part.name == part_details["name"]
        assert retrieved_part.part_number == self.test_part_id
        assert retrieved_part.stock_quantity == 1
        assert retrieved_part.location == "Shelf A-1"
        assert retrieved_part.low_stock_threshold == 2

    def test_update_part(self):
        """
        Tests updating a part's location and verifying the change.
        """
        # 1. Add a part to update
        inventory.add_part(
            name="Oscillation Overthruster",
            part_number=self.test_part_id,
            stock_quantity=10,
            location="Box B-2",
            category="Propulsion",
            low_stock_threshold=5,
            invoked_by_user="test_runner"
        )
        
        # 2. Update the part's location
        updates = {"location": "Cabinet C-3", "category": "Advanced Propulsion"}
        inventory.update_part(self.test_part_id, updates, invoked_by_user="test_runner")

        # 3. Retrieve and verify the update
        updated_part = inventory.get_part_by_id(self.test_part_id)
        assert updated_part is not None
        assert updated_part.location == "Cabinet C-3"
        assert updated_part.category == "Advanced Propulsion"

    def test_adjust_stock_and_low_stock_check(self):
        """
        Tests adjusting stock levels and verifying the low stock warning system.
        """
        # 1. Add a part
        part_details = {
            "name": "Sonic Screwdriver",
            "part_number": self.test_part_id,
            "stock_quantity": 5,
            "location": "Toolbelt",
            "category": "Multipurpose Tools",
            "low_stock_threshold": 3,
            "supplier": "Timelord Supplies"
        }
        inventory.add_part(**part_details, invoked_by_user="test_runner")

        # 2. Adjust stock up
        inventory.adjust_stock(self.test_part_id, 5, user="test_runner")
        part = inventory.get_part_by_id(self.test_part_id)
        assert part.stock_quantity == 10

        # 3. Adjust stock down
        inventory.adjust_stock(self.test_part_id, -7, user="test_runner") # 10 - 7 = 3
        part = inventory.get_part_by_id(self.test_part_id)
        assert part.stock_quantity == 3

        # 4. Check for low stock (should be low now)
        low_stock_parts = inventory.get_low_stock_parts()
        assert any(p.part_number == self.test_part_id for p in low_stock_parts)

        # 5. Adjust stock back up
        inventory.adjust_stock(self.test_part_id, 1, user="test_runner") # 3 + 1 = 4
        
        # 6. Check for low stock again (should NOT be low now)
        low_stock_parts = inventory.get_low_stock_parts()
        assert not any(p.part_number == self.test_part_id for p in low_stock_parts)
