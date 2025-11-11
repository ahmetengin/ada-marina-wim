"""
Unit tests for compliance service
"""

import pytest
from app.services.compliance import ComplianceService
from app.services.wim_regulations import WIMRegulations


@pytest.mark.unit
class TestWIMRegulations:
    """Test WIM regulation definitions"""

    def test_regulation_categories(self):
        """Test that all regulation categories exist"""
        regs = WIMRegulations()
        assert len(regs.categories) == 6
        assert "A" in regs.categories
        assert "B" in regs.categories
        assert "C" in regs.categories
        assert "D" in regs.categories
        assert "E" in regs.categories
        assert "F" in regs.categories

    def test_get_regulation_by_article(self):
        """Test getting specific regulation by article number"""
        regs = WIMRegulations()
        reg = regs.get_regulation("E.2.1")
        assert reg is not None
        assert reg["article"] == "E.2.1"
        assert "insurance" in reg["title"].lower()

    def test_hot_work_permit_regulation(self):
        """Test hot work permit regulation (Article E.5.5)"""
        regs = WIMRegulations()
        reg = regs.get_regulation("E.5.5")
        assert reg is not None
        assert reg["article"] == "E.5.5"
        assert "hot work" in reg["title"].lower() or "sıcak iş" in reg["description"].lower()

    def test_search_regulations(self):
        """Test searching regulations"""
        regs = WIMRegulations()
        results = regs.search_regulations("insurance")
        assert len(results) > 0
        assert any("E.2.1" == r["article"] for r in results)

    def test_regulation_count(self):
        """Test that we have at least 50 regulations defined"""
        regs = WIMRegulations()
        all_regs = []
        for category in regs.categories.values():
            all_regs.extend(category)
        assert len(all_regs) >= 50  # We have at least 50 of the 176 articles


@pytest.mark.unit
class TestComplianceService:
    """Test compliance service"""

    def test_insurance_check_valid(self):
        """Test insurance compliance check with valid insurance"""
        from datetime import datetime, timedelta
        vessel = {
            "insurance_company": "Test Insurance",
            "insurance_policy_number": "POL-12345",
            "insurance_expiry_date": datetime.now() + timedelta(days=60)
        }
        result = ComplianceService.check_insurance_compliance(vessel)
        assert result["compliant"] is True
        assert result["status"] == "valid"

    def test_insurance_check_expiring_soon(self):
        """Test insurance compliance check with expiring insurance"""
        from datetime import datetime, timedelta
        vessel = {
            "insurance_company": "Test Insurance",
            "insurance_policy_number": "POL-12345",
            "insurance_expiry_date": datetime.now() + timedelta(days=15)
        }
        result = ComplianceService.check_insurance_compliance(vessel)
        assert result["compliant"] is True
        assert result["status"] == "expiring_soon"
        assert "warning" in result

    def test_insurance_check_expired(self):
        """Test insurance compliance check with expired insurance"""
        from datetime import datetime, timedelta
        vessel = {
            "insurance_company": "Test Insurance",
            "insurance_policy_number": "POL-12345",
            "insurance_expiry_date": datetime.now() - timedelta(days=1)
        }
        result = ComplianceService.check_insurance_compliance(vessel)
        assert result["compliant"] is False
        assert result["status"] == "expired"

    def test_insurance_check_missing(self):
        """Test insurance compliance check with missing insurance"""
        vessel = {
            "insurance_company": None,
            "insurance_policy_number": None,
            "insurance_expiry_date": None
        }
        result = ComplianceService.check_insurance_compliance(vessel)
        assert result["compliant"] is False
        assert result["status"] == "missing"

    def test_berth_size_compliance(self):
        """Test berth size compliance check"""
        berth = {
            "length_meters": 15.0,
            "width_meters": 5.0,
            "depth_meters": 3.0
        }
        vessel = {
            "length_meters": 14.0,
            "width_meters": 4.5,
            "draft_meters": 2.5
        }
        result = ComplianceService.check_berth_size_compliance(berth, vessel)
        assert result["compliant"] is True

    def test_berth_size_non_compliance(self):
        """Test berth size non-compliance"""
        berth = {
            "length_meters": 12.0,
            "width_meters": 4.0,
            "depth_meters": 2.0
        }
        vessel = {
            "length_meters": 14.0,
            "width_meters": 4.5,
            "draft_meters": 2.5
        }
        result = ComplianceService.check_berth_size_compliance(berth, vessel)
        assert result["compliant"] is False
