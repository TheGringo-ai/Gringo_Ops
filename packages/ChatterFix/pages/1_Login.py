import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# --- Firebase Initialization ---
# This should only be done once
if not firebase_admin._apps:
    try:
        # Try to load from Streamlit secrets first (for deployment)
        cred_json = st.secrets["firebase_service_account"]
        cred = credentials.Certificate(cred_json)
    except (KeyError, FileNotFoundError):
        # Fallback to local file for development
        cred = credentials.Certificate("gcp-service-account-key.json")
    
    firebase_admin.initialize_app(cred)

st.set_page_config(page_title="Login - ChatterFix", layout="centered")

def login_user(email, password):
    """Logs a user in with email and password."""
    try:
        user = auth.get_user_by_email(email)
        # This is a simplified check. In a real app, you'd verify the password.
        # Firebase Admin SDK doesn't verify passwords directly.
        # This is typically handled on the client-side with Firebase Client SDKs.
        st.session_state.logged_in = True
        st.session_state.user_email = user.email
        st.success("Logged in successfully!")
        st.experimental_rerun()
    except auth.UserNotFoundError:
        st.error("User not found.")
    except Exception as e:
        st.error(f"Login failed: {e}")

def signup_user(email, password):
    """Creates a new user with email and password."""
    try:
        user = auth.create_user(email=email, password=password)
        st.session_state.logged_in = True
        st.session_state.user_email = user.email
        st.success("Account created successfully! You are now logged in.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Signup failed: {e}")

# --- UI ---
st.title("Welcome to ChatterFix")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    choice = st.selectbox("Login or Signup?", ["Login", "Signup"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_user(email, password)
    else:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Signup"):
            signup_user(email, password)
else:
    st.write(f"You are logged in as: {st.session_state.user_email}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
