import streamlit as st
import subprocess
import os

st.set_page_config(page_title="🧠 GringoOps Hub", layout="wide")

st.title("🧠 GringoOps Productivity Hub")
st.markdown("Launch any of your Gringo tools from one unified interface.")

TOOLS = {
    "🎙️ Gringo Voice Strip": "~/Projects/GringoOps/GringoVoiceStrip/main.py",
    "📋 LineSmart Trainer": "~/Projects/GringoOps/LineSmart/main.py",
    "🛠️ ChatterFix CMMS": "~/Projects/GringoOps/ChatterFix/main.py",
    "🧬 Agent": "~/Projects/GringoOps/Agent/main.py",
    "🔧 FredFix Dev Agent": "~/Projects/GringoOps/FredFix/main.py",
    "🚄 Bullet Train": "~/Projects/GringoOps/BulletTrain/main.py"
}

col1, col2 = st.columns(2)

with col1:
    selected_tool = st.selectbox("Select a tool to launch", list(TOOLS.keys()))

with col2:
    if st.button("🚀 Launch Tool"):
        tool_path = os.path.expanduser(TOOLS[selected_tool])
        if os.path.exists(tool_path):
            subprocess.Popen(["streamlit", "run", tool_path])
            st.success(f"{selected_tool} launched!")
        else:
            st.error(f"Tool not found at path: {tool_path}")