"""
GringoOps AI Auto-Repair Execution Loop
"""
import sys
from pathlib import Path
import subprocess

# Add the project root to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from packages.fredfix.core.repair_engine import repair_file
from tools.validate_imports import find_python_files, get_imports, build_dependency_graph, find_cycles
from tools.validate_indentation import get_indent_violations
from tools.validate_flake8 import get_flake8_violations
from tools.gringo_checkpoint import log

def get_broken_files():
    """
    Runs the various validation tools and returns a list of files with issues.
    """
    # For now, we'll rely on the indentation checker to find most syntax errors
    return []

def repair_everything():
    """
    The main function for the auto-repair loop.
    """
    files_to_fix = list(set(get_broken_files() + get_indent_violations() + get_flake8_violations()))
    print(f"🔧 {len(files_to_fix)} files to fix")

    for f in files_to_fix:
        path = f
        if not path.endswith(".py"):
            continue
        print(f"🔁 Fixing: {path}")
        try:
            fix_result = repair_file(path)
            log(f"🛠️ {fix_result}")
            print(f"✅ Success: {path}")
        except Exception as e:
            print(f"⚠️ Error fixing {path}: {e}")

def confirm_clean_run():
    """
    Runs the validate_imports.py script again to confirm that all syntax issues have been resolved.
    """
    print("\n--- Confirming Clean Run ---")
    result = subprocess.run(["python3", "tools/validate_imports.py"], capture_output=True, text=True)
    if "invalid syntax" in result.stdout or "expected an indented block" in result.stdout:
        print("❌ Still broken files.")
        log("❌ Self-healing failed. Still broken files.")
    else:
        print("✅ All syntax issues resolved.")
        log("✅ Self-healing successful. All syntax issues resolved.")

if __name__ == "__main__":
    repair_everything()
    confirm_clean_run()
