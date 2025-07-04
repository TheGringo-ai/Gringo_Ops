import streamlit as st
import pandas as pd
from backend import users, models
from frontend.auth_utils import enforce_auth

# --- Page Configuration and Authentication ---
st.set_page_config(layout="wide")
st.title("👤 User Management")

enforce_auth(allowed_roles=['admin'])
user = st.session_state.get("user")
# --- End Authentication ---

# --- User Creation Form ---
st.header("Create New User")
with st.form("new_user_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", help="The unique username for login.")
        email = st.text_input("Email (Optional)")
    with col2:
        role = st.selectbox("Role", options=models.User.__annotations__['role'].__args__, help="Set the user's permissions.")
        password = st.text_input("Password", type="password", help="Set a temporary password for the user.")

    submitted = st.form_submit_button("Create User")
    if submitted:
        if not username or not password or not role:
            st.warning("Username, Password, and Role are required.")
        else:
            try:
                user_id = users.create_user(username, password, role, email)
                st.success(f"Successfully created user: {user_id}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create user: {e}")

# --- User Display and Management ---
st.header("Existing Users")
try:
    all_users = users.get_all_users()
    if not all_users:
        st.info("No users found.")
    else:
        user_data = [u.__dict__ for u in all_users]
        df = pd.DataFrame(user_data).set_index('id')
        st.dataframe(df[['username', 'role', 'email']], use_container_width=True)

        st.subheader("Update or Delete User")
        user_to_manage_id = st.selectbox("Select User", options=df.index)
        selected_user = all_users[df.index.get_loc(user_to_manage_id)]

        with st.expander(f"Manage {selected_user.username}"):
            new_email = st.text_input("New Email", value=selected_user.email, key=f"email_{user_to_manage_id}")
            new_role = st.selectbox("New Role", options=models.User.__annotations__['role'].__args__, index=models.User.__annotations__['role'].__args__.index(selected_user.role), key=f"role_{user_to_manage_id}")
            new_password = st.text_input("New Password (leave blank to keep unchanged)", type="password", key=f"pw_{user_to_manage_id}")

            col1, col2 = st.columns([1, 6])
            with col1:
                if st.button("Update User", key=f"update_{user_to_manage_id}"):
                    updates = {
                        "email": new_email,
                        "role": new_role
                    }
                    if new_password:
                        updates['password'] = new_password
                    try:
                        users.update_user(user_to_manage_id, updates)
                        st.success(f"Successfully updated {user_to_manage_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update user: {e}")
            with col2:
                 if st.button("Delete User", type="primary", key=f"delete_{user_to_manage_id}"):
                    if user_to_manage_id == user.get('id'):
                        st.error("You cannot delete yourself.")
                    else:
                        try:
                            users.delete_user(user_to_manage_id)
                            st.success(f"Successfully deleted {user_to_manage_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete user: {e}")

except Exception as e:
    st.error("Failed to load users.")
    st.exception(e)
