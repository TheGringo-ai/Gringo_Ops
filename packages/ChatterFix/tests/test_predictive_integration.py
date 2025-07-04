"""
Integration Tests for Predictive Maintenance
"""
import pytest
from backend import predictive, assets, work_orders
from datetime import datetime, timedelta

@pytest.mark.integration
class TestPredictiveIntegration:
    def test_get_maintenance_forecast_not_enough_data(self):
        # Should return None if not enough data
        asset_id = "nonexistent_asset"
        forecast = predictive.get_maintenance_forecast(asset_id)
        assert forecast is None

    def test_generate_suggested_work_orders(self, firestore_client):
        # Setup: create an asset and two completed work orders
        assets.database.db_client = firestore_client
        work_orders.database.db_client = firestore_client
        asset_id = assets.create_asset(
            name="Predictive Asset",
            asset_type="TestType",
            location="TestLoc",
            purchase_date="2024-01-01",
            purchase_price=1000.0,
            serial_number="PRED-001"
        )
        # Create two completed work orders for this asset
        for i in range(2):
            work_orders.create_work_order(
                title=f"WO {i}",
                description="Completed for predictive test",
                priority="medium",
                equipment_id=asset_id,
                status="completed"
            )
        # Should now be able to generate a forecast and a suggested WO
        suggested = predictive.generate_suggested_work_orders(prediction_window_days=365)
        assert isinstance(suggested, list)
