


import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ChatterFix Dashboard", layout="wide")

st.title("🔧 ChatterFix Maintenance Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["All Work Orders", "By Technician", "Overdue", "Completed"])

uploaded_file = st.file_uploader("Upload a Work Order Excel File", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File successfully uploaded!")
    with tab1:
        st.subheader("📋 All Work Orders")
        st.dataframe(df)

    with tab2:
        if "Status" in df.columns and "Assigned" in df.columns:
            st.subheader("🔍 Filter by Technician")
            techs = df["Assigned"].dropna().unique()
            selected_tech = st.selectbox("Choose Technician", techs)

            st.subheader("📆 Filter by Status")
            status_filter = st.selectbox("Choose Status", ["All", "Open", "In Progress", "Completed", "Closed"])
            
            filtered_df = df[df["Assigned"] == selected_tech]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["Status"] == status_filter]

            st.dataframe(filtered_df)

    with tab3:
        if "Due Date" in df.columns:
            st.subheader("🚨 Overdue Work Orders")
            overdue_df = df[pd.to_datetime(df["Due Date"], errors='coerce') < pd.Timestamp.now()]
            st.dataframe(overdue_df)

    with tab4:
        if "Completed Date" in df.columns:
            st.subheader("✅ Recently Completed Work Orders")
            recent_completed = df.sort_values("Completed Date", ascending=False).head(10)
            st.dataframe(recent_completed)
else:
    st.info("Please upload a work order spreadsheet to get started.")