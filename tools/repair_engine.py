from tools.openai_review import repair_file
import os
import json
import subprocess

SKIP_LIST = "memory/skip_list.json"

def should_skip(file_path):
    if not os.path.exists(SKIP_LIST):
        return False
    with open(SKIP_LIST) as f:
        data = json.load(f)
    return any(skip in file_path for skip in data.get("skip", []))

def run_auto_repair(file_path=None):
    """Repair one file or the full repo, skipping known-bad files."""
    try:
        if file_path:
            if should_skip(file_path):
                return f"⏩ Skipped {file_path}"
            # First, run ruff to fix what it can
            subprocess.run(["ruff", "check", file_path, "--fix"], check=True)
            # Then, run black to format the file
            subprocess.run(["black", file_path], check=True)
            return f"✅ Repaired {file_path}"
        else:
            # If no file is specified, repair the whole project
            subprocess.run(["ruff", "check", ".", "--fix"], check=True)
            subprocess.run(["black", "."], check=True)
            return "✅ Repaired all files."
    except Exception as e:
        return f"❌ Failed: {e}"