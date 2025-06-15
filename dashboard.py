import os
import streamlit as st
import json
import time
from datetime import datetime
from firebase_admin import credentials, initialize_app, db
import tools.check_modules as check_modules

# Initialize Firebase if not already
firebase_initialized = False
try:
    cred = credentials.ApplicationDefault()
    initialize_app(cred, {
        'databaseURL': 'https://chatterfix.firebaseio.com/'
    })
    firebase_initialized = True
except Exception as e:
    st.sidebar.warning(f"Firebase init error: {e}")

st.session_state.firebase_initialized = firebase_initialized

st.set_page_config(page_title="🧠 GringoOps Dashboard", layout="wide")

st.title("🧠 GringoOps Master Dashboard")
st.markdown("This is the central control panel for launching and managing all AI modules.")

# Check availability of modules
modules_info = {
    "FredFix": {
        "path": "FredFix/fredfix_ui.py",
        "available": check_modules.module_exists("FredFix/fredfix_ui.py"),
        "label": "🛠️ FredFix"
    },
    "Wizard": {
        "path": "FredFix/wizard/wizard.py",
        "available": check_modules.module_exists("FredFix/wizard/wizard.py"),
        "label": "🧙 Wizard"
    },
    "CreatorAgent": {
        "path": "core/creator_agent_ui.py",
        "available": check_modules.module_exists("core/creator_agent_ui.py"),
        "label": "🎨 Creator Agent"
    },
    "BulletTrain": {
        "path": "BulletTrain/ui.py",
        "available": check_modules.module_exists("BulletTrain/ui.py"),
        "label": "🚂 BulletTrain"
    }
}

st.sidebar.markdown("---")
enable_memory = st.sidebar.checkbox("🧠 Enable Memory Logging", value=True)
memory_status_emoji = "🟢" if firebase_initialized else "🔴"
st.sidebar.markdown(f"Memory Status: {memory_status_emoji}")

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

st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("🔁 Reload Dashboard"):
    st.experimental_rerun()
if st.sidebar.button("⚙️ Trigger Agent Loop"):
    try:
        db.reference("gringoops/agent_loop").push({
            "event": "Manual Trigger",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "Triggered",
            "user": os.getenv("USER", "unknown")
        })
        st.sidebar.success("Agent loop triggered.")
    except Exception as e:
        st.sidebar.error(f"Trigger failed: {e}")

# Prepare tabs list dynamically depending on module availability
tab_labels = ["🏠 Home"]
for key in ["FredFix", "Wizard", "CreatorAgent", "BulletTrain"]:
    if modules_info[key]["available"]:
        tab_labels.append(modules_info[key]["label"])
    else:
        st.sidebar.warning(f"Module {modules_info[key]['label']} is missing and disabled.")

tabs = st.tabs(tab_labels)

with tabs[0]:
    st.subheader("Welcome to GringoOps")
    st.success("Use the sidebar to navigate to one of the available tools.")
    st.markdown("---")
    st.info("Modules are fully integrated. You can launch, generate, review, and patch seamlessly.")

    st.markdown("### Available Modules and Status")
    for key, info in modules_info.items():
        status = "Available ✅" if info["available"] else "Missing ❌"
        st.write(f"- {info['label']}: {status}")

tab_index = 1

if modules_info["FredFix"]["available"]:
    with tabs[tab_index]:
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
            st.switch_page("FredFix.fredfix_ui")
    tab_index += 1

if modules_info["Wizard"]["available"]:
    with tabs[tab_index]:
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
            st.switch_page("FredFix.wizard.wizard")
    tab_index += 1

if modules_info["CreatorAgent"]["available"]:
    with tabs[tab_index]:
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
            st.switch_page("core.creator_agent_ui")
    tab_index += 1

if modules_info["BulletTrain"]["available"]:
    with tabs[tab_index]:
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
            st.switch_page("BulletTrain.ui")


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

if "GCP_PROJECT" in os.environ:
    st.caption(f"☁️ GCP Project: {os.environ['GCP_PROJECT']}")
else:
    st.caption("⚠️ GCP Project not set (expected env var: GCP_PROJECT)")