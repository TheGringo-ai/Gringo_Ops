import streamlit as st
from sidebar import agent_sidebar

st.set_page_config(page_title="BulletTrain Agent", page_icon="🚄")

selected = agent_sidebar(selected_agent="BulletTrain")

st.title("🚄 BulletTrain Agent (Coming Soon)")
st.info("This panel will host the BulletTrain AI agent for rapid document analysis and export. Stay tuned!")

if st.session_state.get("go_to_gringoops"):
    st.success("Redirecting to GringoOpsHub... (placeholder)")
    # In production, use st.experimental_redirect or similar
