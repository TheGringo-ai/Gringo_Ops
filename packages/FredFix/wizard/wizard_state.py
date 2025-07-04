import uuid
import streamlit as st
from datetime import datetime


def get_defaults() -> dict:
    """Returns a dictionary of default session state values."""
    return {
        "prompt_history": [],
        "generated_files": [],
        "current_output": "",
        "current_prompt": "",
        "current_filename": "fredfix_output.py",
        "model_choice": "gpt-4",
        "wizard_stage": "start",
        "session_timestamp": str(datetime.now()),
        "memory_log": [],
        "auto_resume": True,
        "session_id": str(uuid.uuid4()),
        "token_usage": {"prompt": 0, "completion": 0},
    }


def init_state() -> None:
    """Initializes the session state with default values if they don't exist."""
    defaults = get_defaults()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state() -> None:
    """Resets the session state to its default values."""
    defaults = get_defaults()
    for key, value in defaults.items():
        st.session_state[key] = value


def get_state() -> dict:
    """Returns the current session state as a dictionary."""
    return dict(st.session_state)
