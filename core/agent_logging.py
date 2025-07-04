import datetime
import json
import os

LOG_FILE = os.getenv("AGENT_LOG_FILE", "agent_interactions.log")


def log_interaction(agent, prompt, response, user=None, context=None):
    """Placeholder docstring for log_interaction."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "agent": agent,
        "prompt": prompt,
        "response": response,
        "user": user,
        "context": context or {},
    }
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")


def get_recent_logs(n=20):
    """Placeholder docstring for get_recent_logs."""
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-n:]
            return [json.loads(line) for line in lines]
    except Exception:
        return []
