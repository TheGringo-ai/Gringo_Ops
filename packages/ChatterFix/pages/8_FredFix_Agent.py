import streamlit as st
import requests
from frontend.auth_utils import enforce_auth
import datetime
import os
import json
from backend import database
from sidebar import agent_sidebar
from frontend import utils # Import the new utils module

# --- Sidebar Navigation ---
selected = agent_sidebar(selected_agent="FredFix")
if st.session_state.get("go_to_gringoops"):
    st.success("Redirecting to GringoOpsHub... (placeholder)")
    st.stop()

# --- Chat Memory (Session + Firestore) ---
def load_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

def save_chat_history_to_firestore():

    """Placeholder docstring for save_chat_history_to_firestore."""    user = st.session_state.get("user")
    if user:
        database.add_document("fredfix_chat_memory", {
            "user": user,
            "chat_history": st.session_state["chat_history"],
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

def render_chat_history():

    """Placeholder docstring for render_chat_history."""    st.markdown("### Chat History")
    for entry in st.session_state["chat_history"][-10:]:
        st.markdown(f"**User:** {entry['prompt']}")
        st.markdown(f"**FredFix:** {entry['response']}")
        st.markdown("---")

# RBAC: Only allow certain roles
enforce_auth(allowed_roles=["admin", "manager", "ai_tech"])

st.title("🤖 FredFix AI Agent Panel")
st.write("Talk to the FredFix agent for BOMs, troubleshooting, checklists, and more.")

FREDFIX_API_URL = os.getenv("FREDFIX_API_URL") or st.secrets.get("fredfix_api_url") or "https://fredfix-agent-487771372565.us-central1.run.app"
FREDFIX_API_KEY = os.getenv("FRED_FIX_API_KEY") or st.secrets.get("fredfix_api_key") or ""

api_url = st.text_input("FredFix API URL", value=FREDFIX_API_URL)
api_key = st.text_input("FredFix API Key", value=FREDFIX_API_KEY, type="password")

# --- Model Selection Dropdown ---
model = st.selectbox("Model", ["openai", "gemini"], index=0)

# --- Query Tagging ---
asset = st.text_input("Asset Tag (optional)")
line = st.text_input("Line (optional)")
priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)

# --- File Upload for AI Input ---
uploaded_file = st.file_uploader(
    "Upload a file for FredFix (PDF, TXT, JPG, JSON)", 
    type=["pdf", "txt", "jpg", "jpeg", "png", "json"]
)

file_content = None
file_type = None
if uploaded_file:
    file_type = uploaded_file.type
    st.info(f"Uploaded: {uploaded_file.name} ({file_type})")
    if file_type in ["text/plain", "application/json"]:
        file_content = uploaded_file.read().decode("utf-8")
        st.text_area("File Content Preview", file_content, height=150)
    elif file_type.startswith("image/"):
        st.image(uploaded_file)
    elif file_type == "application/pdf":
        uploaded_file.seek(0)
        file_content = utils.extract_pdf_text(uploaded_file) # Use the utility function
        st.text_area("Extracted PDF Text", file_content, height=150)

prompt = st.text_area("Enter your prompt or task for FredFix:", "Generate a maintenance checklist for a CNC machine.")

# --- Chat Memory Load/Render ---
load_chat_history()
render_chat_history()

response_text = ""

# --- User Context Validation with Dev Fallback ---

# --- Input Validation for Prompt and Tags ---
def sanitize_input(text):
    if not text:
        return ""
    return str(text).strip().replace("\x00", "")

prompt = sanitize_input(prompt)
asset = sanitize_input(asset)
line = sanitize_input(line)
priority = sanitize_input(priority)

# --- Retry Last Prompt ---
if st.session_state.get("chat_history"):
    if st.button("Retry Last Prompt"):
        last = st.session_state["chat_history"][-1]
        prompt = last["prompt"]
        st.experimental_rerun()

if st.button("Send to FredFix") or st.session_state.get("auto_send"):
    with st.spinner("Contacting FredFix..."):
        try:
            payload = {"command": prompt, "model": model, "asset": asset, "line": line, "priority": priority}
            if file_content:
                payload["file_content"] = file_content
                payload["file_name"] = uploaded_file.name
                payload["file_type"] = file_type
            # --- Debug: Print payload ---
            if st.checkbox("Show Debug Info"):
                st.json(payload)
            resp = requests.post(f"{api_url}/run", json=payload, headers={"x-api-key": api_key}, timeout=60)
            data = resp.json()
            response_text = data.get("result") or str(data)
            # --- Streaming Output: Markdown/HTML Safe, Dict Fallback ---
            if isinstance(response_text, dict):
                response_text = json.dumps(response_text, indent=2)
            placeholder = st.empty()
            displayed = ""
            for token in response_text.split():
                displayed += token + " "
                placeholder.markdown(displayed, unsafe_allow_html=True)
                st.sleep(0.03)
            st.success("FredFix Response:")
            st.write(response_text)
            # Log interaction
            if "user" in st.session_state:
                log_entry = {
                    "user": st.session_state["user"],
                    "prompt": prompt,
                    "response": response_text,
                    "model": model,
                    "asset": asset,
                    "line": line,
                    "priority": priority,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                try:
                    database.add_document("fredfix_agent_logs", log_entry)
                except Exception as e:
                    st.warning(f"Firestore logging failed: {e}")
                try:
                    with open("fredfix_agent_log.jsonl", "a") as f:
                        f.write(json.dumps(log_entry) + "\n")
                except Exception as e:
                    st.warning(f"Local log file write failed: {e}")
                # Update chat memory
                st.session_state["chat_history"].append({
                    "prompt": prompt,
                    "response": response_text,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
                try:
                    save_chat_history_to_firestore()
                except Exception as e:
                    st.warning(f"Chat history Firestore backup failed: {e}")
        except requests.Timeout:
            st.error("Request timed out. Please try again or check your backend.")
        except requests.RequestException as e:
            st.error(f"API request failed: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Feedback on Response ---
if response_text:
    feedback = st.radio("Was this response helpful?", ["👍", "👎"], horizontal=True)
    if st.button("Submit Feedback"):
        try:
            database.add_document("fredfix_feedback", {
                "user": st.session_state.get("user"),
                "prompt": prompt,
                "response": response_text,
                "feedback": feedback,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            st.success("Feedback submitted!")
        except Exception as e:
            st.error(f"Feedback logging failed: {e}")

# --- Convert Response to Work Order ---
if response_text and st.button("Convert to Work Order"):
    try:
        from backend import work_orders
        work_orders.create_from_ai(
            user=st.session_state.get("user"),
            description=response_text,
            metadata={"prompt": prompt, "model": model, "asset": asset, "line": line, "priority": priority}
        )
        st.success("Work Order created from AI response!")
    except Exception as e:
        st.error(f"Work order creation failed: {e}")
# --- Export/Download Feature ---
if response_text:
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Export Response as .txt",
        data=response_text,
        file_name=f"fredfix_response_{now}.txt"
    )
    st.download_button(
        label="Export Response as .md",
        data=f"# FredFix Response\n\n{response_text}",
        file_name=f"fredfix_response_{now}.md"
    )
