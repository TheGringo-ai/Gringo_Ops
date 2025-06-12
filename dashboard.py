import os
import streamlit as st

st.set_page_config(page_title="🧠 GringoOps Dashboard", layout="wide")

st.title("🧠 GringoOps Master Dashboard")
st.markdown("This is the central control panel for launching and managing all AI modules.")

# Sidebar
st.sidebar.title("🔧 Tools")
module = st.sidebar.radio("Navigate to module:", [
    "🏠 Home",
    "🛠️ FredFix",
    "🧙 Wizard",
    "🎨 Creator Agent",
    "🚂 BulletTrain"
])

# Dynamic import/view rendering
if module == "🏠 Home":
    st.subheader("Welcome to GringoOps")
    st.success("Use the sidebar to navigate to one of the available tools.")
    st.markdown("---")
    st.info("Modules are fully integrated. You can launch, generate, review, and patch seamlessly.")

elif module == "🛠️ FredFix":
    st.subheader("🛠️ FredFix Panel")
    with st.container():
        st.markdown("Launching FredFix UI...")
        os.system("streamlit run FredFix/fredfix_ui.py")

elif module == "🧙 Wizard":
    st.subheader("🧙 Prompt Wizard")
    with st.container():
        st.markdown("Launching Wizard...")
        os.system("streamlit run FredFix/wizard/wizard.py")

elif module == "🎨 Creator Agent":
    st.subheader("🎨 Creator Agent UI")
    with st.container():
        st.markdown("Launching Creator Agent...")
        os.system("streamlit run core/creator_agent_ui.py")

elif module == "🚂 BulletTrain":
    st.subheader("🚂 BulletTrain Module")
    with st.container():
        st.markdown("Launching BulletTrain UI...")
        os.system("streamlit run BulletTrain/ui.py")