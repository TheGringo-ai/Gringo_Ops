import os
import streamlit as st
import json
import time
from datetime import datetime
from firebase_admin import credentials, initialize_app, db
import subprocess

# Initialize Firebase if not already
if not getattr(st.session_state, "firebase_initialized", False):
    try:
        cred = credentials.ApplicationDefault()
        initialize_app(cred, {
            'databaseURL': 'https://chatterfix.firebaseio.com/'
        })
        st.session_state.firebase_initialized = True
    except Exception as e:
        st.warning(f"Firebase init error: {e}")

st.set_page_config(page_title="🧠 GringoOps Dashboard", layout="wide")

st.title("🧠 GringoOps Master Dashboard")
st.markdown("This is the central control panel for launching and managing all AI modules.")

st.sidebar.markdown("---")
enable_memory = st.sidebar.checkbox("🧠 Enable Memory Logging", value=True)
load_memory = st.sidebar.checkbox("📥 Load Previous Session", value=False)

if load_memory:
    try:
        mem_ref = db.reference("gringoops/memory/latest")
        last_session = mem_ref.get()
        if last_session:
            st.sidebar.success("Memory loaded")
            st.sidebar.code(json.dumps(last_session, indent=2))
        else:
            st.sidebar.info("No previous session found.")
    except Exception as e:
        st.sidebar.error(f"Memory load error: {e}")

tabs = st.tabs(["🏠 Home", "🛠️ FredFix", "🧙 Wizard", "🎨 Creator Agent", "🚂 BulletTrain"])

with tabs[0]:
    st.subheader("Welcome to GringoOps")
    st.success("Use the sidebar to navigate to one of the available tools.")
    st.markdown("---")
    st.info("Modules are fully integrated. You can launch, generate, review, and patch seamlessly.")

with tabs[1]:
    st.subheader("🛠️ FredFix Panel")
    with st.container():
        if enable_memory:
            try:
                mem_ref = db.reference("gringoops/memory")
                mem_ref.child("latest").set({
                    "module": "🛠️ FredFix",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "Launched",
                    "user": os.getenv("USER", "unknown")
                })
            except Exception as e:
                st.warning(f"Memory log error: {e}")
        st.markdown("Launching FredFix UI...")
        subprocess.Popen(["streamlit", "run", "FredFix/fredfix_ui.py"])

with tabs[2]:
    st.subheader("🧙 Prompt Wizard")
    with st.container():
        if enable_memory:
            try:
                mem_ref = db.reference("gringoops/memory")
                mem_ref.child("latest").set({
                    "module": "🧙 Wizard",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "Launched",
                    "user": os.getenv("USER", "unknown")
                })
            except Exception as e:
                st.warning(f"Memory log error: {e}")
        st.markdown("Launching Wizard...")
        subprocess.Popen(["streamlit", "run", "FredFix/wizard/wizard.py"])

with tabs[3]:
    st.subheader("🎨 Creator Agent UI")
    with st.container():
        if enable_memory:
            try:
                mem_ref = db.reference("gringoops/memory")
                mem_ref.child("latest").set({
                    "module": "🎨 Creator Agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "Launched",
                    "user": os.getenv("USER", "unknown")
                })
            except Exception as e:
                st.warning(f"Memory log error: {e}")
        st.markdown("Launching Creator Agent...")
        subprocess.Popen(["streamlit", "run", "core/creator_agent_ui.py"])

with tabs[4]:
    st.subheader("🚂 BulletTrain Module")
    with st.container():
        if enable_memory:
            try:
                mem_ref = db.reference("gringoops/memory")
                mem_ref.child("latest").set({
                    "module": "🚂 BulletTrain",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "Launched",
                    "user": os.getenv("USER", "unknown")
                })
            except Exception as e:
                st.warning(f"Memory log error: {e}")
        st.markdown("Launching BulletTrain UI...")
        subprocess.Popen(["streamlit", "run", "BulletTrain/ui.py"])


st.markdown("---")
st.caption(f"🕒 Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.caption(f"🧠 Memory Logging: {'Enabled' if enable_memory else 'Disabled'}")
st.caption("🚀 Powered by GringoOps | OpenAI GPT-4 | Firebase")

# Agent Loop Sync
if enable_memory:
    try:
        loop_ref = db.reference("gringoops/agent_loop")
        loop_ref.push({
            "event": "Dashboard Loaded",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "Active",
            "user": os.getenv("USER", "unknown")
        })
    except Exception as e:
        st.error(f"Agent loop sync failed: {e}")