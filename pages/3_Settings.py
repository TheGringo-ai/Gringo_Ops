import streamlit as st
from utils import auth

# --- Page Config and Authentication ---
st.set_page_config(page_title="Settings", layout="wide")
auth.display_app_header()

st.title("⚙️ Model Settings")
st.caption("Choose the default AI models for different tasks across the application.")

# --- Available Models ---
# In a larger application, you might centralize this list in a config file.
AVAILABLE_MODELS = {
    "chat": [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "claude-3-haiku-20240307",
        "gpt-3.5-turbo",
    ],
    "tool_use": [
        "gemini-1.5-pro-latest",
        "claude-3-opus-20240229",
        "gpt-4o",
    ]
}

# --- Initialize Session State ---
# Set default values if they don't exist in the session state.
if 'preferred_chat_model' not in st.session_state:
    st.session_state.preferred_chat_model = AVAILABLE_MODELS["chat"][0]

if 'preferred_tool_model' not in st.session_state:
    st.session_state.preferred_tool_model = AVAILABLE_MODELS["tool_use"][0]


# --- UI for Model Selection ---
st.subheader("Default Chat Model")
st.write("Select the model to use for general conversation in the AI Chat.")
# Using `st.session_state` as the key creates a two-way binding.
st.selectbox("Chat Model", options=AVAILABLE_MODELS["chat"], key='preferred_chat_model', help="Models optimized for fast, conversational responses.")

st.divider()

st.subheader("Default Tool-Use Model")
st.write("Select the model to use for interpreting commands and using tools.")
st.selectbox("Tool-Use Model", options=AVAILABLE_MODELS["tool_use"], key='preferred_tool_model', help="More powerful models, better for reasoning and function calling.")

st.success(f"Settings saved! Your preferred chat model is **{st.session_state.preferred_chat_model}** and your tool model is **{st.session_state.preferred_tool_model}**.")                                                               