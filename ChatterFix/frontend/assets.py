import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from ..backend import assets as assets_backend

st.set_page_config(page_title="Asset Management", layout="wide")

# --- Navigation ---

col1, col2 = st.columns([1,1])
with col1:
    if st.button("⬅️ Back to Dashboard"):
        switch_page("dashboard")

st.title("🛠️ Asset Management")

# --- Asset Creation Form ---
st.header("Create New Asset")
with st.form("new_asset_form", clear_on_submit=True):
    name = st.text_input("Asset Name")
    asset_type = st.text_input("Asset Type")
    location = st.text_input("Location")
    purchase_date = st.date_input("Purchase Date")
    purchase_price = st.number_input("Purchase Price", min_value=0.0, format="%.2f")
    serial_number = st.text_input("Serial Number")
    
    submitted = st.form_submit_button("Create Asset")
    if submitted:
        if not all([name, asset_type, location, purchase_date, serial_number]):
            st.error("Please fill out all fields.")
        else:
            asset_id = assets_backend.create_asset(
                name=name,
                asset_type=asset_type,
                location=location,
                purchase_date=str(purchase_date),
                purchase_price=purchase_price,
                serial_number=serial_number,
            )
            st.success(f"Asset created with ID: {asset_id}")

# --- Asset List ---
st.header("All Assets")
all_assets = assets_backend.get_all_assets()

if not all_assets:
    st.info("No assets found.")
else:
    for asset in all_assets:
        with st.expander(f"{asset.name} ({asset.asset_type}) - {asset.location}"):
            st.write(f"**ID:** {asset.id}")
            st.write(f"**Serial Number:** {asset.serial_number}")
            st.write(f"**Purchase Date:** {asset.purchase_date}")
            st.write(f"**Purchase Price:** ${asset.purchase_price:,.2f}")
            st.write(f"**Status:** {asset.status}")

            new_status = st.selectbox(
                "Update Status",
                options=asset.__class__.__annotations__['status'].__args__,
                index=asset.__class__.__annotations__['status'].__args__.index(asset.status),
                key=f"status_{asset.id}"
            )
            if st.button("Update", key=f"update_{asset.id}"):
                assets_backend.update_asset_status(asset.id, new_status, "admin") # Assuming admin user for now
                st.success("Status updated!")
                st.experimental_rerun()
