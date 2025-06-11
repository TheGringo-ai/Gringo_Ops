import argparse
import subprocess
import os
from pathlib import Path
import sys
import socket
import datetime

ROOT_DIR = Path(__file__).resolve().parents[1]  # /GringoOps
DEFAULT_UI_PATH = ROOT_DIR / "ChatterFix" / "frontend" / "dashboard.py"
GEMINI_REVIEW_PATH = ROOT_DIR / "GeminiReviewTasks"

def scan_and_clean():
    print("🧠 Launching deep cleanup agent...")
    print("🚀 Scanning project for Python files...")

    # Exclude files that match command-line arguments or options
    cli_args = set(arg for arg in sys.argv[1:] if not arg.endswith(".py") and not arg.startswith("--"))
    py_files = [
        f for f in ROOT_DIR.rglob("*.py")
        if str(f) not in cli_args and not any(part in [".venv", "__pycache__"] for part in f.parts)
    ]
    print(f"✅ Found {len(py_files)} Python files.\n")

    for file in py_files:
        if not file.exists():
            print(f"❌ Skipping invalid file: {file}")
            continue
        print(f"📄 Cleaning: {file}")
        try:
            subprocess.run(["python3", str(file)], check=True)
        except Exception as e:
            print(f"❌ Failed to clean {file}: {e}")

    print("\n🧹 All files processed.")
    print("✅ Agent cleanup complete.")


def find_free_port(start=8501, max_tries=10):
    port = start
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
            port += 1
    raise RuntimeError("No available port found for Streamlit.")

def launch_dashboard(custom_ui_path=None):
    if custom_ui_path:
        ui_path = custom_ui_path
        print(f"📁 Using UI file: {ui_path}")
        if not ui_path.exists():
            print(f"❌ Dashboard UI not found at {ui_path}")
            return
        port = find_free_port()
        print(f"🚀 Launching dashboard on port {port}...")
        subprocess.run(["streamlit", "run", str(ui_path), "--server.port", str(port)])
    else:
        import streamlit.web.bootstrap
        print("🚀 Launching enhanced dashboard module...")
        streamlit.web.bootstrap.run(
            enhanced_ui_dashboard, "", [], {}, None, None
        )

def repair_code(ci_mode=False, review_mode=False):
    print("🔧 Repair mode triggered.")
    print(f"📁 Reviewing Gemini tasks in: {GEMINI_REVIEW_PATH}")
    if not GEMINI_REVIEW_PATH.exists():
        print("⚠️ Gemini review folder not found. Skipping enhancement phase.")
        return

    print("🤖 Integrating Gemini and OpenAI suggestions into code...")
    review_files = list(GEMINI_REVIEW_PATH.glob("*.txt"))

    # Load API keys from environment
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    # TODO: fallback to Secret Manager if needed

    # Import OpenAI and Gemini APIs
    openai = None
    try:
        import openai as openai_mod
        openai = openai_mod
        if openai_api_key:
            openai.api_key = openai_api_key
    except Exception:
        pass
    genai = None
    try:
        import google.generativeai as genai_mod
        genai = genai_mod
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
    except Exception:
        pass

    def apply_ai_suggestions(file_path, suggestion, api_source="openai"):
        # api_source: "openai" or "gemini"
        try:
            with open(file_path, "r") as f:
                original_code = f.read()
            prompt = f"""You are an expert Python developer. Here's a suggestion for improvement:
Suggestion: {suggestion}

Apply this to the following file content:

{original_code}

Return the full improved version of the file. Don't add explanations or comments outside the code.
"""
            if api_source == "openai" and openai:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful and precise code refactoring assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                improved_code = response['choices'][0]['message']['content']
                return improved_code
            elif api_source == "gemini" and genai:
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                response = model.generate_content(prompt)
                # Some Gemini responses may include explanations; try to extract code block
                content = response.text
                # Try extracting code if present in triple backticks
                import re
                match = re.search(r"```(?:python)?\n(.*?)\n```", content, re.DOTALL)
                if match:
                    improved_code = match.group(1)
                else:
                    improved_code = content
                return improved_code
            else:
                print(f"❌ No valid API selected or configured for {api_source}")
                return None
        except Exception as e:
            print(f"❌ Error applying suggestion to {file_path} with {api_source}: {e}")
            return None

    # Review mode: print suggestions only, do not apply
    if review_mode:
        for review_file in review_files:
            try:
                with open(review_file, "r") as f:
                    content = f.read()
                print(f"📘 {review_file.name}:\n{'-'*40}\n{content.strip()}\n{'-'*40}\n")
            except Exception as e:
                print(f"❌ Error reading {review_file.name}: {e}")
        print("✅ Review mode complete.")
        return

    # New logic: Attempt to match suggestions to filenames and enhance with both APIs
    for review_file in review_files:
        try:
            with open(review_file, "r") as f:
                suggestion = f.read()
            for py_file in ROOT_DIR.rglob("*.py"):
                if any(part in [".venv", "__pycache__"] for part in py_file.parts):
                    continue
                if py_file.name in review_file.name:
                    # Try Gemini first, then OpenAI fallback
                    gemini_result = apply_ai_suggestions(py_file, suggestion, api_source="gemini") if genai else None
                    openai_result = apply_ai_suggestions(py_file, suggestion, api_source="openai") if openai else None
                    improved_code = None
                    if gemini_result and gemini_result.strip():
                        improved_code = gemini_result
                        source_used = "Gemini"
                    elif openai_result and openai_result.strip():
                        improved_code = openai_result
                        source_used = "OpenAI"
                    else:
                        print(f"❌ Both Gemini and OpenAI failed for {py_file}")
                        continue
                    # Write backup and improved code
                    backup_path = py_file.with_suffix(py_file.suffix + ".bak")
                    try:
                        py_file.rename(backup_path)
                    except Exception:
                        pass
                    with open(py_file, "w") as f:
                        f.write(improved_code)
                    print(f"✅ Applied AI enhancement to {py_file} using {source_used}")
        except Exception as e:
            print(f"❌ Error processing suggestion file {review_file.name}: {e}")

    print("✅ Review phase complete.")

    try:
        repair_dir = ROOT_DIR / ".repair_history"
        repair_dir.mkdir(exist_ok=True)
        with open(repair_dir / f"repair_log_{datetime.datetime.now().isoformat()}.md", "w") as log:
            log.write("## AI Repair Log\n\n")
            log.write(f"Total files reviewed: {len(review_files)}\n")
    except Exception as e:
        print(f"⚠️ Failed to write repair log: {e}")


