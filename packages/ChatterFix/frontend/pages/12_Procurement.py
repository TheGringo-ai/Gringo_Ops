"""
Streamlit-based Frontend for Supply Chain and Procurement
"""
import streamlit as st
from backend import procurement as procurement_service
from backend import inventory as inventory_service
from backend import models
from frontend.auth_utils import enforce_auth

st.set_page_config(layout="wide", page_title="Procurement")

def display_supplier_management():
    """UI for managing suppliers."""
    st.subheader("Supplier Management")

    with st.expander("Add New Supplier", expanded=False):
        with st.form("new_supplier_form", clear_on_submit=True):
            name = st.text_input("Supplier Name")
            contact = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_area("Address")
            submitted = st.form_submit_button("Add Supplier")
            if submitted and name:
                try:
                    procurement_service.create_supplier(name, contact, email, phone, address)
                    st.success(f"Supplier '{name}' added successfully.")
                except Exception as e:
                    st.error(f"Error adding supplier: {e}")

    st.markdown("--- ")
    st.subheader("Existing Suppliers")
    all_suppliers = procurement_service.get_all_suppliers()
    if not all_suppliers:
        st.info("No suppliers found. Add one above.")
        return

    for supplier in all_suppliers:
        with st.container():
            st.markdown(f"**{supplier.name}** (ID: `{supplier.id}`)")
            st.caption(f"Contact: {supplier.contact_person or 'N/A'} | Email: {supplier.email or 'N/A'} | Phone: {supplier.phone or 'N/A'}")
            st.markdown("--- ")

def display_purchase_orders():
    """UI for managing Purchase Orders."""
    st.subheader("Purchase Order Management")

    # --- Automated PO Generation ---
    st.info("The system can automatically generate purchase orders for parts that are below their low-stock threshold.")
    if st.button("Run Low Stock Check & Generate POs"):
        with st.spinner("Checking inventory levels..."):
            user_id = st.session_state.user['id']
            created_pos = procurement_service.check_inventory_and_generate_po(user_id)
            if created_pos:
                st.success(f"Generated {len(created_pos)} new purchase orders for approval.")
                st.balloons()
            else:
                st.info("All parts are currently in stock. No new purchase orders needed.")

    st.markdown("--- ")
    st.subheader("All Purchase Orders")
    all_pos = procurement_service.get_all_purchase_orders()
    if not all_pos:
        st.info("No purchase orders found.")
        return

    for po in all_pos:
        with st.container():
            supplier = procurement_service.get_supplier(po.supplier_id)
            st.markdown(f"**PO ID:** `{po.id}` | **Supplier:** {supplier.name if supplier else 'N/A'}")
            st.markdown(f"**Status:** `{po.status}` | **Total Cost:** ${po.total_cost:,.2f}")
            st.caption(f"Ordered on: {po.order_date.strftime('%Y-%m-%d %H:%M')}")

            with st.expander("View Details"):
                for item in po.items:
                    part = inventory_service.get_part(item['part_id'])
                    st.markdown(f"- **{item['quantity']}x** {part.name if part else 'Unknown Part'} @ ${item['unit_price']:,.2f} each")
                if po.notes:
                    st.info(f"Notes: {po.notes}")

            # --- Actions based on Status ---
            if po.status == 'pending_approval':
                if st.button("Approve & Order", key=f"approve_{po.id}"):
                    procurement_service.update_purchase_order_status(po.id, 'ordered')
                    st.success(f"PO {po.id} approved and status set to 'Ordered'.")
                    st.rerun()
            
            elif po.status == 'ordered' or po.status == 'shipped':
                if st.button("Receive Items", key=f"receive_{po.id}"):
                    # In a real app, you'd have a form to confirm quantities.
                    # For now, we assume all items are received as ordered.
                    received_items = [{'part_id': i['part_id'], 'quantity_received': i['quantity']} for i in po.items]
                    result = procurement_service.receive_purchase_order_items(po.id, received_items, st.session_state.user['id'])
                    st.success(result)
                    st.rerun()

            st.markdown("--- ")

def main():
    """Main function to render the page."""
    st.title("🚚 Supply Chain & Procurement")

    enforce_auth(allowed_roles=['admin', 'manager'])

    tab1, tab2 = st.tabs(["Purchase Orders", "Suppliers"])

    with tab1:
        display_purchase_orders()

    with tab2:
        display_supplier_management()


if __name__ == "__main__":
    main()
