# Trigger rebuild: Streamlit syntax fix confirmation
import os
import streamlit as st

tool = st.sidebar.radio("Choose a tool to run:", ["Chat", "Review", "AutoPatch", "Summarize", "Logs", "📦 New App", "🧪 System Check"])

if tool == "Chat":
    st.write("💬 Chat interface coming soon...")

elif tool == "Review":
    st.write("🔍 Review interface coming soon...")

elif tool == "AutoPatch":
    st.write("🛠 AutoPatch system coming soon...")

elif tool == "Summarize":
    st.write("📝 Summarizer coming soon...")

elif tool == "Logs":
    st.write("📚 Log viewer coming soon...")

elif tool == "📦 New App":
    st.write("📦 App scaffolder coming soon...")

elif tool == "🧪 System Check":
    st.subheader("🧪 Environment & Dependency Check")

    import platform
    import streamlit as stlib

    st.markdown("### 🔑 API Key Status")
    st.write("OPENAI_API_KEY:", "✅ Found" if os.getenv("OPENAI_API_KEY") else "❌ Missing")
    st.write("GOOGLE_API_KEY:", "✅ Found" if os.getenv("GOOGLE_API_KEY") else "❌ Missing")
    st.write("HUGGINGFACE_API_KEY:", "✅ Found" if os.getenv("HUGGINGFACE_API_KEY") else "⚠️ Optional")

    st.markdown("### 🐍 Python Environment")
    st.write("Python version:", platform.python_version())
    st.write("Streamlit version:", stlib.__version__)

    st.markdown("### 📁 Directory Checks")
    st.write("Logs folder:", "✅ Found" if os.path.exists("logs/patches") else "❌ Missing")
    st.write("Plugins folder:", "✅ Found" if os.path.exists("plugins") else "❌ Missing")