import streamlit as st
import pandas as pd
import altair as alt
from backend import work_orders, assets, inventory, accounting # Corrected import
from datetime import datetime
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Reporting & KPIs", allowed_roles=['manager'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

st.title("📊 Reporting & KPIs")
st.markdown("Visualize maintenance operations and track key performance indicators.")

# --- Data Loading ---
@st.cache_data
def load_data():
    wo_data = [wo.__dict__ for wo in work_orders.get_all_work_orders()]
    asset_data = [a.__dict__ for a in assets.get_all_assets()]
    parts_data = [p.__dict__ for p in inventory.get_all_parts()] # Corrected function call
    transactions_data = [t.__dict__ for t in accounting.get_all_transactions()]
    return (
        pd.DataFrame(wo_data) if wo_data else pd.DataFrame(),
        pd.DataFrame(asset_data) if asset_data else pd.DataFrame(),
        pd.DataFrame(parts_data) if parts_data else pd.DataFrame(),
        pd.DataFrame(transactions_data) if transactions_data else pd.DataFrame(),
    )

try:
    work_orders_df, assets_df, parts_df, transactions_df = load_data()

    # --- Work Order Analysis ---
    if work_orders_df.empty:
        st.info("No work order data available to generate reports.")
    else:
        st.header("Work Order Analysis")

        # --- KPI Metrics ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Work Orders", len(work_orders_df))
        open_wos = work_orders_df[work_orders_df['status'] == 'open'].shape[0]
        col2.metric("Open Work Orders", open_wos)
        completed_wos = work_orders_df[work_orders_df['status'] == 'completed'].shape[0]
        col3.metric("Completed Work Orders", completed_wos)
        # Ensure 'created_at' is a datetime object for calculations
        work_orders_df['created_at'] = pd.to_datetime(work_orders_df['created_at'])
        avg_days_open = (datetime.now() - work_orders_df[work_orders_df['status'] == 'open']['created_at']).mean().days
        col4.metric("Avg. Days Open", f"{avg_days_open:.1f}" if avg_days_open else "N/A")


        # --- Charts ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Work Orders by Status")
            status_chart = alt.Chart(work_orders_df).mark_bar().encode(
                x=alt.X('status:N', title="Status"),
                y=alt.Y('count():Q', title="Number of Work Orders"),
                color='status:N'
            ).properties(
                height=300
            )
            st.altair_chart(status_chart, use_container_width=True)

        with col2:
            st.subheader("Work Orders by Priority")
            priority_chart = alt.Chart(work_orders_df).mark_bar().encode(
                x=alt.X('priority:N', title="Priority"),
                y=alt.Y('count():Q', title="Number of Work Orders"),
                color='priority:N'
            ).properties(
                height=300
            )
            st.altair_chart(priority_chart, use_container_width=True)

    # --- Asset Analysis ---
    if assets_df.empty:
        st.info("No asset data available to generate reports.")
    else:
        st.header("Asset Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Assets by Type")
            asset_type_chart = alt.Chart(assets_df).mark_arc(inner_radius=50).encode(
                theta=alt.Theta(field="asset_type", type="nominal"),
                color=alt.Color(field="asset_type", type="nominal", legend=None)
            ).properties(
                height=300
            )
            st.altair_chart(asset_type_chart, use_container_width=True)

        with col2:
            st.subheader("Assets by Status")
            asset_status_chart = alt.Chart(assets_df).mark_arc(inner_radius=50).encode(
                theta=alt.Theta(field="status", type="nominal"),
                color=alt.Color(field="status", type="nominal", legend=None)
            ).properties(
                height=300
            )
            st.altair_chart(asset_status_chart, use_container_width=True)

    # --- Parts Inventory Analysis ---
    if not parts_df.empty:
        st.header("Parts Inventory Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Part Stock Levels")
            # Sort by stock quantity for better visualization
            parts_df_sorted = parts_df.sort_values("stock_quantity", ascending=True)
            stock_chart = alt.Chart(parts_df_sorted).mark_bar().encode(
                x=alt.X('stock_quantity:Q', title="Stock Quantity"),
                y=alt.Y('name:N', title="Part Name", sort='-x'),
                tooltip=['name', 'part_number', 'stock_quantity', 'location']
            ).properties(
                height=350
            )
            st.altair_chart(stock_chart, use_container_width=True)
        with col2:
            st.subheader("Low Stock Items (<= 5)")
            low_stock_df = parts_df[parts_df['stock_quantity'] <= 5]
            if low_stock_df.empty:
                st.success("All parts are well-stocked.")
            else:
                st.dataframe(
                    low_stock_df[['name', 'part_number', 'stock_quantity', 'location']],
                    use_container_width=True
                )

    # --- Financial Summary ---
    if not transactions_df.empty:
        st.header("Financial Summary")
        col1, col2 = st.columns(2)
        with col1:
            total_spending = transactions_df['amount'].sum()
            st.metric("Total Recorded Spend", f"${total_spending:,.2f}")

        with col2:
            st.subheader("Spending by Type")
            spending_chart = alt.Chart(transactions_df).mark_arc(inner_radius=50).encode(
                theta=alt.Theta(field="amount", type="quantitative", aggregate="sum"),
                color=alt.Color(field="transaction_type", type="nominal", title="Transaction Type")
            ).properties(
                height=300
            )
            st.altair_chart(spending_chart, use_container_width=True)


except Exception as e:
    st.error(f"Failed to load reports: {e}")
