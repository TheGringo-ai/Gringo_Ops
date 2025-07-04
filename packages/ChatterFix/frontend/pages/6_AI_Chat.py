import streamlit as st
import json
import types
from backend import chatterfix_agent as agent # Use the new, smarter agent
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="AI Chat", allowed_roles=['manager', 'technician'])
# --- End Auth Check ---

st.set_page_config(page_title="AI Chat", page_icon="🤖")

st.title("🤖 AI Chat & Command")
st.caption("Ask questions or issue commands like 'Create a work order for a broken pump'")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the ChatterFix Agent, passing the existing chat history
try:
    # The agent is re-initialized on each run. We pass the latest history.
    agent_instance = agent.ChatterFixAgent(chat_history=st.session_state.get("messages", []))
    st.session_state.agent = agent_instance
except Exception as e:
    st.error(f"Error initializing ChatterFix Agent: {e}")
    st.stop()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What can I help you with?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # The agent now determines the intent (chat vs. command) internally.
        # The UI just calls a single method and handles the two possible return types.
        response = st.session_state.agent.process_input(
            prompt,
            invoked_by_user=user.email
        )

        # The agent returns a generator for chat messages for streaming.
        if isinstance(response, types.GeneratorType):
            full_response = ""
            for chunk in response:
                full_response += (chunk or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        # The agent returns a dictionary for tool commands.
        else:
            if response.get("success"):
                full_response = f"**Action Executed:** `{response.get('tool')}`\n\n**Result:**\n```json\n{json.dumps(response.get('result'), indent=2)}\n```"
            else:
                full_response = f"**Error:** {response.get('error', 'An unknown error occurred.')}\n\n*Raw model response (if available):\n`{response.get('raw_response')}`"
            message_placeholder.markdown(full_response)
            
    # Add the assistant's final response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
