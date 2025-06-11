


import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Fred Daily Dashboard", layout="wide")

st.title("🔧 FredFix Daily Maintenance Dashboard")

# Upload and cache data
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df
    return None

uploaded_file = st.file_uploader("Upload your Work Order Excel file", type=["xlsx"])
df = load_data(uploaded_file)

if df is not None:
    st.success("✅ Data loaded successfully")

    tabs = st.tabs(["📅 Daily Schedule", "⚠️ Past Due", "✅ Completed", "🧑‍🔧 By Technician", "📊 Summary"])

    with tabs[0]:
        st.subheader("📅 Daily Technician Schedule")
        today = pd.to_datetime("today").normalize()
        today_tasks = df[df["Due Date"].dt.normalize() == today]
        st.dataframe(today_tasks)

    with tabs[1]:
        st.subheader("⚠️ Past Due Work Orders")
        past_due = df[df["Due Date"] < pd.to_datetime("today")]
        st.dataframe(past_due)

    with tabs[2]:
        st.subheader("✅ Completed Work Orders")
        completed = df[df["Status"].str.lower() == "completed"]
        st.dataframe(completed)

    with tabs[3]:
        st.subheader("🧑‍🔧 Work Orders by Technician")
        if "Assigned To" in df.columns:
            technicians = df["Assigned To"].unique()
            selected_tech = st.selectbox("Select Technician", technicians)
            st.dataframe(df[df["Assigned To"] == selected_tech])
        else:
            st.warning("⚠️ 'Assigned To' column not found in dataset.")

    with tabs[4]:
        st.subheader("📊 Work Order Summary")
        st.metric("Total Work Orders", len(df))
        st.metric("Completed", len(df[df["Status"].str.lower() == "completed"]))
        st.metric("Past Due", len(df[df["Due Date"] < pd.to_datetime("today")]))
else:
    st.info("📂 Upload an Excel file to get started.")