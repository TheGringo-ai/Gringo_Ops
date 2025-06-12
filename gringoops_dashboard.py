import streamlit as st
import os
import subprocess
from tools.config import load_config
from tools.logger import log_markdown
from tools import openai_review
from plugins.autopatch import autopatch_run
from plugins.summarize import run as summarize_run
from tools import gemini_query

# Load config
conf = load_config()
st.set_page_config(page_title="GringoOps AI Dashboard", layout="wide")

# Branding logo at the top
logo_path = "static/gringo_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=180)

st.markdown("<h1 style='color:#00bcd4;'>🤖 GringoOps AI Automation Suite</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Navigation
st.sidebar.title("🧰 Toolset")
tool = st.sidebar.radio("Choose a tool to run:", ["Chat", "Review", "AutoPatch", "Summarize", "Logs"])
st.sidebar.markdown("---")
st.sidebar.markdown("Created by **GringoOps** – your AI-powered command platform.")

# Chat Tool
if tool == "Chat":
    model = st.sidebar.selectbox("Choose LLM", ["OpenAI (GPT-4)", "Gemini"])
    user_input = st.text_area("💬 Enter your message:")
    if st.button("Send"):
        if model.startswith("OpenAI"):
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=conf["openai"]["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            st.markdown(f"**GPT-4 Response:**\n\n{response.choices[0].message.content}")
        else:
            st.write("🧠 Sending to Gemini...")
            gemini_query.query_model(prompt=user_input)

# Review Tool
elif tool == "Review":
    st.subheader("📄 GPT-4 Code Review")
    uploaded = st.file_uploader("Upload a Python file for review", type=["py"])
    if uploaded and st.button("Run Code Review"):
        tmp_path = "temp_review.py"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        openai_review.review(target=tmp_path, supervised=False)
        with open("gpt_review.log", "r") as log:
            st.markdown("### 📝 GPT Review Output")
            st.code(log.read(), language="markdown")

# AutoPatch Tool
elif tool == "AutoPatch":
    st.subheader("🛠 GPT-4 AutoPatchBoy")
    uploaded = st.file_uploader("Upload a Python file to patch", type=["py"])
    if uploaded and st.button("Run AutoPatchBoy"):
        tmp_path = "temp_patch.py"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        class Args: target=tmp_path; supervised=False
        autopatch_run(Args())

# Summarize Tool
elif tool == "Summarize":
    st.subheader("🧾 AI Summarization")
    uploaded = st.file_uploader("Upload a code or text file", type=["py", "txt", "md"])
    if uploaded and st.button("Summarize"):
        tmp_path = "temp_summary.txt"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        class Args: target=tmp_path
        summarize_run(Args())

# Log Viewer
elif tool == "Logs":
    st.subheader("📚 Log Viewer (Last 5 Patches)")
    log_dir = "logs/patches"
    if os.path.exists(log_dir):
        files = sorted(os.listdir(log_dir))[-5:]
        for file in reversed(files):
            st.markdown(f"### 📄 `{file}`")
            with open(os.path.join(log_dir, file), "r") as f:
                st.markdown(f.read())
    else:
        st.info("No patch logs found yet.")

# Footer branding
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>GringoOps™ © 2025 — AI Automation Platform by Fred Taylor</div>",
    unsafe_allow_html=True
)