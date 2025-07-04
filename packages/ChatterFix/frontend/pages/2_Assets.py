import streamlit as st
import pandas as pd
from backend import assets, models
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Asset Management", allowed_roles=['manager', 'technician'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

# --- Page Title and Header ---
st.title("📦 Asset Management")
st.markdown("""
Add, view, and manage company assets.
""")

# --- Asset Creation Form ---
st.header("Add New Asset")
with st.form("new_asset_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Asset Name", help="The common name for the asset.")
        asset_type = st.text_input("Asset Type", help="e.g., Vehicle, HVAC Unit, Production Machine.")
        location = st.text_input("Location", help="Where the asset is physically located.")
    with col2:
        purchase_date = st.date_input("Purchase Date")
        purchase_price = st.number_input("Purchase Price", min_value=0.0, format="%.2f")
        serial_number = st.text_input("Serial Number")

    submitted = st.form_submit_button("Add Asset")
    if submitted:
        if not name or not asset_type or not location:
            st.warning("Please fill out Asset Name, Type, and Location.")
        else:
            try:
                asset_id = assets.create_asset(
                    name=name,
                    asset_type=asset_type,
                    location=location,
                    purchase_date=str(purchase_date), # Convert date to string for DB
                    purchase_price=purchase_price,
                    serial_number=serial_number
                )
                st.success(f"Successfully added asset: {asset_id}")
            except Exception as e:
                st.error(f"Failed to add asset: {e}")

# --- Asset Display ---
st.header("Current Assets")

try:
    all_assets = assets.get_all_assets()

    if not all_assets:
        st.info("No assets found. Add one above!")
    else:
        for asset in all_assets:
            with st.expander(f"{asset.name} - {asset.asset_type} (ID: {asset.id})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Location:** {asset.location}")
                    st.write(f"**Status:** {asset.status}")
                    st.write(f"**Serial Number:** {asset.serial_number}")
                    st.write(f"**Purchase Date:** {asset.purchase_date}")
                    st.write(f"**Purchase Price:** ${asset.purchase_price:,.2f}")
                with col2:
                    if asset.qr_code_url:
                        st.image(asset.qr_code_url, caption="Asset QR Code", width=150)
                    else:
                        st.write("No QR Code")

except Exception as e:
    st.error(f"Failed to load assets: {e}")
