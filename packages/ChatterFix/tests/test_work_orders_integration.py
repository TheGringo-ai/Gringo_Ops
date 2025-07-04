"""
Integration Tests for ChatterFix Work Order Management using Firebase Emulator
"""
import os
import sys
import pytest
from datetime import datetime

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from backend import work_orders, database, models

@pytest.mark.integration
class TestWorkOrderIntegration:
    """
    Integration tests for the work order management functions, using a real Firestore backend (emulator).
    """
    created_work_order_ids = []

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, firestore_client):
        """
        Fixture to set up the database client for each test and clean up created data afterwards.
        """
        # This is a workaround to set the db client for the database module in tests.
        # In a real application, you might have a more sophisticated way of managing the db connection.
        database.db_client = firestore_client
        self.cleanup() # Clean before test
        yield
        self.cleanup() # Clean after test

    def cleanup(self):
        """Deletes all documents created during tests."""
        if not database.db_client:
            return
        for wo_id in self.created_work_order_ids:
            try:
                print(f"Cleaning up work order: {wo_id}")
                database.db_client.collection("work_orders").document(wo_id).delete()
            except Exception as e:
                print(f"Error cleaning up work order {wo_id}: {e}")
        self.created_work_order_ids = []

    def test_create_and_get_work_order(self):
        """
        Tests creating a new work order and then retrieving it.
        """
        title = "Fix the temporal displacement unit"
        description = "It's causing temporal paradoxes again."
        wo_id = work_orders.create_work_order(
            title=title,
            description=description,
            priority="high",
            equipment_id="TDU-001",
            invoked_by_user="test_runner"
        )
        self.created_work_order_ids.append(wo_id)

        retrieved_wo = work_orders.get_work_order(wo_id)
        assert retrieved_wo is not None
        assert retrieved_wo.id == wo_id
        assert retrieved_wo.title == title
        assert retrieved_wo.description == description
        assert retrieved_wo.status == "open"
        assert retrieved_wo.priority == "high"
        assert retrieved_wo.created_by == "test_runner"

    def test_update_and_assign_work_order(self):
        """
        Tests updating a work order's status, assigning it to a user, and checking the history.
        """
        # 1. Create a work order
        wo_id = work_orders.create_work_order(
            title="Calibrate the sonic emitter",
            description="The frequency is off by 0.2 kilohertz.",
            priority="medium",
            invoked_by_user="test_creator"
        )
        self.created_work_order_ids.append(wo_id)

        # 2. Update status
        work_orders.update_work_order_status(wo_id, "in_progress", user="test_updater")
        updated_wo = work_orders.get_work_order(wo_id)
        assert updated_wo.status == "in_progress"

        # 3. Assign to a user
        assignee_id = "tech-007"
        work_orders.assign_work_order(wo_id, assignee_id, user="test_assigner")
        assigned_wo = work_orders.get_work_order(wo_id)
        assert assigned_wo.assigned_to_id == assignee_id

        # 4. Verify history
        final_wo = work_orders.get_work_order(wo_id)
        assert len(final_wo.history) == 2
        assert final_wo.history[0]['action'] == "Status changed to 'in_progress'."
        assert final_wo.history[0]['user'] == "test_updater"
        assert final_wo.history[1]['action'] == f"Assigned to user ({assignee_id})."
        assert final_wo.history[1]['user'] == "test_assigner"

    def test_get_all_and_by_status(self):
        """
        Tests retrieving all work orders and filtering them by status.
        """
        # Create a few work orders with different statuses
        wo1_id = work_orders.create_work_order("WO1", "d1", "low", status="open")
        wo2_id = work_orders.create_work_order("WO2", "d2", "high", status="in_progress")
        wo3_id = work_orders.create_work_order("WO3", "d3", "medium", status="open")
        self.created_work_order_ids.extend([wo1_id, wo2_id, wo3_id])

        # Test get_all_work_orders
        all_wos = work_orders.get_all_work_orders()
        assert len(all_wos) >= 3

        # Test get_work_orders_by_status
        open_wos = work_orders.get_work_orders_by_status("open")
        assert len(open_wos) == 2
        assert all(wo.status == "open" for wo in open_wos)

        in_progress_wos = work_orders.get_work_orders_by_status("in_progress")
        assert len(in_progress_wos) == 1
        assert in_progress_wos[0].status == "in_progress"
