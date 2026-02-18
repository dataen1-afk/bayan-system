"""
Dashboard Analytics API Tests - Testing dashboard widgets endpoints
Tests: Certificate Expiration Widget, Revenue Target, Auditor Workload, Today's Activity, Quick Actions
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDashboardStatsAPI:
    """Tests for /api/dashboard/stats endpoint - Main dashboard analytics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_dashboard_stats_returns_200(self):
        """Test that dashboard stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Dashboard stats endpoint returns 200")
    
    def test_dashboard_stats_has_certificates_section(self):
        """Test that response includes certificates statistics for expiration widget"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        data = response.json()
        
        assert "certificates" in data, "Missing 'certificates' section"
        certs = data["certificates"]
        
        # Check required fields for Certificate Expiration Widget
        assert "total" in certs, "Missing certificates.total"
        assert "active" in certs, "Missing certificates.active"
        assert "expiring_30_days" in certs, "Missing certificates.expiring_30_days"
        assert "expiring_60_days" in certs, "Missing certificates.expiring_60_days"
        assert "expiring_90_days" in certs, "Missing certificates.expiring_90_days"
        assert "expiring_count" in certs, "Missing certificates.expiring_count"
        
        # Verify expiring_count structure
        exp_count = certs["expiring_count"]
        assert "30_days" in exp_count, "Missing expiring_count.30_days"
        assert "60_days" in exp_count, "Missing expiring_count.60_days"
        assert "90_days" in exp_count, "Missing expiring_count.90_days"
        
        # Verify data types
        assert isinstance(certs["total"], int), "certificates.total should be int"
        assert isinstance(certs["active"], int), "certificates.active should be int"
        assert isinstance(certs["expiring_30_days"], list), "expiring_30_days should be list"
        assert isinstance(certs["expiring_60_days"], list), "expiring_60_days should be list"
        assert isinstance(certs["expiring_90_days"], list), "expiring_90_days should be list"
        
        print(f"✓ Certificate Expiration data: total={certs['total']}, active={certs['active']}")
        print(f"  Expiring: 30d={exp_count['30_days']}, 60d={exp_count['60_days']}, 90d={exp_count['90_days']}")
    
    def test_dashboard_stats_has_revenue_section(self):
        """Test that response includes revenue statistics for Revenue Target Progress Widget"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        data = response.json()
        
        assert "revenue" in data, "Missing 'revenue' section"
        revenue = data["revenue"]
        
        # Check required fields for Revenue Target Progress Widget
        assert "total" in revenue, "Missing revenue.total"
        assert "monthly" in revenue, "Missing revenue.monthly"
        assert "monthly_target" in revenue, "Missing revenue.monthly_target"
        assert "currency" in revenue, "Missing revenue.currency"
        
        # Verify currency is SAR
        assert revenue["currency"] == "SAR", f"Expected currency SAR, got {revenue['currency']}"
        
        # Verify data types
        assert isinstance(revenue["total"], (int, float)), "revenue.total should be numeric"
        assert isinstance(revenue["monthly"], (int, float)), "revenue.monthly should be numeric"
        assert isinstance(revenue["monthly_target"], (int, float)), "revenue.monthly_target should be numeric"
        
        # Calculate progress percentage
        if revenue["monthly_target"] > 0:
            progress = (revenue["monthly"] / revenue["monthly_target"]) * 100
            print(f"✓ Revenue data: monthly={revenue['monthly']} SAR, target={revenue['monthly_target']} SAR ({progress:.1f}%)")
        else:
            print(f"✓ Revenue data: monthly={revenue['monthly']} SAR, target={revenue['monthly_target']} SAR")
    
    def test_dashboard_stats_has_auditor_workload(self):
        """Test that response includes auditor workload for Auditor Workload Chart"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        data = response.json()
        
        assert "auditor_workload" in data, "Missing 'auditor_workload' section"
        workload = data["auditor_workload"]
        
        # Should be a list
        assert isinstance(workload, list), "auditor_workload should be a list"
        
        # If there are auditors, check structure
        if len(workload) > 0:
            auditor = workload[0]
            assert "id" in auditor, "Missing auditor.id"
            assert "name" in auditor, "Missing auditor.name"
            assert "name_ar" in auditor, "Missing auditor.name_ar"
            assert "total_tasks" in auditor, "Missing auditor.total_tasks"
            assert "job_orders" in auditor, "Missing auditor.job_orders"
            assert "stage1_audits" in auditor, "Missing auditor.stage1_audits"
            assert "stage2_audits" in auditor, "Missing auditor.stage2_audits"
            
            print(f"✓ Auditor Workload: {len(workload)} auditors found")
            for a in workload[:3]:  # Print top 3
                print(f"  - {a['name']}: {a['total_tasks']} tasks")
        else:
            print("✓ Auditor Workload: No auditors found (empty list)")
    
    def test_dashboard_stats_has_today_activity(self):
        """Test that response includes today's activity for Today's Activity Widget"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        data = response.json()
        
        assert "today_activity" in data, "Missing 'today_activity' section"
        activity = data["today_activity"]
        
        # Check required fields for Today's Activity Widget
        assert "notifications" in activity, "Missing today_activity.notifications"
        assert "new_forms" in activity, "Missing today_activity.new_forms"
        assert "new_proposals" in activity, "Missing today_activity.new_proposals"
        
        # Verify data types
        assert isinstance(activity["notifications"], list), "notifications should be a list"
        assert isinstance(activity["new_forms"], int), "new_forms should be int"
        assert isinstance(activity["new_proposals"], int), "new_proposals should be int"
        
        print(f"✓ Today's Activity: {activity['new_forms']} new forms, {activity['new_proposals']} new proposals")
        print(f"  {len(activity['notifications'])} notifications")
    
    def test_dashboard_stats_has_forms_and_proposals(self):
        """Test that response includes forms and proposals stats for Quick Actions"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        data = response.json()
        
        # Forms section
        assert "forms" in data, "Missing 'forms' section"
        forms = data["forms"]
        assert "total" in forms, "Missing forms.total"
        assert "pending" in forms, "Missing forms.pending"
        assert "submitted" in forms, "Missing forms.submitted"
        
        # Proposals section
        assert "proposals" in data, "Missing 'proposals' section"
        proposals = data["proposals"]
        assert "total" in proposals, "Missing proposals.total"
        assert "pending" in proposals, "Missing proposals.pending"
        assert "signed" in proposals, "Missing proposals.signed"
        
        # Approvals section
        assert "approvals" in data, "Missing 'approvals' section"
        approvals = data["approvals"]
        assert "pending" in approvals, "Missing approvals.pending"
        
        print(f"✓ Forms: total={forms['total']}, pending={forms['pending']}, submitted={forms['submitted']}")
        print(f"✓ Proposals: total={proposals['total']}, pending={proposals['pending']}, signed={proposals['signed']}")
        print(f"✓ Approvals: pending={approvals['pending']}")


