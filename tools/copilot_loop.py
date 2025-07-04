"""
GringoOps AI Auto-Repair Execution Loop
"""
import sys
from pathlib import Path
import subprocess

# Add the tools directory to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
# Add the project root to the Python path
sys.path.append(str(current_dir.parent))

from packages.fredfix.core.repair_engine import repair_file
from tools.validate_imports import find_python_files, get_imports, build_dependency_graph, find_cycles
from tools.validate_indentation import get_indent_violations
from tools.validate_flake8 import get_flake8_violations
from tools.repair_engine import run_auto_repair
from tools.gringo_checkpoint import log

def get_broken_files():
    """
    A placeholder for a function that returns a list of files with import errors.
    For now, it returns an empty list.
    """
    return []

def get_indent_violations():
    """
    A placeholder for a function that returns a list of files with indentation errors.
    For now, it returns an empty list.
    """
    # In the future, this could be a more sophisticated check
    # For now, we'll rely on the indentation checker to find most syntax errors
    return []

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
    """Runs pytest and reports the results."""
    print("\n--- Running Tests ---")
    try:
        result = subprocess.run(["pytest"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tests passed after repairs.")
            log("✅ Tests passed after repairs.")
        else:
            print("❌ Tests FAILED after repairs:")
            print(result.stdout)
            log("❌ Tests FAILED after repairs.")
    except FileNotFoundError:
        print("Error: pytest is not installed or not in the system's PATH.")
        log("Error: pytest is not installed or not in the system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred while running tests: {e}")
        log(f"An unexpected error occurred while running tests: {e}")

if __name__ == "__main__":
    repair_everything()
    run_tests()
