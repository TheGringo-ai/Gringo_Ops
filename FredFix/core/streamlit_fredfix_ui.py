import streamlit as st
import requests
import os

st.set_page_config(page_title="FredFix Agent UI", page_icon="🤖")
st.title("FredFix Agent Web UI")

API_URL = st.secrets.get("api_url") or os.getenv("FREDFIX_API_URL") or "https://fredfix-agent-487771372565.us-central1.run.app"
API_KEY = st.secrets.get("api_key") or os.getenv("FRED_FIX_API_KEY") or ""

st.sidebar.header("Settings")
api_url = st.sidebar.text_input("API URL", value=API_URL)
api_key = st.sidebar.text_input("API Key", value=API_KEY, type="password")

st.markdown("Send a command or chat message to your FredFix agent.")

mode = st.radio("Mode", ["Run Command", "Chat"], horizontal=True)

if mode == "Run Command":
    command = st.text_area("Command", "Summarize a maintenance checklist for hydraulic systems.")
    if st.button("Send Command"):
        with st.spinner("Sending to FredFix..."):
            try:
                resp = requests.post(f"{api_url}/run", json={"command": command}, headers={"x-api-key": api_key})
                st.json(resp.json())
            except Exception as e:
                st.error(f"Error: {e}")
else:
    message = st.text_area("Chat Message", "Hello FredFix, what can you do?")
    user_id = st.text_input("User ID (optional)")
    if st.button("Send Message"):
        with st.spinner("Chatting with FredFix..."):
            try:
                payload = {"message": message}
                if user_id:
                    payload["user_id"] = user_id
                resp = requests.post(f"{api_url}/chat", json=payload, headers={"x-api-key": api_key})
                st.json(resp.json())
            except Exception as e:
                st.error(f"Error: {e}")

st.info("""\
- Set your API URL and API Key in the sidebar.
- Use 'Run Command' for automation tasks, or 'Chat' for conversational AI.
- This UI is for demo/dev use. For production, add authentication and HTTPS.
""")
