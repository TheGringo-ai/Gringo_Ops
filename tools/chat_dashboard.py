import streamlit as st
import json
import os
from pathlib import Path
import subprocess
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.gringo_checkpoint import load_journal, log

def load_memory():
    """Safely loads the agent's memory."""
    memory_path = Path("packages/fredfix/core/agent_memory.json")
    if memory_path.exists():
        with open(memory_path, 'r') as f:
            return json.load(f)
    return {}

st.set_page_config(page_title="GringoOps Chat", layout="wide")

# --- Sidebar ---
st.sidebar.title("GringoOps Intelligence")

with st.sidebar.expander("🧠 Agent Memory", expanded=False):
    try:
        memory = load_memory()
        st.markdown("#### Memory Contents:")
        st.json(memory, expand_nested=True)
    except Exception as e:
        st.error(f"Failed to load memory: {e}")

with st.sidebar.expander("📓 Dev Journal Logs", expanded=False):
    logs = load_journal()
    for entry in reversed(logs[-10:]):
        st.markdown(f"**🗂️ File:** `{entry.get('file', 'unknown')}`")
        st.markdown(f"🔧 **Action:** {entry.get('action', '—')}")
        st.markdown(f"🕒 {entry.get('timestamp', '—')}")
        st.markdown("---")

# --- Main Chat Interface ---
st.title("🤖 GringoOps Chat Command Center")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I do for you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # This is where you would handle the command
        # For now, we'll just echo it back
        response = f"✅ Operation complete:\n\n```\n{prompt}\n```"
        
        message_placeholder.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Repair History Dashboard ---
with st.expander("🪞 Full Repair History", expanded=False):
    logs = load_journal()
    for entry in reversed(logs):
        st.markdown(f"#### 📂 `{entry.get('file', 'unknown')}`")
        st.code(entry.get("diff", "No diff found."), language="diff")
        st.markdown("---")
