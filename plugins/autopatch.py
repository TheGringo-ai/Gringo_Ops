import os
import subprocess
from pathlib import Path

GITIGNORE_CONTENT = """
# === Python ===
__pycache__/
*.py[cod]
*.so
*.egg
*.egg-info/
.eggs/
.pytest_cache/
.ipynb_checkpoints/

# === Virtual Environments ===
.env
.env.*
.venv/
env/
venv/
.envrc
.secret
.secrets/
*.env.*

# === Node ===
node_modules/
dist/
build/
.nyc_output/
coverage/
lib-cov/
.cache/
.next/
out/
parcel-cache/
.pnp/
.pnp.js
.vite/
*.tsbuildinfo

# === Terraform ===
.terraform/
terraform.tfstate
terraform.tfstate.*

# === Firebase ===
.firebase/

# === Logs ===
*.log
*.log.*
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
*.pid

# === Editors ===
.vscode/
.idea/
*.sublime-workspace
*.sublime-project

# === System Files ===
.DS_Store
Thumbs.db
desktop.ini
ehthumbs.db
Desktop.ini

# === Secrets & Keys ===
*.pem
*.key
*.crt
*.pfx
*service-account*.json
.gcp-secret*.json
*.p12
gcp-service-account-key.json

# === LLM / Agent-Specific ===
memory/
.agent_memory.json
code_analysis_report.json
project_scan_summary.txt

# === Copilot / Misc ===
copilot*.log
copilot-error*.json
*.bak
*.swp
*.tmp
*.temp
*.orig
*.rej
*.swo
*.swn
*.swns
*.un~
*~
"""

def write_gitignore():
    path = Path(".gitignore")
    with open(path, "w") as f:
        f.write(GITIGNORE_CONTENT.strip())
    print("✅ Wrote optimized .gitignore")

def clean_and_stage():
    print("🔄 Removing cached files that should be ignored...")
    subprocess.run(["git", "rm", "-r", "--cached", "."], check=True)
    subprocess.run(["git", "add", "."], check=True)
    print("✅ Repo cleaned and restaged.")

def commit_and_push():
    print("🚀 Committing and pushing to main...")
    subprocess.run(["git", "commit", "-m", "🔥 Cleaned tracked files using optimized .gitignore"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Changes pushed to main!")

if __name__ == "__main__":
    write_gitignore()
    clean_and_stage()
    commit_and_push()