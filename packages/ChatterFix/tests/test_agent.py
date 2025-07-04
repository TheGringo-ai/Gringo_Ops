"""
Unit Tests for the ChatterFix AI Agent.

This test suite verifies the functionality of the ChatterFixAgent, including
its initialization, tool loading, prompt generation, and command routing logic.
It uses mocking to isolate the agent from its dependencies (LLM router, backend tools).
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call

# Add the project root to the path to allow imports like `from lib.llm_router import LLMRouter`
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Mock the backend modules before they are imported by the agent
# This is necessary because the agent imports them at the module level.
mock_work_orders = MagicMock()
mock_inventory = MagicMock()
mock_assets = MagicMock()
mock_users = MagicMock()
mock_erp_tools = MagicMock()
mock_predictive = MagicMock()
mock_database = MagicMock()

# Define dummy functions for the mocks to simulate the tool functions
mock_work_orders.create_work_order = MagicMock(__doc__="Creates a new work order and saves it to the database.")
mock_work_orders.get_work_order = MagicMock(__doc__="Retrieves a single work order by its ID.")
mock_work_orders.update_work_order_status = MagicMock(__doc__="Updates the status of a work order and logs the change.")
mock_work_orders.get_all_work_orders = MagicMock(__doc__="Retrieves all work orders from the database.")

mock_inventory.get_part_by_id = MagicMock(__doc__="Retrieves a single part by its ID.")
mock_inventory.adjust_stock = MagicMock(__doc__="Adjusts the stock quantity of a part by a given amount (can be positive or negative).")
mock_inventory.get_low_stock_parts = MagicMock(__doc__="Scans the inventory and returns a list of all parts where the quantity is below the reorder threshold.")

mock_assets.get_asset = MagicMock(__doc__="Retrieves a single asset by its ID.")
mock_assets.get_all_assets = MagicMock(__doc__="Retrieves all assets from the database.")

mock_users.get_user_by_username = MagicMock(__doc__="Retrieves a user by their username. Returns the full document including hash for verification.")
mock_users.get_all_users = MagicMock(__doc__="Retrieves all users from the database.")

mock_erp_tools.get_vendor_data = MagicMock(__doc__="Looks up vendor and pricing information for a given part number.")
mock_erp_tools.generate_purchase_order = MagicMock(__doc__="Creates a purchase order (PO) in the ERP system.")

mock_predictive.get_maintenance_forecast = MagicMock(__doc__="Generates a maintenance forecast for a specific asset.")


modules = {
    'ChatterFix.backend.work_orders': mock_work_orders,
    'ChatterFix.backend.inventory': mock_inventory,
    'ChatterFix.backend.assets': mock_assets,
    'ChatterFix.backend.users': mock_users,
    'ChatterFix.backend.erp_tools': mock_erp_tools,
    'ChatterFix.backend.predictive': mock_predictive,
    'ChatterFix.backend.database': mock_database,
    # Also mock the LLM Router
    'lib.llm_router': MagicMock()
}

class TestChatterFixAgent(unittest.TestCase):
    """Test suite for the ChatterFixAgent."""

    def setUp(self):
        """Patch modules, reload the agent, and reset mocks for each test."""
        self.patcher = patch.dict('sys.modules', modules)
        self.patcher.start()

        # We need to reload the module under test to ensure our mocks are used
        import importlib
        from ChatterFix.backend import chatterfix_agent
        importlib.reload(chatterfix_agent)
        self.ChatterFixAgent = chatterfix_agent.ChatterFixAgent

        # Reset mocks on the actual mock objects for test isolation
        mock_work_orders.reset_mock()
        mock_inventory.reset_mock()
        mock_assets.reset_mock()
        mock_users.reset_mock()
        mock_erp_tools.reset_mock()
        mock_predictive.reset_mock()
        mock_database.reset_mock()


    def tearDown(self):
        """Stop the patcher after each test."""
        self.patcher.stop()


    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter')
    def test_agent_initialization_success(self, MockLLMRouter):
        """Verify the agent initializes correctly with all dependencies."""
        mock_router_instance = MockLLMRouter.return_value
        agent = self.ChatterFixAgent()

        self.assertIsNotNone(agent.llm_router)
        self.assertEqual(agent.llm_router, mock_router_instance)
        self.assertIsInstance(agent.available_tools, dict)
        self.assertGreater(len(agent.available_tools), 0)
        MockLLMRouter.assert_called_once()


    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter', side_effect=Exception("Router Init Error"))
    def test_agent_initialization_failure(self, MockLLMRouter):
        """Verify the agent handles initialization errors gracefully."""
        agent = self.ChatterFixAgent()
        self.assertIsNone(agent.llm_router)
        self.assertEqual(agent.available_tools, {})
        MockLLMRouter.assert_called_once()


    def test_get_available_tools(self):
        """Verify that the agent correctly gathers tools from mocked backend modules."""
        agent = self.ChatterFixAgent()
        # Check if a few key tools are present
        self.assertIn("create_work_order", agent.available_tools)
        self.assertIn("get_part_by_id", agent.available_tools)
        self.assertIn("get_maintenance_forecast", agent.available_tools)
        # Check if the values are the mocked functions
        self.assertEqual(agent.available_tools["create_work_order"], mock_work_orders.create_work_order)


    def test_get_tools_prompt_string(self):
        """Verify the tool prompt string is generated correctly from mock docstrings."""
        agent = self.ChatterFixAgent()
        prompt_string = agent._get_tools_prompt_string()
        self.assertIn("Here are the tools you can use.", prompt_string)
        self.assertIn("- `\"create_work_order\"`: Creates a new work order and saves it to the database.", prompt_string)
        self.assertIn("- `\"get_part_by_id\"`: Retrieves a single part by its ID.", prompt_string)


    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter')
    def test_send_chat_message_success(self, MockLLMRouter):
        """Verify the agent can handle a simple chat message and gets a response."""
        mock_router_instance = MockLLMRouter.return_value
        mock_router_instance.invoke_model.return_value = "Hello there! This is a test response."
        agent = self.ChatterFixAgent(chat_history=[])

        # The function is a generator, so we consume it
        response = list(agent.send_chat_message("Hello, agent!"))

        # Check that the router was called correctly
        mock_router_instance.invoke_model.assert_called_once()
        args, kwargs = mock_router_instance.invoke_model.call_args
        self.assertIn("user: Hello, agent!", args[0]) # Check prompt
        self.assertEqual(kwargs['task_type'], 'simple_chat')

        # Check the response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], "Hello there! This is a test response.")
        # Check that history is updated
        self.assertEqual(len(agent.chat_history), 2)
        self.assertEqual(agent.chat_history[-1]['content'], "Hello there! This is a test response.")


    @patch('ChatterFix.backend.chatterfix_agent.LLMRouter')
    def test_get_completion_for_cli(self, MockLLMRouter):
        """Verify the get_completion method for non-streaming CLI usage."""
        mock_router_instance = MockLLMRouter.return_value
        mock_router_instance.invoke_model.return_value = "CLI response."
        agent = self.ChatterFixAgent()

        response = agent.get_completion("CLI query")

        mock_router_instance.invoke_model.assert_called_once_with(
            "CLI query",
            task_type='simple_chat',
            override_model=None
        )
        self.assertEqual(response, "CLI response.")


if __name__ == '__main__':
    unittest.main()
