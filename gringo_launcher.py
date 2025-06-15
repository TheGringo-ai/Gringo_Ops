import os
import openai
import streamlit as st
from google.cloud import secretmanager
from pathlib import Path

@st.cache_resource
def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    project_number = "487771372565"
    secret_name = f"projects/{project_number}/secrets/{secret_id}/versions/latest"
    return client.access_secret_version(request={"name": secret_name}).payload.data.decode("UTF-8")

# Preload secrets dictionary for all tools
secrets = {
    "openai_api_key": get_secret("openai_api_key"),
    "gemini_api_key": get_secret("gemini-api-key"),
    "huggingface_api_key": get_secret("huggingface-api-key"),
    "chatterfix_sa_key": get_secret("chatterfix-sa-key"),
    "chatterfix_service_account": get_secret("chatterfix-service-account"),
    "firebase_github_token": get_secret("firebase-app-hosting-github-oauth-github-oauthtoken-071fda"),
    "gitcentral_github_token": get_secret("GitCentral1-github-oauthtoken-72aaaa")
}

tool = st.sidebar.radio("Choose a tool to run:", ["Chat", "Review", "AutoPatch", "Summarize", "Logs", "📦 New App", "🧪 System Check"])

from tools.config import load_config
from lib.keychain import get_key
from tools import openai_review
from plugins.autopatch import autopatch_run
from plugins.summarize import run as summarize_run
from tools import gemini_query


@st.cache_resource
def get_config():
    return load_config()

conf = get_config()

if tool == "Chat":
    st.subheader("💬 Chat Assistant")
    model_map = {
        "GPT-4 Turbo (OpenAI)": "openai",
        "Gemini Pro (Google)": "gemini"
    }
    model_label = st.selectbox("Choose LLM", list(model_map.keys()))
    selected_model = model_map[model_label]
    # Use preloaded secrets dictionary
    openai_key = secrets["openai_api_key"]
    gemini_key = secrets["gemini_api_key"]
    huggingface_key = secrets["huggingface_api_key"]
    service_account_1 = secrets["chatterfix_sa_key"]
    service_account_2 = secrets["chatterfix_service_account"]
    firebase_token = secrets["firebase_github_token"]
    gitcentral_token = secrets["gitcentral_github_token"]
    st.caption("🔐 All secrets preloaded for Chat tool.")
    user_input = st.text_area("Enter your message:")
    if st.button("Send"):
        if selected_model == "openai":
            try:
                api_key = openai_key
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input}
                    ]
                )
                st.markdown(f"**GPT-4 Turbo Response:**\n\n{response.choices[0].message.content}")
            except Exception as e:
                st.error(f"❌ OpenAI API error: {e}")
        else:
            st.write("🧠 Sending to Gemini...")
            gemini_query.query_model(prompt=user_input)

elif tool == "Review":
    st.subheader("📄 GPT-4 Code Review")
    uploaded = st.file_uploader("Upload a Python file for review", type=["py"])
    if uploaded and st.button("Run Review"):
        tmp_path = "temp_review.py"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        openai_review.review(target=tmp_path, supervised=False)
        with open("gpt_review.log", "r") as log:
            st.markdown("### 📝 GPT Review Output")
            st.code(log.read(), language="markdown")

elif tool == "AutoPatch":
    st.subheader("🛠 AutoPatchBoy (GPT-4)")
    uploaded = st.file_uploader("Upload a Python file to patch", type=["py"])
    if uploaded and st.button("Run AutoPatchBoy"):
        tmp_path = "temp_patch.py"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        class Args: target=tmp_path; supervised=False
        autopatch_run(Args())

elif tool == "Summarize":
    st.subheader("🧾 File Summarizer")
    uploaded = st.file_uploader("Upload a text or code file", type=["py", "txt", "md"])
    if uploaded and st.button("Summarize"):
        tmp_path = "temp_summary.txt"
        with open(tmp_path, "w") as f:
            f.write(uploaded.read().decode())
        class Args: target=tmp_path
        summarize_run(Args())

elif tool == "Logs":
    st.subheader("📚 Review Logs (Latest Patches)")
    log_dir = "logs/patches"
    if os.path.exists(log_dir):
        files = sorted(os.listdir(log_dir))[-5:]
        for file in reversed(files):
            st.markdown(f"### 📄 `{file}`")
            with open(os.path.join(log_dir, file), "r") as f:
                st.markdown(f.read())
    else:
        st.info("No patch logs found yet.")

elif tool == "📦 New App":
    st.subheader("📦 Create New App Module")
    app_name = st.text_input("Enter new app name:")
    if st.button("Create App"):
        base_path = f"apps/{app_name}"
        os.makedirs(base_path, exist_ok=True)
        with open(f"{base_path}/main.py", "w") as f:
            f.write(f"# {app_name} entry point\n\nprint('Hello from {app_name}')\n")
        with open(f"{base_path}/README.md", "w") as f:
            f.write(f"# {app_name}\n\nGenerated by GringoOps.")
        st.success(f"✅ Created new app: {app_name}")

elif tool == "🧪 System Check":
    st.subheader("🧪 Environment & Dependency Check")

    import platform
    import streamlit as stlib

    st.markdown("### 🔑 API Key Status")
    def check_secret(secret_id):
        try:
            return get_secret(secret_id) != ""
        except:
            return False

    st.write("OPENAI_API_KEY:", "✅ Found" if check_secret("openai_api_key") else "❌ Missing")
    st.write("GOOGLE_API_KEY:", "✅ Found" if check_secret("gemini-api-key") else "❌ Missing")
    st.write("HUGGINGFACE_API_KEY:", "✅ Found" if check_secret("huggingface-api-key") else "⚠️ Optional")
    st.write("ChatterFix Service Account:", "✅ Found" if check_secret("chatterfix-sa-key") else "❌ Missing")
    st.write("ChatterFix Service Account (Alt):", "✅ Found" if check_secret("chatterfix-service-account") else "❌ Missing")
    st.write("Firebase GitHub Token:", "✅ Found" if check_secret("firebase-app-hosting-github-oauth-github-oauthtoken-071fda") else "❌ Missing")
    st.write("GitCentral1 GitHub Token:", "✅ Found" if check_secret("GitCentral1-github-oauthtoken-72aaaa") else "❌ Missing")

    st.markdown("### 🐍 Python Environment")
    st.write("Python version:", platform.python_version())
    st.write("Streamlit version:", stlib.__version__)

    st.markdown("### 📁 Directory Checks")
    st.write("Logs folder:", "✅ Found" if os.path.exists("logs/patches") else "❌ Missing")
    st.write("Plugins folder:", "✅ Found" if os.path.exists("plugins") else "❌ Missing")