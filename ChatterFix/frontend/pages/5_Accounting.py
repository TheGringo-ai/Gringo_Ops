import streamlit as st
import pandas as pd
from backend import accounting, models
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Accounting & Financials", allowed_roles=['manager'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

# --- Page Title and Header ---
st.title("💰 Accounting & Financials")
st.markdown("""
Track costs, and manage financial records for all maintenance operations.
""")

# --- Transaction Creation Form ---
st.header("Log New Transaction")
with st.form("new_transaction_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        transaction_type = st.selectbox("Transaction Type", ["purchase", "sale", "maintenance", "other"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    with col2:
        description = st.text_area("Description", help="A detailed description of the transaction.")
    with col3:
        related_to_id = st.text_input("Related ID (Optional)", help="e.g., Asset ID, Work Order ID, Part ID.")

    submitted = st.form_submit_button("Log Transaction")
    if submitted:
        if not description or amount <= 0:
            st.warning("Please provide a valid Description and Amount.")
        else:
            try:
                transaction_id = accounting.create_transaction(
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    related_to_id=related_to_id
                )
                st.success(f"Successfully logged transaction: {transaction_id}")
            except Exception as e:
                st.error(f"Failed to log transaction: {e}")

# --- Transaction Display ---
st.header("Transaction History")

try:
    all_transactions = accounting.get_all_transactions()

    if not all_transactions:
        st.info("No transactions found. Log one above!")
    else:
        # Convert list of dataclasses to list of dicts for DataFrame
        transaction_data = [t.__dict__ for t in all_transactions]
        df = pd.DataFrame(transaction_data)

        # Reorder and select columns for display
        display_columns = [
            'id', 'transaction_date', 'transaction_type', 'amount',
            'description', 'related_to_id'
        ]
        df = df[display_columns]

        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load transactions: {e}")
