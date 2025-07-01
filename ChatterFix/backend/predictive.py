"""
ChatterFix Backend Predictive Maintenance Logic
This file contains the core business logic for forecasting maintenance events.
"""

import pandas as pd
from prophet import Prophet
from . import work_orders, models, assets
from datetime import datetime, timedelta


def get_maintenance_forecast(asset_id: str, periods: int = 365) -> pd.DataFrame | None:
    """
    Generates a maintenance forecast for a specific asset.

    Args:
        asset_id: The ID of the asset to forecast.
        periods: The number of days into the future to forecast.

    Returns:
        A pandas DataFrame containing the forecast, or None if there is not enough data.
    """
    print(f"🔍 Generating forecast for asset: {asset_id}")
    all_wos = work_orders.get_all_work_orders()

    # Filter for completed work orders for the specific asset
    asset_maintenance_history = [
        wo for wo in all_wos 
        if wo.equipment_id == asset_id and wo.status == 'completed'
    ]

    # Prophet requires at least two data points to make a forecast
    if len(asset_maintenance_history) < 2:
        print(f"⚠️ Not enough maintenance history for asset {asset_id} to generate a forecast.")
        return None

    # Prepare the DataFrame for Prophet
    # It requires two columns: 'ds' (datestamp) and 'y' (numeric value)
    df = pd.DataFrame(
        {'ds': [wo.created_at for wo in asset_maintenance_history], 'y': 1}
    )
    # Ensure the 'ds' column is datetime
    df['ds'] = pd.to_datetime(df['ds'])

    try:
        # Initialize and fit the Prophet model
        model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
        # We can add custom seasonalities if we find patterns, e.g., quarterly maintenance
        model.fit(df)

        # Create a future dataframe to predict on
        future = model.make_future_dataframe(periods=periods)

        # Generate the forecast
        forecast = model.predict(future)

        print(f"✅ Successfully generated forecast for asset: {asset_id}")
        return forecast

    except Exception as e:
        print(f"❌ Error during Prophet forecasting for asset {asset_id}: {e}")
        return None

def generate_suggested_work_orders(prediction_window_days: int = 14) -> list[str]:
    """
    Analyzes all assets and automatically creates 'suggested' work orders
    for assets with a high probability of needing maintenance soon.

    Args:
        prediction_window_days: How many days in the future to look for predicted events.

    Returns:
        A list of IDs of the newly created suggested work orders.
    """
    print("🤖 Starting autonomous work order suggestion process...")
    all_assets_list = assets.get_all_assets()
    all_wos = work_orders.get_all_work_orders()
    newly_suggested_wos = []

    if not all_assets_list:
        print("No assets found to analyze.")
        return []

    for asset in all_assets_list:
        # Check if there's already an open or suggested work order for this asset
        has_existing_suggestion = any(
            wo.equipment_id == asset.id and wo.status in ['suggested', 'open', 'in_progress']
            for wo in all_wos
        )
        if has_existing_suggestion:
            print(f"⏩ Skipping asset {asset.name} ({asset.id}) as it already has an active or suggested work order.")
            continue

        # Generate the forecast
        forecast = get_maintenance_forecast(asset.id)

        if forecast is not None:
            # Find the first predicted event within our window
            future_df = forecast[forecast['ds'] > datetime.now()] 
            future_df = future_df[future_df['ds'] <= datetime.now() + timedelta(days=prediction_window_days)]

            if not future_df.empty:
                predicted_date = future_df.iloc[0]['ds'].strftime('%Y-%m-%d')
                print(f"🔥 High-probability event found for asset {asset.name} around {predicted_date}.")

                # Create the suggested work order
                title = f"AI Suggestion: Proactive Maintenance for {asset.name}"
                description = (
                    f"The predictive maintenance model forecasts a high probability of a "
                    f"required maintenance event for asset '{asset.name}' (ID: {asset.id}) "
                    f"around {predicted_date}. It is recommended to schedule a proactive inspection."
                )
                
                try:
                    new_wo_id = work_orders.create_work_order(
                        title=title,
                        description=description,
                        priority='medium', # Suggestions can be medium priority
                        equipment_id=asset.id,
                        status='suggested' # Set the new status
                    )
                    newly_suggested_wos.append(new_wo_id)
                    print(f"✅ Created suggested work order {new_wo_id} for asset {asset.id}")

                except Exception as e:
                    print(f"❌ Failed to create suggested work order for asset {asset.id}: {e}")

    print(f"🤖 Autonomous suggestion process finished. Created {len(newly_suggested_wos)} new work orders.")
    return newly_suggested_wos
