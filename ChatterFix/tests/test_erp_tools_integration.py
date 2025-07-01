"""
Integration Tests for ERP Tools
"""
import pytest
from backend import erp_tools

@pytest.mark.integration
class TestERPToolsIntegration:
    def test_get_vendor_data(self):
        result = erp_tools.get_vendor_data("BR-54321")
        assert result["primary_vendor"] == "Global Bearings Inc."
        assert result["price"] == 15.99
        assert result["lead_time_days"] == 7
        # Test for unknown part
        assert erp_tools.get_vendor_data("UNKNOWN") == {}

    def test_create_financial_report(self):
        report = erp_tools.create_financial_report("cost_analysis", "2025-Q2")
        assert report["status"] == "generated"
        assert "report_id" in report

    def test_check_budget_limits(self):
        assert erp_tools.check_budget_limits("maintenance", 1000) is True
        assert erp_tools.check_budget_limits("sales", 1000) is False

    def test_generate_purchase_order(self):
        po = erp_tools.generate_purchase_order("BR-54321", 10, "Global Bearings Inc.")
        assert po["status"] == "submitted"
        assert "po_number" in po
