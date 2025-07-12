import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # Adds GringoOps to sys.path
import os
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEMORY_DIR = str(BASE_DIR / "memory_logs")

def get_memory_path(agent_name: str) -> str:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{agent_name}_memory.txt")

def save_memory(agent_name: str, user_input: str, agent_output: str, metadata: dict = None, verified: bool = False):
    memory_path = get_memory_path(agent_name)
    print(f"[MemoryManager] Writing to {memory_path}")
    timestamp = datetime.datetime.now().isoformat()
    meta_block = "\n".join([f"{k}: {v}" for k, v in (metadata or {}).items()])
    log_entry = f"[{timestamp}] ✅={verified}\nUser: {user_input}\nAgent: {agent_output}\n{meta_block}\n{'='*40}\n"
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

def get_memory(agent_name: str) -> str:
    memory_path = get_memory_path(agent_name)
    print(f"[MemoryManager] Reading from {memory_path}")
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
    timestamp = datetime.datetime.now().isoformat()
    user_input = "auto_learn"
    agent_output = f"Auto-learn triggered at {timestamp}"
    metadata = {"event": "auto_learn"}
    save_memory(agent_name, user_input, agent_output, metadata)
    return f"Memory updated for {agent_name} at {timestamp}"
def get_verified_memory(agent_name: str) -> list:
    memory_path = get_memory_path(agent_name)
    if not os.path.exists(memory_path):
        return []
    with open(memory_path, "r", encoding="utf-8") as f:
        logs = f.read().strip().split("="*40)
        verified_pairs = []
        for log in logs:
            if "✅=True" in log:
                user_line = next((l for l in log.splitlines() if l.startswith("User: ")), None)
                agent_line = next((l for l in log.splitlines() if l.startswith("Agent: ")), None)
                if user_line and agent_line:
                    verified_pairs.append((user_line[6:], agent_line[7:]))
        return verified_pairs