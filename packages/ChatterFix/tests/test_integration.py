"""
Integration Tests for the ChatterFix Application.

This suite tests the interaction between different components of the system,
such as the agent and the database, using the actual Firebase Emulator.
"""
import unittest
import sys
import os
import time # Added for connection retries
from unittest.mock import patch, MagicMock
import google.cloud.firestore

# Add project root for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import the agent and the database module we want to test
from ChatterFix.backend.chatterfix_agent import ChatterFixAgent
from ChatterFix.backend import database, work_orders

# --- Test Configuration ---
# These settings direct the Firebase Admin SDK to use the local emulator
# instead of connecting to the live Google Cloud project.
os.environ["GCLOUD_PROJECT"] = "chatterfix-test-project"
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8686" # Using IP for consistency

class TestAgentFirestoreIntegration(unittest.TestCase):
    """
    Tests the integration between the ChatterFixAgent and the Firestore Emulator.
    """
    db = None

    @classmethod
    def setUpClass(cls):
        """Initialize a connection to the Firestore emulator, with retries."""
        max_retries = 5
        retry_delay = 4  # seconds
        for attempt in range(max_retries):
            try:
                # The environment variables set above direct this client to the emulator.
                cls.db = google.cloud.firestore.Client()
                # Perform a simple operation to confirm the connection is truly live.
                list(cls.db.collections())
                print(f"\n✅ Successfully connected to Firestore Emulator on attempt {attempt + 1}.")
                return  # Exit the setup method on success
            except Exception as e:
                print(f"\nAttempt {attempt + 1}/{max_retries} failed: Could not connect to Firestore Emulator. Retrying in {retry_delay}s...")
                print(f"   Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("\n❌ All attempts to connect to the emulator failed. Please ensure it is running and accessible at 127.0.0.1:8686.")
                    sys.exit(1)  # Exit if all retries fail

    def setUp(self):
        """Clear all data from collections before each test to ensure isolation."""
        print("\n--- Clearing Firestore data for new test ---")
        try:
            collections = list(self.db.collections())
            if not collections:
                print("No collections found to clear.")
                return
            for collection_ref in collections:
                for doc_ref in collection_ref.stream():
                    doc_ref.reference.delete()
            print("Data cleared successfully.")
        except Exception as e:
            print(f"\n❌ Error clearing Firestore data: {e}")
            print("   This may indicate a problem with the emulator connection.")
            # We will let the test proceed, but it will likely fail.
            # This provides more specific feedback than a hard exit.

    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter')
    def test_create_work_order_integration(self, MockLLMRouter):
        """
        Verify the agent can process a command to create a work order,
        and that the work order is correctly saved to the Firestore emulator.
        """
        # Arrange:
        # 1. Mock the LLM's response to simulate it wanting to use the 'create_work_order' tool.
        mock_router_instance = MockLLMRouter.return_value
        llm_response_json = '''{
            "tool_name": "create_work_order",
            "parameters": {
                "title": "Main conveyor belt is torn",
                "description": "The main conveyor belt, model CV-100, has a 5-foot tear.",
                "priority": "high",
                "equipment_id": "ASSET-001"
            }
        }'''
        mock_router_instance.invoke_model.return_value = llm_response_json

        # 2. Initialize the agent. It will use the real backend functions that talk to the emulator.
        # We need to reload the modules to make sure they pick up the emulator connection.
        import importlib
        importlib.reload(database)
        importlib.reload(work_orders)
        from ChatterFix.backend.chatterfix_agent import ChatterFixAgent # Re-import after reload
        agent = ChatterFixAgent()

        command = "The main conveyor belt is torn. We need to replace it. Priority is high."
        test_user = "integration_tester@chatterfix.com"

        # Act:
        # Run the command through the agent. This should trigger the real create_work_order function.
        result = agent.route_command(command, invoked_by_user=test_user)

        # Assert:
        # 1. Check that the agent reported success.
        self.assertTrue(result.get('success'))
        self.assertEqual(result['tool'], 'create_work_order')

        # 2. Verify the work order was actually created in the Firestore emulator.
        work_orders_ref = self.db.collection('work_orders')
        docs = list(work_orders_ref.stream())
        self.assertEqual(len(docs), 1)
        created_wo = docs[0].to_dict()
        self.assertEqual(created_wo['title'], "Main conveyor belt is torn")
        self.assertEqual(created_wo['status'], 'open') # Default status
        self.assertEqual(created_wo['created_by'], test_user)

    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter')
    def test_full_work_order_lifecycle(self, MockLLMRouter):
        """
        Verify the agent can create, update, and assign a work order.
        """
        # Arrange:
        agent = ChatterFixAgent()
        test_user = "lifecycle_tester@chatterfix.com"
        
        # --- 1. Create the Work Order ---
        mock_router_instance = MockLLMRouter.return_value
        mock_router_instance.invoke_model.return_value = '''{
            "tool_name": "create_work_order",
            "parameters": {
                "title": "Hydraulic pump leaking",
                "description": "Pump P-501 is leaking hydraulic fluid near the main seal.",
                "priority": "medium",
                "equipment_id": "ASSET-002"
            }
        }'''
        
        create_result = agent.route_command("A hydraulic pump is leaking", invoked_by_user=test_user)
        self.assertTrue(create_result.get('success'))
        work_order_id = create_result.get('document_id')
        self.assertIsNotNone(work_order_id)

        # --- 2. Update the Status ---
        mock_router_instance.invoke_model.return_value = f'''{{
            "tool_name": "update_work_order_status",
            "parameters": {{
                "work_order_id": "{work_order_id}",
                "new_status": "in_progress",
                "user": "{test_user}"
            }}
        }}'''

        update_result = agent.route_command(f"Start work on ticket {work_order_id}", invoked_by_user=test_user)
        self.assertTrue(update_result.get('success'))

        # --- 3. Assign the Work Order ---
        technician_id = "tech-jane-doe"
        mock_router_instance.invoke_model.return_value = f'''{{
            "tool_name": "assign_work_order",
            "parameters": {{
                "work_order_id": "{work_order_id}",
                "assignee_id": "{technician_id}",
                "user": "{test_user}"
            }}
        }}'''

        assign_result = agent.route_command(f"Assign ticket {work_order_id} to Jane Doe", invoked_by_user=test_user)
        self.assertTrue(assign_result.get('success'))

        # --- 4. Verify the final state in Firestore ---
        final_wo_doc = self.db.collection('work_orders').document(work_order_id).get()
        self.assertTrue(final_wo_doc.exists)
        final_wo_data = final_wo_doc.to_dict()

        self.assertEqual(final_wo_data['status'], 'in_progress')
        self.assertEqual(final_wo_data['assigned_to_id'], technician_id)
        
        # Check that the history was recorded correctly
        history = final_wo_data.get('history', [])
        self.assertEqual(len(history), 2)
        self.assertIn("Status changed to 'in_progress'", history[0]['action'])
        self.assertIn(f"Assigned to user ({technician_id})", history[1]['action'])


if __name__ == '__main__':
    # Note: Running this directly requires the Firebase Emulator to be active.
    # You can start it with: firebase emulators:start --only firestore
    unittest.main()
