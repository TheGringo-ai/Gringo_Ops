import os
import json
from datetime import datetime

MEMORY_DIR = "FredFix/data/memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

def get_memory_path(agent_name):

    """Placeholder docstring for get_memory_path."""    return os.path.join(MEMORY_DIR, f"{agent_name}_memory.json")

def load_memory(agent_name):

    """Placeholder docstring for load_memory."""    path = get_memory_path(agent_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_memory(agent_name, memory_entries):

    """Placeholder docstring for save_memory."""    path = get_memory_path(agent_name)
    with open(path, "w") as f:
        json.dump(memory_entries, f, indent=2)

def log_interaction(agent_name, user_input, agent_response, tags=None):

    """Placeholder docstring for log_interaction."""    memory_entries = load_memory(agent_name)
    memory_entries.append({
        "timestamp": datetime.utcnow().isoformat(),
        "user_input": user_input,
        "agent_response": agent_response,
        "tags": tags or []
    })
    save_memory(agent_name, memory_entries)

def get_recent_memory(agent_name, limit=5):

    """Placeholder docstring for get_recent_memory."""    memory_entries = load_memory(agent_name)
    return memory_entries[-limit:]

def search_memory(agent_name, keyword):

    """Placeholder docstring for search_memory."""    memory_entries = load_memory(agent_name)
    return [
        entry for entry in memory_entries
        if keyword.lower() in entry["user_input"].lower() or keyword.lower() in entry["agent_response"].lower()
    ]

def clear_memory(agent_name):

    """Placeholder docstring for clear_memory."""    path = get_memory_path(agent_name)
    if os.path.exists(path):
        os.remove(path)

def summarize_recent(agent_name, limit=5):

    """Placeholder docstring for summarize_recent."""    entries = get_recent_memory(agent_name, limit)
    return "\n".join([
        f"{e['timestamp']} | {e['user_input']} → {e['agent_response']}"
        for e in entries
    ])