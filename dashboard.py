import streamlit as st
from FredFix.core.CreatorAgent import CreatorAgent
from FredFix.core.repair_engine import repair_all_code
import os

st.set_page_config(page_title="Unified Dashboard", layout="wide")

st.title("FredFix Unified Dashboard")
st.markdown("Welcome to your unified AI agent interface.")

# Placeholder UI
col1, col2 = st.columns(2)

with col1:
    st.header("Creator Agent")
    user_prompt = st.text_input("What should the agent generate?")
    if st.button("Generate Code"):
        if user_prompt:
            agent = CreatorAgent()
            code = agent.create_module(user_prompt)
            st.code(code, language="python")
            save_path = os.path.join(os.getcwd(), "generated_module.py")
            agent.save_module(save_path, code)
            st.success(f"Module saved to {save_path}")
        else:
            st.warning("Please enter a prompt.")

with col2:
    st.header("Repair Agent")
    target_path = st.text_input("Path to codebase for repair")
    if st.button("Fix Codebase"):
        if os.path.isdir(target_path):
            result = repair_all_code(target_path)
            st.success("Codebase repair completed.")
            st.text(result)
        else:
            st.error("Invalid directory path.")

st.success("Dashboard is running properly.")
st.markdown("---")
st.info("Dashboard ready for multi-agent operations.")