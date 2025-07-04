import streamlit as st
from backend.database import load_work_orders

def render_work_orders_page():
    st.title("🧾 Work Orders")

    orders = load_work_orders()
    for order in orders:
        st.subheader(order.title)
        st.markdown(f"- **Assigned To:** {order.assigned_to}")
        st.markdown(f"- **Status:** {order.status}")
        st.markdown(f"- **Priority:** {order.priority}")
        st.markdown(f"- **Due Date:** {order.due_date or 'N/A'}")
        st.markdown("---")

if __name__ == "__main__":
    render_work_orders_page()
