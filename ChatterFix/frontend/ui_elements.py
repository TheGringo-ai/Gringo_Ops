

# ui_elements.py
# Contains reusable Streamlit UI components for ChatterFix

import streamlit as st

def section_title(title: str):
    st.markdown(f"### {title}")

def divider():
    st.markdown("---")

def status_badge(text: str, color: str = "green"):
    st.markdown(f"<span style='color: {color}; font-weight: bold;'>{text}</span>", unsafe_allow_html=True)