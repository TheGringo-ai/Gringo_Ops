import streamlit as st
import sys
import os
from unittest.mock import MagicMock

# The conftest.py already adds the project root to the path, so this is not needed.
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Corrected import based on project structure. The sidebar is in the 'pages' directory.
from pages.sidebar import agent_sidebar

def test_sidebar_renders(monkeypatch):
    """
    Tests that the agent_sidebar function can be called and attempts to render.
    This is a basic unit test, not a full UI test.
    """
    # The conftest.py provides a mock for `st`, but it doesn't have a `sidebar` attribute.
    # We use monkeypatch to add a mock `sidebar` to the mocked `st` object.
    mock_sidebar = MagicMock()
    monkeypatch.setattr(st, "sidebar", mock_sidebar)

    # Set a return value for the radio button to avoid issues with list indexing
    st.sidebar.radio.return_value = "🤖 FredFix"

    try:
        selected = agent_sidebar(selected_agent="FredFix")
        assert selected == "8_FredFix_Agent.py" # Check if it returns the correct page

        # Assert that some key sidebar elements were called
        st.sidebar.title.assert_called_with("🛠️ AI Operations Hub")
        st.sidebar.radio.assert_called()
        st.sidebar.button.assert_called_with("Go to GringoOpsHub 🏢")
    except Exception as e:
        assert False, f"Sidebar failed to render even with mocks: {e}"
