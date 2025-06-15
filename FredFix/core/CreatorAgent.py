import streamlit as st
import os
from core.memory_manager import MemoryManager
import yaml

st.set_page_config(page_title="GringoOps: God Mode", layout="wide")

memory = MemoryManager()
config_path = "gringoops_config.yaml"
user_config = {}
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f)

st.title("🧠 GringoOps: God Mode Dev Console")
st.markdown("Welcome to your full-stack AI cockpit. Choose a tool to begin:")

tabs = st.tabs(["🛠 Dev Tools", "🤖 AI Agents", "📁 Project Explorer", "🔐 Secrets", "🚀 Launch", "📊 Health Check"])

with tabs[0]:
    st.header("Dev Tools")
    st.button("🧠 Creator Agent")
    st.button("🛠 Diff Repairer")
    st.button("🧱 Scaffolder")

with tabs[1]:
    st.header("AI Agents")
    st.button("Chat with Gemini")
    st.button("Chat with OpenAI")
    st.button("Chat with Hugging Face")
    st.button("View Agent Memory")

    st.subheader("💬 Direct Multi-Agent Chat")

    agent_roles = {
        "🤖 Coder": "gemini_agent",
        "📋 Project Manager": "openai_agent",
        "📝 Note Taker": "hf_agent"
    }

    st.markdown("#### Agent Toggles")
    for role in agent_roles:
        if f"toggle_{role}" not in st.session_state:
            st.session_state[f"toggle_{role}"] = True
        st.session_state[f"toggle_{role}"] = st.checkbox(f"Enable {role}", value=st.session_state[f"toggle_{role}"])

    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    user_message = st.text_input("You:", key="multi_agent_input")

    if user_message:
        st.session_state.chat_log.append(("🧑 You", user_message))
        for role, agent in agent_roles.items():
            if st.session_state.get(f"toggle_{role}", True):
                assistant_reply = f"{role} via `{agent}` responding to: {user_message}"
                st.session_state.chat_log.append((role, assistant_reply))
                memory.save("CreatorAgent", {"role": role, "input": user_message, "response": assistant_reply})

    for speaker, message in st.session_state.chat_log:
        with st.chat_message(speaker):
            st.markdown(message)

    st.subheader("🧠 Agent Memory Tools")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Export Memory"):
            memory.export_json("creator_memory.json")
            st.success("Exported to creator_memory.json")
    with col2:
        if st.button("Clear Memory"):
            memory.clear()
            st.warning("Agent memory cleared")
    with col3:
        if st.button("Summarize Memory"):
            summary = memory.summarize()
            st.info(summary)

with tabs[2]:
    st.header("Project File Explorer")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                st.write(os.path.join(root, file))

with tabs[3]:
    st.header("Secrets & Keys")
    st.text("🔑 Manage your API keys and secrets here (WIP)")

with tabs[4]:
    st.header("Deployment & Launch")
    st.button("▶️ Run LineSmart")
    st.button("▶️ Run ChatterFix")
    st.button("▶️ Run FredFix")

with tabs[5]:
    st.header("Project Health Check")
    st.markdown("- [ ] README.md present")
    st.markdown("- [ ] .env linked or Secret Manager active")
    st.markdown("- [ ] Unit test coverage")
    st.markdown("- [ ] Agent memory synced")