# --- Enhanced UI Dashboard ---
def enhanced_ui_dashboard():
    import streamlit as st
    import pandas as pd
    import datetime

    st.set_page_config(layout="wide")
    st.title("🛠️ GringoOps Unified Dashboard")
    tabs = st.tabs(["📋 Work Orders", "👷 Technicians", "📆 Calendar", "🧠 Gemini AI Reviews"])

    with tabs[0]:
        st.header("📋 All Work Orders")
        st.write("Placeholder for all work orders table or grid view.")
        # TODO: Load work orders from database or file

    with tabs[1]:
        st.header("👷 Technician Overview")
        st.write("Placeholder for technician assignments and load balancing UI.")

    with tabs[2]:
        st.header("📆 Calendar View")
        today = datetime.date.today()
        st.date_input("Select date", today)

    with tabs[3]:
        st.header("🧠 Gemini AI Review Queue")
        st.write("Automatically processed Gemini review files:")
        review_files = list(GEMINI_REVIEW_PATH.glob("*.txt")) if GEMINI_REVIEW_PATH.exists() else []
        for f in review_files:
            with open(f) as r:
                st.expander(f.name).write(r.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FredFix Agent")
    parser.add_argument("--launch-ui", action="store_true", help="Launch Streamlit dashboard UI")
    parser.add_argument("--ui-path", type=str, help="Path to custom Streamlit UI file")
    parser.add_argument("--repair", action="store_true", help="Run AI-powered repair routines")
    parser.add_argument("--ci", action="store_true", help="Run in CI/CD mode (headless repair + cleanup)")
    parser.add_argument("--review", action="store_true", help="Print AI suggestions only, do not apply changes")
    args = parser.parse_args()

    if args.launch_ui:
        launch_dashboard(Path(args.ui_path) if args.ui_path else None)
    elif args.ci:
        print("🤖 Running in CI/CD mode (repair + cleanup, headless)...")
        repair_code(ci_mode=True)
        scan_and_clean()
    elif args.review:
        repair_code(review_mode=True)
    elif args.repair:
        repair_code()
    elif len(sys.argv) == 1:
        scan_and_clean()
    else:
        print("⚠️ Unrecognized argument or missing flag. Use --help to see available options.")