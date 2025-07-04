from datetime import datetime
import sys

def log(msg):
    """Logs a message to the GringoOps Dev Journal."""
    with open("docs/gringoops-dev-journal.md", "a") as f:
        f.write(f"✅ {datetime.now().strftime('%Y-%m-%d %H:%M')} — {msg}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        log(message)
        print(f"Logged: {message}")
    else:
        print("Usage: python tools/gringo_checkpoint.py <message>")
