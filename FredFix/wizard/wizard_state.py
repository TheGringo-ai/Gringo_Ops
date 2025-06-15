


import uuid
import streamlit as st

def init_state() -> None:
    if "prompt_history" not in st.session_state:
        st.session_state.prompt_history = []
    if "generated_files" not in st.session_state:
        st.session_state.generated_files = []
    if "current_output" not in st.session_state:
        st.session_state.current_output = ""
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = ""
    if "model_choice" not in st.session_state:
        st.session_state.model_choice = "gpt-4"
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {"prompt": 0, "completion": 0}

def reset_state() -> None:
    st.session_state.prompt_history = []
    st.session_state.generated_files = []
    st.session_state.current_output = ""
    st.session_state.current_prompt = ""
    st.session_state.model_choice = "gpt-4"


def get_state() -> dict:
    return dict(st.session_state)