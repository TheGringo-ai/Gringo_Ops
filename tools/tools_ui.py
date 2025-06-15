import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import json

st.set_page_config(page_title="GringoOps Tools UI", layout="wide")
st.markdown("Welcome to GringoOps Black Box 🚀 - Your Dev Copilot Engine.\n\nJust upload your project, select your AI model, and hit 'Run Full Project Scan'.")
st.title("🧠 GringoOps - God Mode Agent Interface")

# File upload section
st.markdown("### 📂 Upload Files for Review (Optional)")
uploaded_files = st.file_uploader("Upload one or more files", accept_multiple_files=True, type=["py", "txt", "json", "md"])
for uploaded_file in uploaded_files:
    save_path = Path("uploads") / uploaded_file.name
    save_path.parent.mkdir(exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Saved file: {uploaded_file.name}")

st.markdown("Select the AI provider to run project review and enhancement:")

provider = st.selectbox("AI Provider", ["Gemini", "OpenAI", "Hugging Face"])
user_idea = st.text_input("💡 Describe what you want to build (optional)", placeholder="e.g. A todo app with Firebase backend and Streamlit UI")
go = st.button("Run Full Project Scan")

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_files = sorted(log_dir.glob("refactor_log_*.txt"), reverse=True)

if go:
    if user_idea:
        st.info(f"🤖 Submitting idea: {user_idea}")
        os.environ["PROJECT_IDEA"] = user_idea
    # NOTE: The PROJECT_IDEA environment variable can be read by agents to auto-bootstrap a project from a prompt
    st.info(f"🔄 Triggering scan using {provider}...")
    os.system(f"python tools/agent_cli.py --go --provider={provider.lower()}")
    st.success("✅ Task triggered. Check log below.")

st.markdown("---")
st.subheader("📜 View Log Output")

selected_log = st.selectbox(
    "Select a log file to view",
    options=[f.name for f in log_files] + ["Clear All Logs"]
)

if selected_log == "Clear All Logs":
    for log_file in log_files:
        log_file.unlink()
    st.success("🧹 Logs cleared.")
    st.experimental_rerun()
else:
    with open(log_dir / selected_log, "r") as f:
        st.text(f.read())

st.markdown("---")
st.subheader("🧠 Memory Viewer & Editor")

memory_file = Path("memory.json")
if memory_file.exists():
    with open(memory_file, "r") as f:
        memory_data = f.read()
else:
    memory_data = "{}"

edited_memory = st.text_area("Edit Memory JSON", value=memory_data, height=300)
if st.button("💾 Save Memory"):
    try:
        parsed = json.loads(edited_memory)
        with open(memory_file, "w") as f:
            json.dump(parsed, f, indent=2)
        st.success("✅ Memory updated.")
    except Exception as e:
        st.error(f"❌ Invalid JSON format: {e}")

st.markdown("---")
st.subheader("🪛 Patch History")

patch_dir = Path("patches")
patch_dir.mkdir(exist_ok=True)
patch_files = sorted(patch_dir.glob("*.diff"), reverse=True)

selected_patch = st.selectbox("Select a patch file to view", options=[f.name for f in patch_files])
if selected_patch:
    with open(patch_dir / selected_patch, "r") as f:
        st.text(f.read())

with st.expander("💬 Open Live Chat Assistant"):
    user_query = st.text_input("Ask the Agent:", key="agent_chat_input")
    if st.button("Send to Agent"):
        if user_query:
            from agent_cli import handle_user_prompt
            try:
                response = handle_user_prompt(user_query)
                st.markdown(f"**Agent:** {response}")
            except Exception as e:
                st.error(f"❌ Agent failed to respond: {e}")