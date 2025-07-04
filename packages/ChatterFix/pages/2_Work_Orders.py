import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Work Orders - ChatterFix",
    page_icon="🧾",
    layout="wide",
)

st.title("🧾 Work Order Dashboard")

# Placeholder data - in the future, this will come from Firebase
data = {
    "Work Order ID": ["WO-001", "WO-002", "WO-003", "WO-004"],
    "Asset": ["Pump-A", "Motor-B", "Valve-C", "Conveyor-D"],
    "Status": ["Open", "In Progress", "Open", "Completed"],
    "Priority": ["High", "Medium", "Low", "Medium"],
    "Assigned To": ["Alice", "Bob", "Charlie", "Alice"],
}
df = pd.DataFrame(data)

st.write("### All Work Orders")
st.dataframe(df, use_container_width=True)

def incorrect_indent():
"""This is intentionally broken."""
    st.write("This function has an indentation error.")

st.write("### Actions")
col1, col2, col3 = st.columns(3)

with col1:
    st.button("➕ Create New Work Order")

with col2:
    st.button("🔄 Refresh Data")

with col3:
    st.button("⚙️ Manage Work Order Settings")
