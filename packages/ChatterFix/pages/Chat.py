import streamlit as st
import sys
from pathlib import Path

# Add project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from packages.fredfix.core.agent import FredFixAgent

st.set_page_config(page_title="ChatterFix Chat", page_icon="🤖")

st.title("ChatterFix AI Assistant")
st.write("Ask me anything about your maintenance tasks, or give me a command!")

# Initialize agent and chat history
if "logged_in" in st.session_state and st.session_state.logged_in:
    user_email = st.session_state.get("user_email", "default_user")
    if 'fredfix_agent' not in st.session_state:
        st.session_state.fredfix_agent = FredFixAgent(user_id=user_email)
else:
    st.warning("Please log in to use the chat.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What can I help you with?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            agent_response = st.session_state.fredfix_agent.run_agent(prompt)
            response_content = agent_response.get("output", "Sorry, I encountered an error.")
            st.markdown(response_content)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response_content})
