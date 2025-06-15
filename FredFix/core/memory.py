<file name=FredFix/fredfix_ui.py>import streamlit as st
from FredFix.core.memory import auto_learn

# ... existing Streamlit UI code ...

# Example UI block with buttons
if st.button("Clear Memory"):
    # Clear memory logic here
    pass

if st.button("Run Auto Learn"):
    st.success(auto_learn("fredfix"))

# ... rest of the UI code ...</file>

<file name=FredFix/main.py>from FredFix.core.memory import auto_learn

# ... existing agent loop and interaction handling code ...

# After agent logs the interaction or processes the response
auto_learn("fredfix")

# ... rest of the main.py code ...</file>
# Add a simple auto_learn function for UI and main.py functionality

import os
import datetime

MEMORY_DIR = "memory"

def get_memory_path(agent_name: str) -> str:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{agent_name}_memory.txt")

def save_memory(agent_name: str, user_input: str, agent_output: str, metadata: dict = None):
    memory_path = get_memory_path(agent_name)
    timestamp = datetime.datetime.now().isoformat()
    meta_block = "\n".join([f"{k}: {v}" for k, v in (metadata or {}).items()])
    log_entry = f"[{timestamp}]\nUser: {user_input}\nAgent: {agent_output}\n{meta_block}\n{'='*40}\n"
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

def get_memory(agent_name: str) -> str:
    memory_path = get_memory_path(agent_name)
    if not os.path.exists(memory_path):
        return ""
    with open(memory_path, "r", encoding="utf-8") as f:
        return f.read()

def get_latest_memory(agent_name: str) -> str:
    memory_path = get_memory_path(agent_name)
    if not os.path.exists(memory_path):
        return ""
    with open(memory_path, "r", encoding="utf-8") as f:
        logs = f.read().strip().split("="*40)
        return logs[-2].strip() if len(logs) > 1 else logs[-1].strip()

def clear_memory(agent_name: str):
    memory_path = get_memory_path(agent_name)
    if os.path.exists(memory_path):
        os.remove(memory_path)

def auto_learn(agent_name: str):
    memory_path = get_memory_path(agent_name)
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] Auto-learn triggered for {agent_name}\n{'='*40}\n")
    return f"Memory updated for {agent_name}"