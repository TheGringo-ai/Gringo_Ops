import streamlit as st
import subprocess
from FredFix.core.repair_engine import repair_all_code
from FredFix.core.review_engine import review_code
from FredFix.ui.dashboard import launch_dashboard
from FredFix.models import gpt_agent
from FredFix.utils.logger import log_result

st.set_page_config(page_title="GringoOps God Mode", layout="wide")
st.title("🧠 GringoOps Unified Dashboard")

st.sidebar.title("Agent Commands")
task = st.sidebar.radio("Choose a Task", ["None", "Repair", "Review", "Launch UI", "Launch Global Dashboard", "Run Prompt", "Run Custom Agent"])

if task == "Repair":
    st.subheader("🔧 Repairing Codebase")
    result = repair_all_code()
    log_result("repair", result)
    st.code(result)

elif task == "Review":
    st.subheader("🕵️ Reviewing Codebase")
    result = review_code()
    log_result("review", result)
    st.code(result)

elif task == "Launch UI":
    st.subheader("🖥️ Launching FredFix UI Dashboard")
    st.info("Opening FredFix dashboard in terminal (port 8501)...")
    subprocess.Popen(["streamlit", "run", "FredFix/ui/dashboard.py"])

elif task == "Launch Global Dashboard":
    st.subheader("🌐 Launching GringoOps Main Dashboard")
    st.info("Launching global control center in terminal...")
    subprocess.Popen(["streamlit", "run", "Agent/dashboard.py"])

elif task == "Run Prompt":
    user_prompt = st.text_input("Enter your custom prompt")
    if st.button("Send to GPT Agent"):
        response = gpt_agent.run_task(user_prompt)
        log_result("prompt", response)
        st.code(response)

elif task == "Run Custom Agent":
    agent_type = st.selectbox("Select Agent Type", ["Builder", "Analyzer", "Fixer", "QA"])
    agent_prompt = st.text_area("Enter your command for the agent")
    if st.button("Run Custom Agent"):
        response = run_custom_agent(agent_type, agent_prompt)
        log_result("custom_agent", response)
        st.code(response)

def run_custom_agent(agent_type, prompt):
    if agent_type == "Builder":
        from FredFix.agents.builder import builder_agent
        return builder_agent(prompt)
    elif agent_type == "Analyzer":
        from FredFix.agents.analyzer import analyzer_agent
        return analyzer_agent(prompt)
    elif agent_type == "Fixer":
        from FredFix.agents.fixer import fixer_agent
        return fixer_agent(prompt)
    elif agent_type == "QA":
        from FredFix.agents.qa import qa_agent
        return qa_agent(prompt)
    else:
        return f"[Unknown Agent]: No agent found for type '{agent_type}'"