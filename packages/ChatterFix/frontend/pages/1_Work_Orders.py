import streamlit as st
import pandas as pd
from backend import work_orders, models, assets, users
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Work Order Management", allowed_roles=['manager', 'technician'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

# --- Page Title and Header ---
st.title("🛠️ Work Order Management")
st.markdown("""
Create, view, and manage all work orders.
""")

# --- Fetch data for forms ---
try:
    all_assets = assets.get_all_assets()
    asset_options = {asset.id: f"{asset.name} (ID: {asset.id})" for asset in all_assets}
except Exception as e:
    st.error(f"Failed to load assets: {e}")
    asset_options = {}

try:
    all_users = users.get_all_users()
    # Filter for users who can be assigned tasks
    assignable_users = [user for user in all_users if user.get('role') in ['technician', 'manager']]
    user_options = {user['id']: user['username'] for user in assignable_users}
except Exception as e:
    st.error(f"Failed to load users: {e}")
    user_options = {}


# --- Work Order Creation Form ---
st.header("Create New Work Order")
with st.form("new_work_order_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", help="A brief, descriptive title for the work order.")
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"], help="The urgency of the work order.")
        equipment_id = st.selectbox("Equipment/Asset", options=list(asset_options.keys()), format_func=lambda x: asset_options[x], help="The asset related to this work order.")
    with col2:
        description = st.text_area("Description", help="A detailed description of the issue or task.")
        assigned_to_id = st.selectbox("Assign To (Optional)", options=[""] + list(user_options.keys()), format_func=lambda x: user_options.get(x, "Unassigned"), help="Assign the work order to a specific user.")


    submitted = st.form_submit_button("Create Work Order")
    if submitted:
        if not title or not description:
            st.warning("Please fill out both Title and Description.")
        else:
            try:
                work_order_id = work_orders.create_work_order(
                    title=title,
                    description=description,
                    priority=priority,
                    equipment_id=equipment_id,
                    assigned_to_id=assigned_to_id
                )
                st.success(f"Successfully created work order: {work_order_id}")
                st.rerun() # Rerun to update the list
            except Exception as e:
                st.error(f"Failed to create work order: {e}")


# --- Work Order Display ---
st.header("Current Work Orders")

try:
    all_work_orders = work_orders.get_all_work_orders()

    if not all_work_orders:
        st.info("No work orders found. Create one above!")
    else:
        # Convert list of dataclasses to list of dicts for DataFrame
        work_orders_data = [wo.__dict__ for wo in all_work_orders]
        df = pd.DataFrame(work_orders_data)

        # Create a mapping for better display names
        df['asset_name'] = df['equipment_id'].apply(lambda x: asset_options.get(x, 'N/A'))
        df['assigned_to_name'] = df['assigned_to_id'].apply(lambda x: user_options.get(x, 'Unassigned'))


        # Reorder and select columns for display
        display_columns = [
            'id', 'title', 'status', 'priority', 'asset_name', 'assigned_to_name', 'created_at'
        ]
        df_display = df[display_columns].copy()
        df_display.rename(columns={'asset_name': 'Asset', 'assigned_to_name': 'Assigned To'}, inplace=True)


        st.dataframe(df_display, use_container_width=True)

        st.subheader("Update Work Order")
        # Allow managers/admins to update
        if user.role in ['manager', 'admin']:
            wo_to_update_id = st.selectbox("Select Work Order to Update", options=df['id'])
            selected_wo = df[df['id'] == wo_to_update_id].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox(
                    "New Status",
                    options=models.WorkOrder.__annotations__['status'].__args__,
                    index=models.WorkOrder.__annotations__['status'].__args__.index(selected_wo['status']),
                    key=f"status_{wo_to_update_id}"
                )
            with col2:
                new_assignee_id = st.selectbox(
                    "Assign To",
                    options=[""] + list(user_options.keys()),
                    format_func=lambda x: user_options.get(x, "Unassigned"),
                    index= (list(user_options.keys()).index(selected_wo['assigned_to_id']) + 1) if selected_wo['assigned_to_id'] in user_options else 0,
                    key=f"assignee_{wo_to_update_id}"
                )

            if st.button("Update Work Order", key=f"update_{wo_to_update_id}"):
                try:
                    # Check for status change
                    if new_status != selected_wo['status']:
                        work_orders.update_work_order_status(wo_to_update_id, new_status, user.username)
                        st.success(f"Updated status for WO {wo_to_update_id}.")

                    # Check for assignment change
                    if new_assignee_id != selected_wo['assigned_to_id']:
                         work_orders.assign_work_order(wo_to_update_id, new_assignee_id, user.username)
                         st.success(f"Assigned WO {wo_to_update_id} to {user_options.get(new_assignee_id, 'Unassigned')}.")

                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update work order: {e}")

except Exception as e:
    st.error(f"Failed to load work orders: {e}")
    st.exception(e) # show full traceback for debugging
