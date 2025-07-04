import streamlit as st
import os
import subprocess
import json
from pathlib import Path

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

# --- Analysis & Memory Tabs ---
tab1, tab2 = st.tabs(["📊 Analysis Report", "🧠 Agent Memory"])

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
    st.warning("Firestore memory viewing is not yet implemented in the dashboard.")

# --- Debug Info Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Debug Info")
st.sidebar.write(f"Python: {__import__('platform').python_version()}")
st.sidebar.write(f"Working Dir: {os.getcwd()}")
try:
    st.sidebar.write(f"Secrets loaded: {list(st.secrets.keys())}")
except Exception as e:
    st.sidebar.warning(f"Could not load secrets: {e}")