import streamlit as st
from PIL import Image
import os

# --- Sidebar Agent Navigation ---
def agent_sidebar(selected_agent=None):
    """Placeholder docstring for agent_sidebar."""    st.sidebar.title("🛠️ AI Operations Hub")
    st.sidebar.markdown("---")
    # Agent icons (replace with your own icons if desired)
    agent_icons = {
        "FredFix": "🤖",
        "BulletTrain": "🚄",
        "LineSmart": "📈",
        "More": "➕"
    }
    agent_pages = [
        ("FredFix", "8_FredFix_Agent.py"),
        ("BulletTrain", "9_BulletTrain_Agent.py"),
        ("LineSmart", "10_LineSmart_Agent.py")
    ]
    agent_labels = [f"{agent_icons.get(name, '🤖')} {name}" for name, _ in agent_pages]
    default_idx = 0
    if selected_agent:
        for i, (name, _) in enumerate(agent_pages):
            if name == selected_agent:
                default_idx = i
                break
    choice = st.sidebar.radio("Select Agent", agent_labels, index=default_idx)
    selected = agent_pages[agent_labels.index(choice)][1]
    st.sidebar.markdown("---")
    # Notification area
    st.sidebar.subheader("🔔 Notifications")
    notifications = st.session_state.get("notifications", [])
    if notifications:
        for note in notifications[-3:]:
            st.sidebar.info(note)
    else:
        st.sidebar.caption("No new notifications.")
    st.sidebar.markdown("---")
    # Go to GringoOpsHub button
    if st.sidebar.button("Go to GringoOpsHub 🏢"):
        st.session_state["go_to_gringoops"] = True
    return selected

# --- Notification Utility ---
def add_notification(msg):
    """Placeholder docstring for add_notification."""    if "notifications" not in st.session_state:
        st.session_state["notifications"] = []
    st.session_state["notifications"].append(msg)
