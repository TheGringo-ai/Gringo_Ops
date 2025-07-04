import streamlit as st
import sys
from pathlib import Path

# Add project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from packages.fredfix.core.agent import FredFixAgent
from tools.export_to_pdf import export_to_pdf

st.set_page_config(page_title="ChatterBot - ChatterFix", page_icon="🤖")

st.title("ChatterBot AI Assistant")
st.write("Ask me anything about your maintenance tasks, or give me a command!")
st.info("Try this: `create work order The conveyor belt is making a loud squeaking noise.`")

# Initialize agent and chat history
if 'fredfix_agent' not in st.session_state:
    # Get user email if logged in, otherwise use a default
    user_email = st.session_state.get("user_email", "default_user")
    st.session_state.fredfix_agent = FredFixAgent(user_id=user_email)
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
            
            if st.button("Save as PDF", key=f"pdf_{len(st.session_state.messages)}"):
                pdf_path = export_to_pdf(response_content)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=pdf_path)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# --- Upgrade Button ---
if st.session_state.get("limit_reached"):
    st.warning("You have reached your command limit for this month.")
    if st.button("Upgrade to ChatterFix Team ($49/mo)"):
        # This is a placeholder for the real Stripe integration
        # In a real app, you would get the user's ID token and call your Firebase Function
        st.success("Upgrade functionality coming soon!")
