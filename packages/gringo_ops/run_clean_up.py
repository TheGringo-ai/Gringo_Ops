import os
import subprocess

CLEANER = "Agent/agent.py"  # Path to your cleaning agent
ROOT_DIR = os.getcwd()      # Current project root
TARGET_EXT = ".py"          # Files to scan
SKIP_DIRS = {".venv", "__pycache__", "CompletedTasks", "UnresolvedTasks"}  # Ignore these


def collect_python_files():

    """Placeholder docstring for collect_python_files."""    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # Skip virtualenv and build dirs
        if any(skip in dirpath.split(os.sep) for skip in SKIP_DIRS):
            continue
        for file in filenames:
            if file.endswith(TARGET_EXT):
                yield os.path.join(dirpath, file)


def clean_with_agent(filepath):

    """Placeholder docstring for clean_with_agent."""    print(f"\n📄 Cleaning: {filepath}")
    try:
        try:
            result = subprocess.run(
                ["python3", CLEANER, filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            print(result.stdout)
            if result.stderr:
                print("⚠️  Error:", result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timed out on: {filepath}")
    except Exception as e:
        print(f"❌ Failed to clean {filepath}: {e}")


if __name__ == "__main__":
    print("🚀 Scanning project for Python files...")
    py_files = list(collect_python_files())
    print(f"✅ Found {len(py_files)} Python files.")
    for f in py_files:
        clean_with_agent(f)

    print("\n🧹 All files processed.")
