


import logging
import os
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

def repair_all_code(repo_path="."):
    """
    Scans all Python files in the repo and attempts to auto-format and commit fixes.
    """
    logging.info(f"🔍 Scanning for Python files in: {repo_path}")

    repaired_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py") and "venv" not in root and "__pycache__" not in root:
                full_path = os.path.join(root, file)
                try:
                    subprocess.run(["black", full_path], check=True)
                    repaired_files.append(full_path)
                    logging.info(f"✅ Repaired: {full_path}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"❌ Failed to repair {full_path}: {e}")

    if repaired_files:
        subprocess.run(["git", "add"] + repaired_files)
        subprocess.run(["git", "commit", "-m", f"🤖 Auto-repair: formatted {len(repaired_files)} file(s)"])
        logging.info(f"💾 Commit complete: formatted {len(repaired_files)} file(s)")
    else:
        logging.info("✅ No changes needed. Repo is clean.")