class TestQuickActionsAPI:
    """Tests for /api/dashboard/quick-actions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_quick_actions_returns_200(self):
        """Test that quick actions endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/quick-actions", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Quick actions endpoint returns 200")
    
    def test_quick_actions_has_required_counts(self):
        """Test that quick actions returns all required counts"""
        response = requests.get(f"{BASE_URL}/api/dashboard/quick-actions", headers=self.headers)
        data = response.json()
        
        assert "pending_forms" in data, "Missing pending_forms"
        assert "pending_approvals" in data, "Missing pending_approvals"
        assert "pending_reviews" in data, "Missing pending_reviews"
        
        # Verify data types
        assert isinstance(data["pending_forms"], int), "pending_forms should be int"
        assert isinstance(data["pending_approvals"], int), "pending_approvals should be int"
        assert isinstance(data["pending_reviews"], int), "pending_reviews should be int"
        
        print(f"✓ Quick Actions: pending_forms={data['pending_forms']}, pending_approvals={data['pending_approvals']}, pending_reviews={data['pending_reviews']}")


class TestDashboardUnauthorized:
    """Test unauthorized access to dashboard endpoints"""
    
    def test_stats_requires_auth(self):
        """Test that stats endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Dashboard stats requires authentication")
    
    def test_quick_actions_requires_auth(self):
        """Test that quick actions endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/quick-actions")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Quick actions requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
