"""
Integration Tests for ChatterFix Asset Management using Firebase Emulator
"""
import os
import sys
import pytest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import assets, database, models

@pytest.mark.integration
class TestAssetIntegration:
    """
    Integration tests for the asset management functions, using a real Firestore backend (emulator).
    """
    created_asset_ids = []

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, firestore_client):
        """
        Fixture to set up the database client for each test and clean up created data afterwards.
        """
        database.db_client = firestore_client
        self.cleanup()
        yield
        self.cleanup()

    def cleanup(self):
        """Deletes all documents created during tests."""
        if not database.db_client:
            return
        for asset_id in self.created_asset_ids:
            try:
                print(f"Cleaning up asset: {asset_id}")
                database.db_client.collection("assets").document(asset_id).delete()
            except Exception as e:
                print(f"Error cleaning up asset {asset_id}: {e}")
        self.created_asset_ids = []

    def test_create_and_get_asset(self):
        """
        Tests creating a new asset and then retrieving it to verify its properties.
        """
        asset_id = assets.create_asset(
            name="Main Power Generator",
            asset_type="Generator",
            location="Basement Level 2",
            purchase_date="2023-01-15",
            purchase_price=50000.00,
            serial_number="MPG-98765",
            invoked_by_user="test_runner"
        )
        self.created_asset_ids.append(asset_id)

        retrieved_asset = assets.get_asset(asset_id)
        assert retrieved_asset is not None
        assert retrieved_asset.id == asset_id
        assert retrieved_asset.name == "Main Power Generator"
        assert retrieved_asset.status == "active"
        assert retrieved_asset.serial_number == "MPG-98765"
        assert retrieved_asset.qr_code_url is not None
        assert "data:image/png;base64," in retrieved_asset.qr_code_url

    def test_update_asset_status(self):
        """
        Tests updating an asset's status.
        """
        # 1. Create an asset
        asset_id = assets.create_asset(
            name="HVAC Unit 4",
            asset_type="HVAC",
            location="Rooftop",
            purchase_date="2022-05-20",
            purchase_price=15000.00,
            serial_number="HVAC-004",
            invoked_by_user="test_creator"
        )
        self.created_asset_ids.append(asset_id)

        # 2. Update status to 'maintenance'
        assets.update_asset_status(asset_id, "maintenance", user="test_updater")
        updated_asset = assets.get_asset(asset_id)
        assert updated_asset.status == "maintenance"

        # 3. Update status to 'decommissioned'
        assets.update_asset_status(asset_id, "decommissioned", user="test_updater")
        final_asset = assets.get_asset(asset_id)
        assert final_asset.status == "decommissioned"

    def test_get_all_assets(self):
        """
        Tests retrieving all assets.
        """
        # Create a few assets
        asset1_id = assets.create_asset("Asset 1", "Type A", "Loc 1", "2023-01-01", 100, "S1")
        asset2_id = assets.create_asset("Asset 2", "Type B", "Loc 2", "2023-02-01", 200, "S2")
        self.created_asset_ids.extend([asset1_id, asset2_id])

        all_assets = assets.get_all_assets()
        assert len(all_assets) >= 2
        # Verify that the created assets are in the retrieved list
        retrieved_ids = [asset.id for asset in all_assets]
        assert asset1_id in retrieved_ids
        assert asset2_id in retrieved_ids
