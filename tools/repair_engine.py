from tools.openai_review import repair_all_code
import os
import json

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
            repair_all_code(file_path)
            return f"✅ Repaired {file_path}"
        else:
            return repair_all_code(repo_path=os.path.expanduser("~/Projects/GringoOps"))
    except Exception as e:
        return f"❌ Failed: {e}"