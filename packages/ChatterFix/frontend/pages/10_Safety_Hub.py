import streamlit as st
import pandas as pd
from backend import safety, users, models
from frontend.auth_utils import enforce_auth

# --- Page Config and Auth ---
st.set_page_config(layout="wide")
st.title("⛑️ Safety Hub")

enforce_auth()

user = st.session_state.get("user")
# --- End Auth ---

# --- Data Loading ---
try:
    all_users = users.get_all_users()
    user_options = {u.id: u.username for u in all_users}
except Exception as e:
    st.error(f"Failed to load users: {e}")
    user_options = {}

# --- UI Tabs ---
tab1, tab2, tab3 = st.tabs(["Report Incident", "Incident Log", "Log Safety Meeting"])

with tab1:
    st.header("Report a New Safety Incident")
    with st.form("new_incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            incident_type = st.selectbox("Incident Type", options=models.SafetyIncident.__annotations__['incident_type'].__args__)
            severity = st.selectbox("Severity", options=models.SafetyIncident.__annotations__['severity'].__args__)
            location = st.text_input("Location")
        with col2:
            description = st.text_area("Full Description")
        
        involved_parties = st.multiselect("Involved Parties (Optional)", options=list(user_options.keys()), format_func=lambda x: user_options[x])
        create_work_order = st.checkbox("Generate a corrective action work order?", value=True)

        submitted = st.form_submit_button("Submit Incident Report")
        if submitted:
            try:
                safety.report_incident(
                    incident_type=incident_type,
                    location=location,
                    description=description,
                    severity=severity,
                    reported_by=user['id'],
                    involved_parties=involved_parties,
                    create_work_order=create_work_order
                )
                st.success("Successfully reported incident.")
            except Exception as e:
                st.error(f"Failed to report incident: {e}")

with tab2:
    st.header("Safety Incident Log")
    try:
        all_incidents = safety.get_all_incidents()
        if not all_incidents:
            st.info("No safety incidents have been reported.")
        else:
            incident_data = [i.__dict__ for i in all_incidents]
            df = pd.DataFrame(incident_data)
            df['reported_by_name'] = df['reported_by'].apply(lambda x: user_options.get(x, 'Unknown'))
            
            display_cols = ['id', 'incident_type', 'severity', 'status', 'location', 'reported_by_name', 'timestamp']
            st.dataframe(df[display_cols], use_container_width=True)

            # --- Incident Update Section (for Admins/Managers) ---
            if user.get('role') in ['admin', 'manager']:
                st.subheader("Update Incident Status")
                incident_to_update_id = st.selectbox("Select Incident", options=df['id'])
                selected_incident = df[df['id'] == incident_to_update_id].iloc[0]

                with st.expander(f"Update Incident #{selected_incident['id']}"):
                    new_status = st.selectbox("New Status", options=models.SafetyIncident.__annotations__['status'].__args__, index=models.SafetyIncident.__annotations__['status'].__args__.index(selected_incident['status']))
                    corrective_action = st.text_area("Corrective Action Taken", value=selected_incident['corrective_action_taken'])

                    if st.button("Update Incident"): 
                        try:
                            safety.update_incident_status(incident_to_update_id, new_status, corrective_action)
                            st.success("Incident updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update: {e}")

    except Exception as e:
        st.error(f"Failed to load incidents: {e}")

with tab3:
    st.header("Log a New Safety Meeting")
    with st.form("new_meeting_form", clear_on_submit=True):
        topic = st.text_input("Meeting Topic")
        attendees = st.multiselect("Attendees", options=list(user_options.keys()), format_func=lambda x: user_options[x])
        notes = st.text_area("Meeting Notes")
        
        submitted = st.form_submit_button("Log Meeting")
        if submitted:
            if not topic or not attendees:
                st.warning("Topic and Attendees are required.")
            else:
                try:
                    safety.log_safety_meeting(topic, attendees, user['id'], notes)
                    st.success("Successfully logged safety meeting.")
                except Exception as e:
                    st.error(f"Failed to log meeting: {e}")

    st.header("Recent Safety Meetings")
    try:
        all_meetings = safety.get_all_safety_meetings()
        if not all_meetings:
            st.info("No safety meetings have been logged.")
        else:
            meeting_data = [m.__dict__ for m in all_meetings]
            df_meetings = pd.DataFrame(meeting_data)
            df_meetings['conducted_by_name'] = df_meetings['conducted_by'].apply(lambda x: user_options.get(x, 'Unknown'))
            df_meetings['attendee_names'] = df_meetings['attendees'].apply(lambda ids: ", ".join([user_options.get(id, 'Unknown') for id in ids]))
            st.dataframe(df_meetings[['topic', 'conducted_by_name', 'attendee_names', 'timestamp']], use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load meetings: {e}")
