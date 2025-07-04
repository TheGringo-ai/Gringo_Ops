import streamlit as st
import pandas as pd
from backend import database
from datetime import datetime
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
st.set_page_config(page_title="Audit Trail", page_icon="🛡️")
user = auth_utils.enforce_auth(page_name="Audit Trail", allowed_roles=['manager', 'admin'])
# --- End Auth Check ---

st.title("🛡️ System Audit Trail")

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_audit_logs():
    """Fetches all audit logs from Firestore and converts to a DataFrame."""
    try:
        logs = database.get_collection("audit_log")
        if not logs:
            return pd.DataFrame()
        # Sort by timestamp descending
        logs_sorted = sorted(logs, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        return pd.DataFrame(logs_sorted)
    except Exception as e:
        st.error(f"Failed to fetch audit logs: {e}")
        return pd.DataFrame()

logs_df = get_audit_logs()

if logs_df.empty:
    st.info("No audit log entries found.")
    st.stop()

# --- Filtering and Display ---
st.sidebar.header("Filter Logs")

# Filter by User
users = sorted(logs_df['user'].unique())
selected_user = st.sidebar.multiselect("Filter by User", options=users, default=[])

# Filter by Action
actions = sorted(logs_df['action'].unique())
selected_action = st.sidebar.multiselect("Filter by Action", options=actions, default=[])

# Filter by Status
statuses = sorted(logs_df['status'].unique())
selected_status = st.sidebar.multiselect("Filter by Status", options=statuses, default=[])

# Apply filters
filtered_df = logs_df.copy()
if selected_user:
    filtered_df = filtered_df[filtered_df['user'].isin(selected_user)]
if selected_action:
    filtered_df = filtered_df[filtered_df['action'].isin(selected_action)]
if selected_status:
    filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]

st.write(f"Displaying {len(filtered_df)} of {len(logs_df)} log entries.")

# --- Display DataFrame ---
# Improve display
display_df = filtered_df.copy()

# Convert timestamp to readable format
if 'timestamp' in display_df.columns:
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

# Select and reorder columns for clarity
display_columns = ['timestamp', 'user', 'action', 'status', 'result', 'parameters', 'keyword_parameters']
existing_columns = [col for col in display_columns if col in display_df.columns]

st.dataframe(display_df[existing_columns])

# --- Expand to see details ---
with st.expander("View Raw Log Details"):
    selected_index = st.selectbox("Select a log entry to inspect:", filtered_df.index)
    if selected_index is not None:
        st.json(filtered_df.loc[selected_index].to_dict())
