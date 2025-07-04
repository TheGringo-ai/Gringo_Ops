import streamlit as st
import os
import subprocess
import json
from pathlib import Path
import psutil
import sys

# --- Page Configuration ---
st.set_page_config(page_title="GringoOps God Mode", layout="wide")

# --- Helper Functions ---
def load_json(file_path):
    """Safely loads a JSON file."""
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# --- Main UI ---
st.title("🤖 GringoOps God Mode")
st.caption("The central command center for the GringoOps AI agent.")

# --- Agent Control Tab ---
st.header("🚀 Agent Control")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Trigger Review Agent")
    scope = st.text_input("Scope (directory to scan)", value=".")
    auto_fix = st.checkbox("Enable Auto-Fix (God Mode)", value=True)
    memory_backend = st.selectbox("Memory Backend", ["json", "firestore"])
    
    if st.button("Run Agent", type="primary"):
        command = [
            "python3", "Gringo_Ops/review_agent.py",
            "--scope", scope,
            "--memory-backend", memory_backend
        ]
        if auto_fix:
            command.append("--auto-fix")
            
        with st.spinner("Running GringoOps Agent..."):
            try:
                process = subprocess.run(command, capture_output=True, text=True, check=True)
                st.success("Agent run completed successfully!")
                st.code(process.stdout)
                if process.stderr:
                    st.warning("Agent produced the following warnings:")
                    st.code(process.stderr)
            except subprocess.CalledProcessError as e:
                st.error(f"Agent run failed with exit code {e.returncode}")
                st.code(e.stdout)
                st.code(e.stderr)

with col2:
    st.subheader("Agent Status")
    st.info("Status monitoring will be implemented here.")

# --- Analysis, Memory & Launchpad Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis Report", "🧠 Agent Memory", "🛠️ FredFix Agent", "🚀 Launchpad"])

with tab1:
    st.header("Code Analysis Report")
    report_path = Path("code_analysis_report.json")
    report_data = load_json(report_path)
    
    if report_data:
        st.json(report_data)
    else:
        st.info("No analysis report found. Run the agent to generate one.")

with tab2:
    st.header("Agent Memory")
    
    st.subheader("Local Memory (`.agent_memory.json`)")
    local_memory_path = Path(".agent_memory.json")
    local_memory_data = load_json(local_memory_path)
    if local_memory_data:
        st.json(local_memory_data)
    else:
        st.info("No local memory file found.")
        
    st.subheader("Firestore Memory")
    try:
        from Gringo_Ops.tools.memory import FirestoreMemoryBackend
        
        gcp_project_id = st.secrets.get("GCP_PROJECT_ID")
        if gcp_project_id:
            firestore_memory = FirestoreMemoryBackend(project_id=gcp_project_id)
            firestore_data = firestore_memory._get_memory_doc()
            if firestore_data:
                st.json(firestore_data)
            else:
                st.info("No data found in Firestore memory for this project.")
        else:
            st.warning("GCP_PROJECT_ID secret not found. Cannot connect to Firestore.")
            
    except ImportError:
        st.error("Could not import FirestoreMemoryBackend. Make sure the `Gringo_Ops` package is in your Python path.")
    except Exception as e:
        st.error(f"An error occurred while fetching Firestore memory: {e}")

with tab3:
    st.header("Interact with the FredFix Agent")
    
    # Import the agent
    try:
        from packages.fredfix.core.agent import FredFixAgent
        
        if 'fredfix_agent' not in st.session_state:
            st.session_state.fredfix_agent = FredFixAgent()
            
        agent = st.session_state.fredfix_agent

        user_input = st.text_input("Enter a command or prompt for FredFix:")

        if st.button("Run FredFix"):
            if user_input:
                with st.spinner("FredFix is thinking..."):
                    result = agent.run_agent(user_input)
                    st.write("### Agent Output")
                    st.json(result)
            else:
                st.warning("Please enter a command or prompt.")

    except ImportError:
        st.error("Could not import FredFixAgent. Make sure the `packages` directory is in your Python path.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

with tab4:
    st.header("GringoOps Tool Launcher")

    if st.button("🛠 Run Full Code Repair", type="primary"):
        with st.spinner("Running full code repair..."):
            try:
                from tools.copilot_loop import repair_everything
                # This is a long-running process, so we might want to handle this differently in the future
                repair_everything()
                st.success("Full code repair process completed.")
            except Exception as e:
                st.error(f"Full code repair failed: {e}")

    if st.button("🛠 Run Full Auto-Repair"):
        with st.spinner("Running agent loop..."):
            result = subprocess.run(["python", "tools/copilot_loop.py"], capture_output=True, text=True)
            st.code(result.stdout)

    with st.expander("📓 Dev Journal"):
        try:
            with open("docs/gringoops-dev-journal.md") as f:
                st.code(f.read())
        except FileNotFoundError:
            st.warning("Dev journal not found.")

    with st.expander("📊 Repair Summary"):
        try:
            with open("docs/gringoops-dev-journal.md") as f:
                logs = f.readlines()[-10:]  # show last 10 entries
                for line in logs:
                    st.markdown(f"- {line.strip()}")
        except FileNotFoundError:
            st.warning("Dev journal not found.")

    def is_process_running(keyword):
        """Checks if a process with a given keyword in its command line is running."""
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and any(keyword in str(arg) for arg in cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError, TypeError):
                continue
            except Exception as e:
                st.warning(f"Process check error: {e}")
                continue
        return None

    tools = {
        "FredFix": "pages/1_🛠️_FredFix.py",
        "Wizard": "pages/2_Wizard.py",
        "CreatorAgent": "pages/3_Creator_Agent.py",
        "BulletTrain": "pages/4_BulletTrain.py",
        "ChatterFix": "pages/6_ChatterFix.py",
        "Asset Management": "pages/7_Asset_Management.py",
        "Parts Management": "pages/8_Parts_Management.py",
    }

    for name, path in tools.items():
        pid = is_process_running(path)
        status = "🟢 Running" if pid else "⚪ Not running"
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{name}**")
        with col2:
            if st.button(f"Launch {name}", key=f"launch_{name}"):
                if not pid:
                    if os.path.exists(path):
                        try:
                            subprocess.Popen([sys.executable, "-m", "streamlit", "run", path], env={**os.environ, "PYTHONPATH": os.getcwd()})
                            st.success(f"Launched {name} in a new process.")
                        except Exception as e:
                            st.error(f"Failed to launch {name}: {e}")
                    else:
                        st.error(f"File not found: {path}")
                else:
                    st.toast(f"{name} is already running (PID {pid})", icon="ℹ️")
        with col3:
            if pid and st.button(f"Kill {name}", key=f"kill_{name}"):
                try:
                    psutil.Process(pid).terminate()
                    st.success(f"{name} (PID {pid}) terminated.")
                except Exception as e:
                    st.error(f"Failed to kill {name}: {e}")
            
        st.write(f"Status: {status}")
        st.markdown("---")

# --- Debug Info Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Debug Info")
st.sidebar.write(f"Python: {__import__('platform').python_version()}")
st.sidebar.write(f"Working Dir: {os.getcwd()}")
try:
    st.sidebar.write(f"Secrets loaded: {list(st.secrets.keys())}")
except Exception as e:
    st.sidebar.warning(f"Could not load secrets: {e}")