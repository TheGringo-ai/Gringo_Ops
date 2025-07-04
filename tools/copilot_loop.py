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
from tools.gringo_checkpoint import log

def get_invalid_syntax_files():
    """
    Runs the validate_imports.py script and returns a list of files with syntax errors.
    """
    result = subprocess.run(
        ["python3", "tools/validate_imports.py"],
        capture_output=True,
        text=True
    )
    return [
        line.split(":")[0].strip()
        for line in result.stdout.splitlines()
        if "invalid syntax" in line or "expected an indented block" in line
    ]

def repair_everything():
    """
    The main function for the auto-repair loop.
    """
    broken_files = get_invalid_syntax_files()
    print(f"🔧 {len(broken_files)} files to fix")

    for path in broken_files:
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
