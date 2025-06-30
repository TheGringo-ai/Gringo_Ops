import pytest
import json
from unittest.mock import patch, MagicMock

# Make sure the app directory is in the path for imports
# (conftest.py should handle this, but this is a safeguard)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import ChatterFixAgent

@pytest.fixture
def agent_instance():
    """
    Provides a ChatterFixAgent instance for each test, with a mocked LLMRouter
    to prevent actual API calls.
    """
    agent = ChatterFixAgent()
    # Replace the real router with a mock to control its behavior in tests
    agent.llm_router = MagicMock()
    return agent

def test_process_input_routes_to_command(agent_instance):
    """
    Tests that when the LLM classifies input as a 'command',
    the run_tool_command method is correctly called.
    """
    user_input = "Create a work order for the main conveyor belt."
    user_email = "test@gringo.com"
    
    # Mock the classification response from the LLM
    classification_response = json.dumps({"intent": "command"})
    agent_instance.llm_router.invoke_model.return_value = classification_response
    
    # Patch the methods we expect to be called (or not called)
    with patch.object(agent_instance, 'run_tool_command', return_value={"success": True}) as mock_run_tool, \
         patch.object(agent_instance, 'send_chat_message') as mock_send_chat:

        # Call the method under test
        agent_instance.process_input(user_input, invoked_by_user=user_email)

        # Assert: The classification model was called with a prompt containing the user input
        agent_instance.llm_router.invoke_model.assert_called_once()
        call_args, _ = agent_instance.llm_router.invoke_model.call_args
        assert user_input in call_args[0]

        # Assert: The command router was called, and the chat method was not
        mock_run_tool.assert_called_once_with(user_input, invoked_by_user=user_email)
        mock_send_chat.assert_not_called()

def test_process_input_routes_to_chat(agent_instance):
    """
    Tests that when the LLM classifies input as 'chat',
    the send_chat_message method is correctly called.
    """
    user_input = "Hello, how are you today?"
    
    # Mock the classification response from the LLM
    classification_response = json.dumps({"intent": "chat"})
    agent_instance.llm_router.invoke_model.return_value = classification_response
    
    with patch.object(agent_instance, 'run_tool_command') as mock_run_tool, \
         patch.object(agent_instance, 'send_chat_message', return_value=iter(["Hello!"])) as mock_send_chat:

        agent_instance.process_input(user_input)

        # Assert: The chat method was called, and the command router was not
        mock_send_chat.assert_called_once_with(user_input)
        mock_run_tool.assert_not_called()

def test_process_input_falls_back_to_chat_on_json_error(agent_instance):
    """
    Tests that if the LLM returns malformed JSON, the agent safely
    falls back to calling the chat method to avoid crashing.
    """
    user_input = "This is some weird input."
    
    # Mock a malformed response that will cause a JSONDecodeError
    malformed_response = '{"intent": "command"' # Missing closing brace
    agent_instance.llm_router.invoke_model.return_value = malformed_response
    
    with patch.object(agent_instance, 'run_tool_command') as mock_run_tool, \
         patch.object(agent_instance, 'send_chat_message', return_value=iter(["I see."])) as mock_send_chat:

        agent_instance.process_input(user_input)

        # Assert: It fell back to chat and did not call the command tool
        mock_send_chat.assert_called_once_with(user_input)
        mock_run_tool.assert_not_called()

def test_process_input_falls_back_to_chat_on_classification_exception(agent_instance):
    """
    Tests that if the LLM call itself raises an exception, the agent safely
    falls back to calling the chat method.
    """
    user_input = "This input will cause an error."
    
    # Mock the LLM call to raise a generic exception
    agent_instance.llm_router.invoke_model.side_effect = Exception("LLM service unavailable")
    
    with patch.object(agent_instance, 'run_tool_command') as mock_run_tool, \
         patch.object(agent_instance, 'send_chat_message', return_value=iter(["Sorry..."])) as mock_send_chat:

        agent_instance.process_input(user_input)

        # Assert: It fell back to chat and did not call the command tool
        mock_send_chat.assert_called_once_with(user_input)
        mock_run_tool.assert_not_called()