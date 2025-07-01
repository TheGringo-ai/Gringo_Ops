"""
Integration Tests for ChatterFix Procurement and Supplier Management using Firebase Emulator
"""
import os
import sys
import pytest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import procurement, inventory, database, models

@pytest.mark.integration
class TestProcurementIntegration:
    """
    Integration tests for procurement, supplier, and purchase order functions.
    """
    created_ids = {
        "suppliers": [],
        "parts": [],
        "purchase_orders": []
    }

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, firestore_client):
        """
        Set up the database client and clean up all created test data.
        """
        database.db_client = firestore_client
        self.cleanup()
        yield
        self.cleanup()

    def cleanup(self):
        """Deletes all documents created during tests from all relevant collections."""
        if not database.db_client:
            return
        for collection, ids in self.created_ids.items():
            for doc_id in ids:
                try:
                    print(f"Cleaning up {collection}: {doc_id}")
                    database.db_client.collection(collection).document(doc_id).delete()
                except Exception as e:
                    print(f"Error cleaning up {collection} {doc_id}: {e}")
        self.created_ids = {"suppliers": [], "parts": [], "purchase_orders": []}

    def test_create_and_get_supplier(self):
        """
        Tests creating a new supplier and then retrieving it.
        """
        supplier_id = procurement.create_supplier(
            name="Test Supplier Inc.",
            contact_person="John Doe",
            email="contact@testsupplier.com"
        )
        self.created_ids["suppliers"].append(supplier_id)

        retrieved_supplier = procurement.get_supplier(supplier_id)
        assert retrieved_supplier is not None
        assert retrieved_supplier.id == supplier_id
        assert retrieved_supplier.name == "Test Supplier Inc."

    def test_full_purchase_order_lifecycle(self):
        """
        Tests creating a PO, updating its status, receiving items, and verifying stock levels.
        """
        # 1. Create a supplier and a part
        supplier_id = procurement.create_supplier(name="Test Auto Parts")
        self.created_ids["suppliers"].append(supplier_id)

        part_id = inventory.add_part(
            name="Test Part", part_number="TP-001", stock_quantity=10,
            location="A1", category="Testing", low_stock_threshold=5, supplier=supplier_id
        )
        self.created_ids["parts"].append(part_id)

        # 2. Create a Purchase Order
        po_items = [{'part_id': part_id, 'quantity': 20, 'unit_price': 9.99}]
        po_id = procurement.create_purchase_order(
            supplier_id=supplier_id,
            items=po_items,
            created_by="test_runner"
        )
        self.created_ids["purchase_orders"].append(po_id)

        po = procurement.get_purchase_order(po_id)
        assert po is not None
        assert po.status == 'pending_approval'
        assert po.total_cost == 20 * 9.99

        # 3. Update PO status
        procurement.update_purchase_order_status(po_id, 'ordered')
        updated_po = procurement.get_purchase_order(po_id)
        assert updated_po.status == 'ordered'

        # 4. Receive items
        received_items = [{'part_id': part_id, 'quantity_received': 20}]
        procurement.receive_purchase_order_items(po_id, received_items, user="receiver_test")

        # 5. Verify stock and PO status
        final_po = procurement.get_purchase_order(po_id)
        assert final_po.status == 'received'

        updated_part = inventory.get_part_by_id(part_id)
        assert updated_part.stock_quantity == 30 # Initial 10 + 20 received

    def test_automated_po_generation(self):
        """
        Tests the automated PO generation for low-stock items.
        """
        # 1. Create a supplier and a low-stock part
        supplier_id = procurement.create_supplier(name="Low Stock Supplier")
        self.created_ids["suppliers"].append(supplier_id)

        part_id = inventory.add_part(
            name="Low Stock Part", part_number="LSP-001", stock_quantity=2,
            location="B2", category="Urgent", low_stock_threshold=5, supplier=supplier_id
        )
        self.created_ids["parts"].append(part_id)

        # 2. Run the automated check
        created_po_ids = procurement.check_inventory_and_generate_po("auto_system")
        self.created_ids["purchase_orders"].extend(created_po_ids)

        # 3. Verify a PO was created
        assert len(created_po_ids) == 1
        po_id = created_po_ids[0]
        new_po = procurement.get_purchase_order(po_id)
        assert new_po is not None
        assert new_po.supplier_id == supplier_id
        assert new_po.status == 'pending_approval'
        assert new_po.items[0]['part_id'] == part_id
        assert new_po.items[0]['quantity'] == 10 # 2 * low_stock_threshold
