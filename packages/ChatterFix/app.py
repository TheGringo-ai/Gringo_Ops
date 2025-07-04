import streamlit as st

st.set_page_config(
    page_title="ChatterFix - The AI-Powered CMMS",
    page_icon="🔧",
    layout="wide",
)

st.title("Welcome to ChatterFix!")
st.write("This is the main entrypoint for the ChatterFix application.")
st.write("Use the sidebar to navigate to the different modules.")

st.sidebar.success("Select a module above.")
