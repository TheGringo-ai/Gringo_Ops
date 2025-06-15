import streamlit as st
from datetime import datetime

def init_state():
    defaults = {
        "prompt_history": [],
        "generated_files": [],
        "current_output": "",
        "current_prompt": "",
        "model_choice": "gpt-4",
        "wizard_stage": "start",
        "session_timestamp": str(datetime.now()),
        "memory_log": [],
        "auto_resume": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_state():
    st.session_state.prompt_history = []
    st.session_state.generated_files = []
    st.session_state.current_output = ""
    st.session_state.current_prompt = ""
    st.session_state.model_choice = "gpt-4"
    st.session_state.wizard_stage = "start"
    st.session_state.session_timestamp = str(datetime.now())
    st.session_state.memory_log = []
    st.session_state.auto_resume = True