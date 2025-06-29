import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page

# To access the backend, we need to add the project root to the Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ChatterFix.backend import app as backend
from ChatterFix.backend import documents as documents_backend
from ChatterFix.backend import ai_assistant as ai
from ChatterFix.backend import models
from ChatterFix.frontend.auth_utils import display_auth_status, is_logged_in, has_permission

st.set_page_config(page_title="ChatterFix CMMS", layout="wide")

# --- Authentication and Sidebar ---
display_auth_status()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
if st.sidebar.button("Asset Management"):
    switch_page("7_Asset_Management")
if st.sidebar.button("Parts Management"):
    switch_page("8_Parts_Management")


# --- Main Dashboard View ---
st.title("🤖 ChatterFix - The Intelligent CMMS")
st.markdown("Welcome to the central dashboard for managing all maintenance operations.")

# --- Work Order Creation (Sidebar) ---
if has_permission('technician'):
    st.sidebar.title("📝 Create New Work Order")
    with st.sidebar.form("new_work_order_form", clear_on_submit=True):
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ['low', 'medium', 'high', 'critical'])
        # In a real app, these would be dynamic lookups
        equipment_id = st.text_input("Equipment ID (Optional)")
        assigned_to_id = st.text_input("Assign to User ID (Optional)")
        submitted = st.form_submit_button("Create Work Order")

        if submitted and title and description:
            try:
                new_id = backend.create_work_order(
                    title=title, 
                    description=description, 
                    priority=priority,
                    equipment_id=equipment_id,
                    assigned_to_id=assigned_to_id
                )
                st.sidebar.success(f"✅ Successfully created Work Order: {new_id}")
                st.experimental_rerun() # Refresh the main display
            except Exception as e:
                st.sidebar.error(f"❌ Error creating work order: {e}")

# --- Work Order Display ---
if not is_logged_in():
    st.warning("Please log in to view work orders.")
else:
    st.header("Work Orders")
    try:
        all_work_orders = backend.get_all_work_orders()
        if not all_work_orders:
            st.info("No work orders found. Create one using the form on the left.")
        else:
            for wo in sorted(all_work_orders, key=lambda x: x.created_at, reverse=True):
                with st.expander(f"**{wo.title}** (Priority: {wo.priority}, Status: {wo.status}) - ID: {wo.id}"):
                    st.markdown(f"**Description:** {wo.description}")
                    st.markdown(f"**Created:** {wo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Equipment ID:** {wo.equipment_id or 'N/A'}")
                    st.markdown(f"**Assigned To:** {wo.assigned_to_id or 'N/A'}")

                    # --- AI Assistant ---
                    st.subheader("🤖 AI Assistant")
                    if st.button("Get Troubleshooting Suggestion", key=f"ai_{wo.id}"):
                        with st.spinner("The AI is thinking..."):
                            suggestion = ai.get_troubleshooting_suggestion(wo.id)
                            st.markdown(suggestion)

                    # --- Status Update ---
                    if has_permission('technician'):
                        st.subheader("Update Status")
                        current_status_index = models.WorkOrder.__annotations__['status'].__args__.index(wo.status)
                        new_status = st.selectbox(
                            "New Status",
                            options=models.WorkOrder.__annotations__['status'].__args__,
                            index=current_status_index,
                            key=f"status_{wo.id}"
                        )
                        if st.button("Update Status", key=f"update_{wo.id}"):
                            backend.update_work_order_status(wo.id, new_status, st.session_state.user.username)
                            st.success("Status updated!")
                            st.experimental_rerun()

                    # --- Document Management ---
                    if has_permission('technician'):
                        st.subheader("📄 Documents")
                        uploaded_file = st.file_uploader(
                            "Upload a document (manual, photo, etc.)",
                            key=f"upload_{wo.id}"
                        )
                        if uploaded_file:
                            try:
                                doc_id = documents_backend.upload_document(
                                    file=uploaded_file,
                                    related_to_id=wo.id,
                                    uploaded_by=st.session_state.user.username
                                )
                                st.success(f"Uploaded {uploaded_file.name} successfully!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to upload file: {e}")

                    # Display existing documents
                    st.markdown("**Attached Documents:**")
                    work_order_docs = documents_backend.get_documents_for(wo.id)
                    if not work_order_docs:
                        st.info("No documents attached to this work order.")
                    else:
                        for doc in work_order_docs:
                            st.markdown(f"[{doc.file_name}]({doc.storage_path}) - Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d')}")


                    # --- History ---
                    st.subheader("📜 History")
                    if not wo.history:
                        st.info("No history for this work order.")
                    else:
                        # Sort history from newest to oldest
                        sorted_history = sorted(wo.history, key=lambda x: x['timestamp'], reverse=True)
                        for entry in sorted_history:
                            st.markdown(f"- **{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}** ({entry['user']}): {entry['action']}")


    except Exception as e:
        st.error(f"❌ Failed to load work orders: {e}. Is the backend running and configured?")

# --- Placeholder for future features ---
# st.header("🔍 Search & Analytics")
