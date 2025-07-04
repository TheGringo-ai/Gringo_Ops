from datetime import datetime

def log(msg):
    with open("docs/gringoops-dev-journal.md", "a") as f:
        f.write(f"✅ {datetime.now().strftime('%Y-%m-%d %H:%M')} — {msg}\n")
