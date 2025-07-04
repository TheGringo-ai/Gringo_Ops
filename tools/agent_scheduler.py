import subprocess
import sys
from pathlib import Path

# Add project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from tools.gringo_checkpoint import log

def run_scheduled_repair():
    """
    Runs the main repair loop and logs the outcome.
    This is intended to be called by a scheduler like cron or a GitHub Action.
    """
    log("🤖 Starting scheduled auto-repair cycle...")
    try:
        result = subprocess.run(
            ["python3", "tools/copilot_loop.py"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✅ Scheduled auto-repair cycle completed successfully.")
        print(result.stdout)
        if result.stderr:
            log(f"⚠️ Repair cycle finished with warnings:\n{result.stderr}")
            print("--- Warnings ---")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        log(f"❌ Scheduled auto-repair cycle FAILED.\nExit Code: {e.returncode}\nOutput:\n{e.stdout}\n{e.stderr}")
        print(f"--- ❌ Repair cycle FAILED ---")
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    run_scheduled_repair()
