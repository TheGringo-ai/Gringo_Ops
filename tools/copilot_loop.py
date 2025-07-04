"""
GringoOps AI Auto-Repair Execution Loop
"""
import sys
from pathlib import Path
import subprocess
import json

# Add the project root to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from packages.fredfix.core.repair_engine import repair_file as run_auto_repair
from tools.validate_imports import find_python_files, get_imports, build_dependency_graph, find_cycles
from tools.validate_indentation import get_indent_violations
from tools.validate_flake8 import get_flake8_violations
from tools.gringo_checkpoint import log
from tools.gcp_scanner import get_service_accounts, get_iam_policy

def get_broken_files():
    """
    Runs the various validation tools and returns a list of files with issues.
    """
    # For now, we'll rely on the indentation checker to find most syntax errors
    return []

def update_gcp_memory():
    """
    Scans for GCP service accounts and their permissions and updates the agent's memory.
    """
    log("🧠 Updating GCP memory...")
    accounts = get_service_accounts()
    gcp_memory = {"service_accounts": {}}
    for account in accounts:
        email = account.get("email")
        if email:
            policy = get_iam_policy(email)
            gcp_memory["service_accounts"][email] = {
                "details": account,
                "policy": policy
            }
    
    # We'll save this to a new memory file for now
    with open("memory/gcp_memory.json", "w") as f:
        json.dump(gcp_memory, f, indent=2)
    log("✅ GCP memory updated.")

def repair_everything():
    """
    The main function for the auto-repair loop.
    """
    files_to_fix = list(set(get_broken_files() + get_indent_violations() + get_flake8_violations()))
    print(f"🔧 {len(files_to_fix)} files to fix")

    for f in files_to_fix:
        result = run_auto_repair(f)
        print(result)
        log(f"🛠️ {result}")

def run_tests():
    """
    Runs the test suite to ensure that everything is working correctly.
    """
    print("\n--- Running Tests ---")
    result = subprocess.run(["pytest", "--tb=short", "-q"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ All tests passed.")
        log("✅ All tests passed.")
    else:
        print("❌ Some tests failed.")
        log("❌ Some tests failed.")
        print(result.stdout)
        print(result.stderr)

if __name__ == "__main__":
    update_gcp_memory()
    repair_everything()
    run_tests()
