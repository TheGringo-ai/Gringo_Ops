import streamlit as st
from BulletTrain.services import run_auto_repair, sync_agents, transcribe_backlog

st.set_page_config(page_title="🚄 Bullet Train Launcher", layout="wide")

st.title("🚄 GringoOps Bullet Train")
st.markdown("Launch rapid-fire automation tools and diagnostics here.")

st.subheader("🔧 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧠 Run Auto-Repair"):
        result = run_auto_repair()
        st.success(f"Auto-repair finished: {result}")

with col2:
    if st.button("📦 Sync Agents"):
        result = sync_agents()
        st.success(f"Agent sync complete: {result}")

with col3:
    if st.button("📝 Transcribe Backlog"):
        result = transcribe_backlog()
        st.success(f"Transcription complete: {result}")

st.subheader("📊 System Diagnostics (coming soon)")
st.info("Live logs and status dashboards will appear here.")