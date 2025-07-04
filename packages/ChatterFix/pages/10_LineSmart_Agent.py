import streamlit as st
from sidebar import agent_sidebar

st.set_page_config(page_title="LineSmart Agent", page_icon="📈")

selected = agent_sidebar(selected_agent="LineSmart")

st.title("📈 LineSmart Agent (Coming Soon)")
st.info("This panel will host the LineSmart AI agent for line analytics and smart operations. Stay tuned!")

if st.session_state.get("go_to_gringoops"):
    st.success("Redirecting to GringoOpsHub... (placeholder)")
    # In production, use st.experimental_redirect or similar
