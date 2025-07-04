"""
Streamlit-based Frontend for Production Planning & Management
"""
import streamlit as st
from backend import production as production_service
from backend import inventory as inventory_service
from backend import models
from frontend.auth_utils import enforce_auth

st.set_page_config(layout="wide", page_title="Production Planning")

def display_bom_management():
    """UI for managing Bills of Materials."""
    st.subheader("Bill of Materials (BOM) Management")

    # --- Create New BOM Form ---
    with st.expander("Create New Bill of Materials", expanded=False):
        with st.form("new_bom_form", clear_on_submit=True):
            bom_name = st.text_input("BOM Name/Identifier")
            bom_description = st.text_area("BOM Description")

            st.write("Add Components:")
            all_parts = inventory_service.get_all_parts()
            part_options = {f"{p.name} (ID: {p.id})": p.id for p in all_parts}

            if 'components' not in st.session_state:
                st.session_state.components = []

            def add_component():
                st.session_state.components.append({"part_id": "", "quantity": 1})

            for i, component in enumerate(st.session_state.components):
                col1, col2, col3 = st.columns([3, 1, 1])
                selected_key = col1.selectbox(f"Part #{i+1}", options=part_options.keys(), key=f"part_{i}")
                st.session_state.components[i]['part_id'] = part_options[selected_key]
                st.session_state.components[i]['quantity'] = col2.number_input("Quantity", min_value=1, value=component['quantity'], key=f"qty_{i}")
                if col3.button("Remove", key=f"remove_{i}"):
                    st.session_state.components.pop(i)
                    st.rerun()

            st.button("Add Another Component", on_click=add_component)

            submitted = st.form_submit_button("Create BOM")
            if submitted:
                if not bom_name or not st.session_state.components:
                    st.warning("BOM Name and at least one component are required.")
                else:
                    try:
                        bom_id = production_service.create_bill_of_materials(
                            name=bom_name,
                            description=bom_description,
                            components=st.session_state.components
                        )
                        st.success(f"Successfully created BOM: {bom_id}")
                        st.session_state.components = [] # Clear for next form
                    except Exception as e:
                        st.error(f"Error creating BOM: {e}")

    # --- Display Existing BOMs ---
    st.markdown("--- ")
    st.subheader("Existing Bills of Materials")
    all_boms = production_service.get_all_bills_of_materials()
    if not all_boms:
        st.info("No Bills of Materials found.")
        return

    for bom in all_boms:
        with st.container():
            st.markdown(f"**{bom.name}** (ID: `{bom.id}`)")
            st.caption(f"Description: {bom.description or 'N/A'}")
            st.write("**Components:**")
            for comp in bom.components:
                part = inventory_service.get_part(comp['part_id'])
                part_name = f"{part.name} (ID: {part.id})" if part else f"Unknown Part (ID: {comp['part_id']})"
                st.markdown(f"- **{comp['quantity']}x** {part_name}")
            st.markdown("--- ")

def display_production_orders():
    """UI for managing Production Orders."""
    st.subheader("Production Order Management")

    # --- Create New Production Order Form ---
    with st.expander("Create New Production Order", expanded=False):
        with st.form("new_order_form", clear_on_submit=True):
            all_boms = production_service.get_all_bills_of_materials()
            bom_options = {f"{b.name} (ID: {b.id})": b.id for b in all_boms}

            selected_bom_key = st.selectbox("Select Bill of Materials", options=bom_options.keys())
            order_quantity = st.number_input("Quantity to Produce", min_value=1, value=1)
            order_notes = st.text_area("Notes")

            submitted = st.form_submit_button("Create Production Order")
            if submitted:
                if not selected_bom_key:
                    st.warning("Please select a Bill of Materials.")
                else:
                    try:
                        bom_id = bom_options[selected_bom_key]
                        order_id = production_service.create_production_order(
                            bom_id=bom_id,
                            quantity=order_quantity,
                            notes=order_notes
                        )
                        st.success(f"Successfully created Production Order: {order_id}")
                    except Exception as e:
                        st.error(f"Error creating order: {e}")

    # --- Display Existing Production Orders ---
    st.markdown("--- ")
    st.subheader("Current Production Orders")
    all_orders = production_service.get_all_production_orders()

    if not all_orders:
        st.info("No active production orders.")
        return

    for order in all_orders:
        with st.container():
            col1, col2, col3 = st.columns(3)
            bom = production_service.get_bill_of_materials(order.bom_id)
            col1.markdown(f"**Order ID:** `{order.id}`")
            col2.markdown(f"**BOM:** {bom.name if bom else 'Unknown'}")
            col3.markdown(f"**Quantity:** {order.quantity}")

            st.markdown(f"**Status:** {order.status}")
            st.caption(f"Created: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
            if order.notes:
                st.info(f"Notes: {order.notes}")

            # --- Status Update & Inventory Check ---
            if order.status == "Pending":
                if st.button("Start Production", key=f"start_{order.id}"):
                    with st.spinner("Checking inventory and starting production..."):
                        result = production_service.update_production_order_status(order.id, "In Progress", "system") # Assuming system user for now
                        if result.startswith("Error:"):
                            st.error(result)
                        else:
                            st.success(result)
                            st.rerun()

            elif order.status == "In Progress":
                if st.button("Complete Production", key=f"complete_{order.id}"):
                     production_service.update_production_order_status(order.id, "Completed", "system")
                     st.success("Order marked as complete!")
                     st.rerun()

            st.markdown("--- ")


def main():
    """Main function to render the page."""
    st.title("🏭 Production Planning and Control")

    enforce_auth(allowed_roles=['admin', 'manager'])

    tab1, tab2 = st.tabs(["Production Orders", "Bill of Materials"])

    with tab1:
        display_production_orders()

    with tab2:
        display_bom_management()


if __name__ == "__main__":
    main()
