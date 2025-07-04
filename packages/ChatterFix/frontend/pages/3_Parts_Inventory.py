import streamlit as st
import pandas as pd
from backend import inventory, models # Updated import
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Parts Inventory", allowed_roles=['manager', 'technician'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

# --- Page Title and Header ---
st.title("📦 Warehouse & Inventory Management")
st.markdown("""
Manage your inventory, track stock levels, and get alerts for low-stock items.
""")

# --- Data Loading ---
try:
    all_parts = inventory.get_all_parts()
    low_stock_parts = inventory.get_low_stock_parts()
except Exception as e:
    st.error(f"Failed to load inventory data: {e}")
    all_parts = []
    low_stock_parts = []

# --- Low Stock Alerts ---
st.header("🚨 Low Stock Alerts")
if not low_stock_parts:
    st.success("All parts are above their low-stock thresholds.")
else:
    st.warning(f"There are {len(low_stock_parts)} items that need reordering.")
    low_stock_df = pd.DataFrame([p.__dict__ for p in low_stock_parts])
    st.dataframe(low_stock_df[['name', 'part_number', 'stock_quantity', 'low_stock_threshold', 'location']], use_container_width=True)

# --- UI Tabs for Management ---
tab1, tab2 = st.tabs(["Full Inventory List", "Add & Manage Parts"])

with tab1:
    st.header("Current Full Inventory")
    if not all_parts:
        st.info("No parts found in inventory. Add one in the 'Add & Manage Parts' tab.")
    else:
        for part in all_parts:
            with st.expander(f"{part.name} - {part.part_number}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Category:** {part.category}")
                    st.write(f"**Location:** {part.location}")
                    st.write(f"**Supplier:** {part.supplier}")
                    st.write(f"**Stock Quantity:** {part.stock_quantity}")
                    st.write(f"**Low Stock Threshold:** {part.low_stock_threshold}")
                    st.write(f"**Part ID:** {part.id}")
                with col2:
                    if part.qr_code_url:
                        st.image(part.qr_code_url, caption="Part QR Code", width=150)
                    else:
                        st.write("No QR Code")

with tab2:
    # --- Part Creation Form ---
    with st.expander("Add New Part", expanded=True):
        with st.form("new_part_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Part Name")
                part_number = st.text_input("Part Number / SKU")
                category = st.text_input("Category", "Uncategorized")
            with col2:
                stock_quantity = st.number_input("Initial Stock Quantity", min_value=0, step=1)
                low_stock_threshold = st.number_input("Low Stock Threshold", min_value=0, step=1, value=5)
            with col3:
                location = st.text_input("Storage Location")
                supplier = st.text_input("Supplier (Optional)")

            submitted = st.form_submit_button("Add Part")
            if submitted:
                if not name or not part_number:
                    st.warning("Part Name and Part Number are required.")
                else:
                    try:
                        inventory.add_part(
                            name=name, part_number=part_number, stock_quantity=stock_quantity,
                            location=location, supplier=supplier, category=category, 
                            low_stock_threshold=low_stock_threshold
                        )
                        st.success(f"Successfully added part: {name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add part: {e}")

    # --- Part Update and Stock Adjustment ---
    if all_parts:
        st.header("Update Part or Adjust Stock")
        part_to_manage_id = st.selectbox(
            "Select Part to Manage", 
            options=[p.id for p in all_parts], 
            format_func=lambda x: f"{inventory.get_part_by_id(x).name} ({inventory.get_part_by_id(x).part_number})"
        )
        selected_part = inventory.get_part_by_id(part_to_manage_id)

        if selected_part:
            # --- Stock Adjustment ---
            st.subheader(f"Adjust Stock for {selected_part.name}")
            with st.form(f"adjust_stock_{selected_part.id}"):
                adjustment = st.number_input("Adjust Quantity (use negative to subtract)", step=1, value=0)
                submitted_adj = st.form_submit_button("Adjust Stock")
                if submitted_adj and adjustment != 0:
                    try:
                        inventory.adjust_stock(selected_part.id, adjustment, user['username'])
                        st.success(f"Stock for {selected_part.name} adjusted by {adjustment}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to adjust stock: {e}")

            # --- Update Details ---
            st.subheader(f"Edit Details for {selected_part.name}")
            with st.form(f"update_part_{selected_part.id}"):
                updates = {}
                updates['name'] = st.text_input("Name", value=selected_part.name)
                updates['category'] = st.text_input("Category", value=selected_part.category)
                updates['location'] = st.text_input("Location", value=selected_part.location)
                updates['supplier'] = st.text_input("Supplier", value=selected_part.supplier)
                updates['low_stock_threshold'] = st.number_input("Low Stock Threshold", min_value=0, step=1, value=selected_part.low_stock_threshold)
                
                submitted_update = st.form_submit_button("Save Changes")
                if submitted_update:
                    try:
                        inventory.update_part(selected_part.id, updates)
                        st.success(f"Details for {selected_part.name} updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update part: {e}")
