from tools.repair_engine import repair_all_code
import os

def run_auto_repair():
    try:
        repair_all_code(repo_path=os.path.expanduser("~/Projects/GringoOps"))
        return "Auto-repair complete for GringoOps codebase."
    except Exception as e:
        return f"Auto-repair failed: {e}"