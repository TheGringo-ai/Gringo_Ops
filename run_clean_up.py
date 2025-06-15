import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json  # Add to imports

CLEANER = "Agent/agent.py"  # Path to your cleaning agent
ROOT_DIR = os.getcwd()      # Current project root
TARGET_EXT = ".py"          # Files to scan
SKIP_DIRS = {".venv", "__pycache__", "CompletedTasks", "UnresolvedTasks"}  # Ignore these


def collect_python_files(max_files=None):
    files = []
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(skip in dirpath.split(os.sep) for skip in SKIP_DIRS):
            continue
        for file in filenames:
            if file.endswith(TARGET_EXT):
                files.append(os.path.join(dirpath, file))
                if max_files and len(files) >= max_files:
                    return files
    return files


def clean_with_agent(filepath, dry_run=False):
    print(f"\n📄 Cleaning: {filepath}")
    if dry_run:
        return
    try:
        result = subprocess.run(
            ["python3", CLEANER, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        print(result.stdout)
        log_to_memory(filepath, result.stdout)
        if result.stderr:
            print("⚠️  Error:", result.stderr)
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timed out on: {filepath}")
    except Exception as e:
        print(f"❌ Failed to clean {filepath}: {e}")


def listen_to_agent_loop():
    print("👂 Listening to agent loop...")
    try:
        subprocess.Popen(
            ["python3", "FredFix/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Failed to launch agent loop: {e}")


def log_to_memory(filename, output):
    memory_path = os.path.join("Agent", "memory.json")
    log_entry = {
        "filename": filename,
        "output": output,
        "event": "cleaned",
    }

    try:
        if os.path.exists(memory_path):
            with open(memory_path, "r") as f:
                memory_data = json.load(f)
        else:
            memory_data = []

        memory_data.append(log_entry)

        with open(memory_path, "w") as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to log memory: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Python files with AI agent.")
    parser.add_argument("--dry-run", action="store_true", help="List files but don't clean.")
    parser.add_argument("--max-files", type=int, help="Limit number of files to clean.")
    parser.add_argument("--workers", type=int, default=4, help="Parallel jobs (default: 4)")
    args = parser.parse_args()

    print("🚀 Scanning project for Python files...")
    py_files = collect_python_files(max_files=args.max_files)
    print(f"✅ Found {len(py_files)} Python files.")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(clean_with_agent, f, args.dry_run) for f in py_files]
        for future in as_completed(futures):
            _ = future.result()

    print("\n🧹 All files processed.")

    if not args.dry_run:
        listen_to_agent_loop()
