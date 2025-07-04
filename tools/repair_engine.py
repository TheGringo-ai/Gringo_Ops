from packages.fredfix.core.agent import repair_all_code
import os

def run_auto_repair():
    """Runs the auto-repair script on the GringoOps codebase."""
    try:
        repair_all_code(repo_path=os.path.expanduser("~/Projects/GringoOps"))
        return "Auto-repair complete for GringoOps codebase."
    except Exception as e:
        return f"Auto-repair failed: {e}"