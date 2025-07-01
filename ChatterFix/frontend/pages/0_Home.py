import streamlit as st
from backend import work_orders, predictive # Import the predictive backend

# --- Page Config ---
st.set_page_config(page_title="ChatterFix Home", layout="wide")

# --- Check Login Status ---
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.stop()

user = st.session_state.get("user")
if not user:
    st.error("User information not found. Please log in again.")
    st.stop()

# --- Header ---
st.title(f"🏠 Welcome to ChatterFix, {user.username.capitalize()}!")
st.markdown("This is your central hub for managing all maintenance operations. Select a page from the sidebar to get started.")

# --- Role-Based Welcome Message ---
st.header("Your Dashboard")

if user.role == 'manager':
    st.info("As a **Manager**, you have full access to all modules, including reporting and financial data. Use the sidebar to navigate.")

    # --- AI-Suggested Work Orders ---
    st.header("🤖 AI-Suggested Work Orders")

    # Add a button to manually trigger the analysis
    if st.button("🧠 Run AI Analysis to Find New Suggestions"):
        with st.spinner("Running predictive models on all assets... This may take a moment."):
            try:
                new_suggestions = predictive.generate_suggested_work_orders()
                if new_suggestions:
                    st.success(f"Analysis complete! Found {len(new_suggestions)} new suggestion(s).")
                else:
                    st.info("Analysis complete. No new maintenance suggestions at this time.")
                st.rerun() # Rerun to refresh the list of suggestions
            except Exception as e:
                st.error(f"An error occurred during AI analysis: {e}")

    suggested_wos = work_orders.get_work_orders_by_status('suggested')

    if not suggested_wos:
        st.success("No new AI suggestions at the moment. The system is monitoring asset health.")
    else:
        st.warning(f"You have {len(suggested_wos)} new work order suggestion(s) to review.")
        for wo in suggested_wos:
            with st.expander(f"**{wo.title}** (Priority: {wo.priority.capitalize()})"):
                st.markdown(f"**Description:** {wo.description}")
                st.markdown(f"**Asset ID:** `{wo.equipment_id}`")
                st.markdown(f"**Suggested On:** {wo.created_at.strftime('%Y-%m-%d %H:%M')}")

                col1, col2, col3 = st.columns([1, 1, 8])
                with col1:
                    if st.button("✅ Approve", key=f"approve_{wo.id}"):
                        try:
                            work_orders.update_work_order_status(wo.id, 'open', user.username)
                            st.success(f"Work Order '{wo.title}' approved and moved to Open.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error approving work order: {e}")
                with col2:
                    if st.button("❌ Reject", key=f"reject_{wo.id}"):
                        try:
                            work_orders.update_work_order_status(wo.id, 'cancelled', user.username)
                            st.success(f"Work Order '{wo.title}' has been rejected and cancelled.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error rejecting work order: {e}")

elif user.role == 'technician':
    st.info("As a **Technician**, you can manage work orders, view assets, and check parts inventory. Use the sidebar to access your tools.")
else: # Admin or other roles
    st.info("You have **Admin** privileges and can access all system functionalities.")

# --- Quick Stats (Future Enhancement) ---
# We can add some high-level KPIs here later
# col1, col2, col3 = st.columns(3)
# col1.metric("Open Work Orders", "12")
# col2.metric("Assets Due for Maintenance", "3")
# col3.metric("Low Stock Parts", "8")
