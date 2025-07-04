import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ChatterFix.backend import auth as auth_backend

st.set_page_config(page_title="User Authentication", layout="centered")

st.title("👤 User Authentication")

# Check if the user is already logged in
if 'user' in st.session_state and st.session_state.user is not None:
    st.write(f"Welcome, {st.session_state.user.username}!")
    if st.button("Log Out"):
        del st.session_state.user
        st.success("You have been logged out.")
        st.experimental_rerun()
    if st.button("Go to Dashboard"):
        switch_page("6_ChatterFix")

else:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.header("Login")
        with st.form("login_form"): 
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if login_email and login_password:
                    try:
                        # In a real app, this would be a secure sign-in.
                        # Here, we are using a placeholder function.
                        user_record = auth_backend.sign_in_with_email_and_password(login_email, login_password)
                        user_details = auth_backend.get_user_from_firestore(user_record.uid)
                        st.session_state.user = user_details
                        st.success("Logged in successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")
                else:
                    st.warning("Please enter both email and password.")

    with tab2:
        st.header("Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")
            reg_role = st.selectbox("Role", ['technician', 'manager', 'admin'])
            register_button = st.form_submit_button("Register")

            if register_button:
                if reg_username and reg_email and reg_password and reg_role:
                    try:
                        auth_backend.create_user_with_email_and_password(
                            email=reg_email,
                            password=reg_password,
                            username=reg_username,
                            role=reg_role
                        )
                        st.success("Registration successful! Please log in.")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
                else:
                    st.warning("Please fill out all fields.")
