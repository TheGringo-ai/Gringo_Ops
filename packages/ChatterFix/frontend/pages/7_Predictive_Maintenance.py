import streamlit as st
import pandas as pd
from backend import predictive, assets
from prophet import Prophet
from prophet.plot import plot_plotly
from frontend import auth_utils

# --- Authentication and Role-Based Access Control ---
user = auth_utils.enforce_auth(page_name="Predictive Maintenance", allowed_roles=['manager'])
# --- End Auth Check ---

st.set_page_config(layout="wide")

# --- Page Title and Header ---
st.title("🔮 Predictive Maintenance")
st.markdown("""
Forecast future maintenance needs for your assets based on their history.
""")

# --- Asset Selection ---
st.header("Select an Asset to Forecast")

try:
    all_assets = assets.get_all_assets()
    if not all_assets:
        st.warning("No assets found. Please add assets in the 'Assets' page first.")
    else:
        asset_options = {asset.name: asset.id for asset in all_assets}
        selected_asset_name = st.selectbox(
            "Choose an asset:",
            options=list(asset_options.keys())
        )

        if selected_asset_name:
            selected_asset_id = asset_options[selected_asset_name]
            st.info(f"Generating forecast for **{selected_asset_name}** (ID: `{selected_asset_id}`). This may take a moment...")

            # --- Forecasting Logic ---
            with st.spinner("Running Prophet model..."):
                # The function now returns the model and the forecast dataframe
                model, forecast_df = predictive.get_maintenance_forecast(selected_asset_id)

            if forecast_df is None or forecast_df.empty or model is None:
                st.error("Could not generate a forecast. This usually means there is not enough maintenance history (at least 2 completed work orders) for this asset.")
            else:
                st.header(f"Forecast for {selected_asset_name}")

                # --- Display Prophet Plot ---
                # The plot function requires the fitted model and the forecast dataframe
                fig = plot_plotly(model, forecast_df)
                st.plotly_chart(fig, use_container_width=True)

                # --- Display Next Predicted Event ---
                st.subheader("Next Predicted Maintenance Event")
                # The forecast includes the history. We want the first future prediction.
                future_df = forecast_df[forecast_df['ds'] > pd.to_datetime('today')]
                if not future_df.empty:
                    next_event = future_df.iloc[0]
                    st.metric(
                        label="Predicted Date",
                        value=next_event['ds'].strftime('%Y-%m-%d')
                    )
                    st.write(f"The model predicts the next maintenance event around this date. The blue shaded area in the chart represents the confidence interval.")
                else:
                    st.info("No future maintenance events were predicted within the forecast period.")

                # --- Display Raw Forecast Data ---
                with st.expander("View Raw Forecast Data"):
                    st.dataframe(forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
                        columns={
                            'ds': 'Date',
                            'yhat': 'Prediction',
                            'yhat_lower': 'Lower Confidence Bound',
                            'yhat_upper': 'Upper Confidence Bound'
                        }
                    ), use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.exception(e) # Provides a full traceback for debugging
