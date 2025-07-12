import os
import json
from datetime import datetime
import platform
import socket

session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
memory_path = os.path.expanduser("~/Projects/GringoOps/shared_memory.json")

def log_event(event_type, data):
    log = {
        "timestamp": datetime.now().isoformat(),
        "session": session_id,
        "event": event_type,
        "data": data,
        "host": socket.gethostname(),
        "app": "ChatterFix"
    }
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.append(log)
    with open(memory_path, "w") as f:
        json.dump(history, f, indent=2)

# Log app startup event
log_event("App started", {"status": "ChatterFix launched"})