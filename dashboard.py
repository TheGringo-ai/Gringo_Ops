import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from FredFix import registry
from FredFix import scan_all

st.set_page_config(page_title="GringoOps Unified Dashboard", layout="wide")
st.title("🛠️ GringoOps Unified AI Dashboard")
st.markdown("Control and monitor all your AI-powered agents from here.")

with st.sidebar:
    st.header("🔧 Agent Controls")
    agent = st.selectbox("Select an agent to run", ["repair", "scan"])
    if st.button("Run Selected Agent"):
        if agent == "scan":
            issues = scan_all.report_issues()
            st.session_state["scan_issues"] = issues
            st.success(f"🔍 Scan complete. Found {len(issues)} issues.")
        else:
            result = registry.invoke_agent(agent)
            st.success(result)

if "scan_issues" in st.session_state and st.session_state["scan_issues"]:
    st.subheader("⚠️ Code Issues Found:")
    for path, note in st.session_state["scan_issues"]:
        st.write(f"{note} — `{path}`")

st.markdown("---")
st.info("✅ All agents are now unified under one dashboard. Additional modules will auto-load as wired.")