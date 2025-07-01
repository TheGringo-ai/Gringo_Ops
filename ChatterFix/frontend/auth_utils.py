import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# --- User Authentication and Role-Based Access Control ---

def display_auth_status():
    """Displays user login status and navigation in the sidebar."""
    if 'user' in st.session_state and st.session_state['user'] is not None:
        user = st.session_state['user']
        st.sidebar.success(f"Logged in as **{user.username}** ({user.role})")
        if st.sidebar.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()
    else:
        st.sidebar.warning("You are not logged in.")
        if st.sidebar.button("Login or Register"):
            switch_page("9_User_Authentication")

def is_logged_in():
    """Checks if a user is logged in."""
    return 'user' in st.session_state and st.session_state['user'] is not None

def has_permission(required_role):
    """Checks if the logged-in user has the required role."""
    if not is_logged_in():
        return False
    
    user_role = st.session_state['user'].role
    # Simple hierarchy: admin > manager > technician
    if required_role == 'admin' and user_role == 'admin':
        return True
    if required_role == 'manager' and user_role in ['manager', 'admin']:
        return True
    if required_role == 'technician' and user_role in ['technician', 'manager', 'admin']:
        return True
    return False
