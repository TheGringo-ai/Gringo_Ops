import streamlit as st
from BulletTrain.services import run_auto_repair, sync_agents, transcribe_backlog
from FredFix.core.memory_manager import MemoryManager

st.set_page_config(page_title="🚄 Bullet Train Launcher", layout="wide")

memory = MemoryManager()

st.title("🚄 GringoOps Bullet Train")
st.markdown("Launch rapid-fire automation tools and diagnostics here.")

st.subheader("🔧 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧠 Run Auto-Repair"):
        try:
            result = run_auto_repair()
            st.success(f"Auto-repair finished: {result}")
            memory.log_event("Tool run", {
                "tool": "auto_repair",
                "result": str(result)
            })
        except Exception as e:
            st.error(f"Error during auto-repair: {str(e)}")

with col2:
    if st.button("📦 Sync Agents"):
        try:
            result = sync_agents()
            st.success(f"Agent sync complete: {result}")
            memory.log_event("Tool run", {
                "tool": "sync_agents",
                "result": str(result)
            })
        except Exception as e:
            st.error(f"Error during agent sync: {str(e)}")

with col3:
    if st.button("📝 Transcribe Backlog"):
        try:
            result = transcribe_backlog()
            st.success(f"Transcription complete: {result}")
            memory.log_event("Tool run", {
                "tool": "transcribe_backlog",
                "result": str(result)
            })
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")

st.subheader("📊 System Diagnostics (coming soon)")
st.info("Live logs and status dashboards will appear here.")

# Agent Memory Section
st.subheader("🔁 Agent Memory")
if st.button("🔁 View Agent Memory"):
    mem_log = memory.load_memory()
    with st.expander("🧠 Memory Log"):
        st.code(f"Session ID: {memory.session_id}\n\n{mem_log}", language="markdown")

# Plugin Loader Section
import importlib
import os

st.subheader("🧩 Load an Extension")

plugin_files = [f.replace(".py", "") for f in os.listdir("BulletTrain/plugins") if f.endswith(".py")]

selected_plugin = st.selectbox("Choose Plugin", plugin_files)
if st.button("🚀 Launch Plugin"):
    try:
        plugin = importlib.import_module(f"BulletTrain.plugins.{selected_plugin}")
        plugin.run()
    except Exception as e:
        st.error(f"Failed to launch plugin: {str(e)}")