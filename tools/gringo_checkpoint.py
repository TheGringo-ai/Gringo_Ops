from datetime import datetime
import json
import os
import sys

JOURNAL_PATH = "docs/dev_journal.json"

def load_journal():
    """Loads the dev journal from the JSON file."""
    if not os.path.exists(JOURNAL_PATH):
        return []
    with open(JOURNAL_PATH, "r") as f:
        return json.load(f)

def log(msg, action="log", file="system", diff=""):
    """Logs a message to the GringoOps Dev Journal."""
    journal = load_journal()
    entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "message": msg,
        "action": action,
        "file": file,
        "diff": diff
    }
    journal.append(entry)
    with open(JOURNAL_PATH, "w") as f:
        json.dump(journal, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        log(message)
        print(f"Logged: {message}")
    else:
        print("Usage: python tools/gringo_checkpoint.py <message>")
