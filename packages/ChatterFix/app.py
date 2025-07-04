import streamlit as st
from pages import Work_Orders

st.set_page_config(page_title="ChatterFix", layout="wide")

# TODO: Add sidebar nav in the future
Work_Orders.render_work_orders_page()
