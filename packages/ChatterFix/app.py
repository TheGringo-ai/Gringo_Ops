import streamlit as st
from pages import Chat, Work_Orders

st.set_page_config(
    page_title="ChatterFix - The AI-Powered CMMS",
    page_icon="🔧",
    layout="wide",
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.switch_page("pages/1_Login.py")

# Main App
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Work Orders"])

if page == "Chat":
    Chat
elif page == "Work Orders":
    Work_Orders
