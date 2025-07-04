import streamlit as st
from backend import synthetic_data
from frontend import auth_utils

# --- Page Config ---
st.set_page_config(page_title="Admin Tools", layout="wide")

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Admin Tools", allowed_roles=['admin'])
# --- End Auth Check ---

# --- Page Content ---
st.title("🛠️ Admin Tools")
st.markdown("Use these tools for system administration and testing.")

st.header("Database Management")
st.subheader("Generate Synthetic Data")

st.warning(
    "**DANGER ZONE:** This will delete all existing data (users, assets, work orders, etc.) "
    "and replace it with a new, randomly generated dataset. This action cannot be undone."
)

if st.button("🔥 Generate New Synthetic Dataset"):
    with st.spinner("Generating data... This may take a minute. Please do not navigate away."):
        try:
            success = synthetic_data.generate_synthetic_data()
            if success:
                st.success("✅ Successfully cleared the database and generated a new synthetic dataset!")
                st.info("You may need to log out and log back in with one of the new demo accounts (e.g., username: admin, password: password123).")
            else:
                st.error("An error occurred during data generation. Check the application logs.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.exception(e)
