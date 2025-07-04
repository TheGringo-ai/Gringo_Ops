"""
GringoOps AI Auto-Repair Execution Loop
"""
from tools.repair_engine import run_auto_repair
from tools.validate_imports import get_broken_files
from tools.validate_indentation import get_indent_violations
from tools.gringo_checkpoint import log

def repair_everything():
    """
    The main function for the auto-repair loop.
    """
    files = list(set(get_broken_files() + get_indent_violations()))
    print(f"🔍 {len(files)} files to inspect")

    for f in files:
        result = run_auto_repair(f)
        print(result)
        log(f"🛠️ {result}")

if __name__ == "__main__":
    repair_everything()
