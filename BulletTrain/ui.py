

import streamlit as st
import subprocess

# Page setup for embedded use
st.set_page_config(page_title="🚂 BulletTrain", layout="wide")

# Title
st.markdown("## 🚂 BulletTrain Module")
st.markdown("This feature panel performs automation, inspection, and developer tooling under the GringoOps platform.")

# Tabs for module use
tab1, tab2, tab3 = st.tabs(["🧪 Tools", "📜 Logs", "⬅️ Return"])

with tab1:
    st.subheader("🧩 Available Actions")
    st.write("Choose a tool to run:")
    if st.button("🚧 Run Repair Check"):
        st.info("Repair engine started...")
        result = subprocess.run(["python", "repair_engine.py"], capture_output=True, text=True)
        st.code(result.stdout if result.returncode == 0 else result.stderr)

    if st.button("🛤️ Run Path Analysis"):
        st.info("Path analysis module triggered...")
        result = subprocess.run(["python", "path_analysis.py"], capture_output=True, text=True)
        st.code(result.stdout if result.returncode == 0 else result.stderr)

with tab2:
    st.subheader("📜 System Logs")
    st.write("Logs or recent outputs would display here.")
    st.code("2025-06-12 13:30 | RepairEngine: Passed ✓")

with tab3:
    st.subheader("⬅️ Back to GringoOps Dashboard")
    st.markdown("[Return to Main Dashboard](../gringoops_dashboard.py)")