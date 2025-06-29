import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# To access the backend, we need to add the project root to the Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ChatterFix.backend import parts as parts_backend

st.set_page_config(page_title="Parts Management", layout="wide")

# --- Navigation ---

col1, col2 = st.columns([1,1])
with col1:
    if st.button("⬅️ Back to ChatterFix Dashboard"):
        switch_page("6_ChatterFix")

st.title("🔩 Parts Management")

# --- Part Creation Form ---
st.header("Create New Part")
with st.form("new_part_form", clear_on_submit=True):
    name = st.text_input("Part Name")
    part_number = st.text_input("Part Number")
    stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
    location = st.text_input("Location")
    supplier = st.text_input("Supplier (Optional)")
    
    submitted = st.form_submit_button("Create Part")
    if submitted:
        if not all([name, part_number, location]):
            st.error("Please fill out all required fields.")
        else:
            part_id = parts_backend.create_part(
                name=name,
                part_number=part_number,
                stock_quantity=stock_quantity,
                location=location,
                supplier=supplier,
            )
            st.success(f"Part created with ID: {part_id}")

# --- Part List ---
st.header("All Parts")
all_parts = parts_backend.get_all_parts()

if not all_parts:
    st.info("No parts found.")
else:
    for part in all_parts:
        with st.expander(f"{part.name} ({part.part_number}) - Stock: {part.stock_quantity}"):
            st.write(f"**ID:** {part.id}")
            st.write(f"**Location:** {part.location}")
            st.write(f"**Supplier:** {part.supplier}")

            quantity_change = st.number_input("Update Stock", step=1, key=f"quantity_{part.id}")
            if st.button("Update Stock", key=f"update_{part.id}"):
                parts_backend.update_part_stock(part.id, quantity_change, "admin") # Assuming admin user for now
                st.success("Stock updated!")
                st.experimental_rerun()
