import streamlit as st
import os
import subprocess
import psutil

st.set_page_config(page_title="GringoOps Dashboard", layout="wide")

tab1, tab2 = st.tabs(["🔧 Control Center", "📜 Logs"])

with tab1:
    st.title("🧠 GringoOps Control Center")

    def is_process_running(keyword):
    
        """Placeholder docstring for is_process_running."""        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                if any(keyword in str(arg) for arg in proc.info['cmdline']):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    st.sidebar.markdown("## 🚀 Launch External Tools")

    tools = {
        "FredFix": "FredFix/main.py",
        "CreatorAgent UI": "FredFix/core/creator_agent_ui.py",
        "BulletTrain": "BulletTrain/main.py",
        "Agent": "Agent/main.py",
        "Wizard": "wizard.py"
    }

    for name, path in tools.items():
        pid = is_process_running(path)
        status = "🟢 Running" if pid else "⚪ Not running"
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            if st.button(f"Launch {name}"):
                if not pid:
                    subprocess.Popen(["env", f"PYTHONPATH={os.getcwd()}", "streamlit", "run", path])
                else:
                    st.toast(f"{name} is already running (PID {pid})", icon="ℹ️")
        with col2:
            st.write(status)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ❌ Shutdown Running Tools")

    for name, path in tools.items():
        pid = is_process_running(path)
        if pid and st.sidebar.button(f"Kill {name}"):
            try:
                psutil.Process(pid).terminate()
                st.sidebar.success(f"{name} (PID {pid}) terminated.")
            except Exception as e:
                st.sidebar.error(f"Failed to kill {name}: {e}")

with tab2:
    st.title("📜 Log Viewer")

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_files = [f for f in os.listdir(log_dir) if f.endswith(".log") or f.endswith(".txt")]
    if log_files:
        selected_log = st.selectbox("Choose a log file:", log_files)
        with open(os.path.join(log_dir, selected_log), "r") as f:
            content = f.read()
        st.text_area("Log Content", content, height=400)
    else:
        st.info("No log files found in the logs/ directory.")