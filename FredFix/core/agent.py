import streamlit as st
import subprocess
from FredFix.core.repair_engine import repair_all_code
from FredFix.core.review_engine import review_code
from FredFix.ui.dashboard import launch_dashboard

try:
    from FredFix.models import gpt_agent
except ImportError:
    gpt_agent = None
    st.warning("⚠️ GPT agent module not found. Please check FredFix/models/gpt_agent.py")

try:
    from FredFix.core.unified_agent import unified_agent
except ImportError:
    unified_agent = None
    st.warning("⚠️ Unified Agent logic is missing. Please create FredFix/core/unified_agent.py")

from FredFix.utils.logger import log_result

st.set_page_config(page_title="GringoOps God Mode", layout="wide")
st.title("🧠 GringoOps Unified Dashboard")

st.sidebar.title("Agent Commands")
task = st.sidebar.radio("Choose a Task", ["None", "Repair", "Review", "Launch UI", "Launch Global Dashboard", "Run Prompt", "Run Custom Agent"])

def run_custom_agent(agent_type, prompt):
    if not unified_agent:
        return "Unified agent logic is not available."
    try:
        return unified_agent(task_type=agent_type, prompt=prompt)
    except Exception as e:
        return f"Error running custom agent: {str(e)}"

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
        if gpt_agent:
            response = gpt_agent.run_task(user_prompt)
            log_result("prompt", response)
            st.code(response)
        else:
            st.error("GPT agent is not available.")

elif task == "Run Custom Agent":
    agent_type = st.selectbox("Select Agent Type", ["Builder", "Analyzer", "Fixer", "QA"])
    agent_prompt = st.text_area("Enter your command for the agent")
    if st.button("Run Custom Agent"):
        response = run_custom_agent(agent_type, agent_prompt)
        log_result("custom_agent", response)
        st.code(response)