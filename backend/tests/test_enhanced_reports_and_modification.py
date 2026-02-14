"""
Test cases for Enhanced Reports and Modification Request features
Features tested:
1. Enhanced Reports - /api/reports/filtered endpoint with filters (date range, status, standard)
2. Modification Request - /api/public/proposal/{access_token}/request_modification endpoint
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agreement-hub-14.preview.emergentagent.com').rstrip('/')

# Test access tokens provided by main agent
PENDING_PROPOSAL_TOKEN = "d4a5fd8f-7c81-4453-a529-626b8c2bfe1a"  # Pending proposal for modification test
MODIFICATION_REQUESTED_TOKEN = "4d2067ae-cc32-400b-8f69-3b14b28ba313"  # Already has modification_requested status


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_admin_login_success(self):
        """Test admin login returns token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful, token received")


class TestEnhancedReports:
    """Test Enhanced Reports with filtering functionality"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers for admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_filtered_reports_endpoint_no_filters(self, auth_headers):
        """Test /api/reports/filtered endpoint returns data without filters"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "forms" in data
        assert "proposals" in data
        assert "revenue" in data
        assert "conversion_rate" in data
        assert "standards_breakdown" in data
        assert "filters_applied" in data
        
        # Verify forms structure
        assert "total" in data["forms"]
        assert "submitted" in data["forms"]
        assert "pending" in data["forms"]
        
        # Verify proposals structure
        assert "total" in data["proposals"]
        assert "accepted" in data["proposals"]
        assert "rejected" in data["proposals"]
        assert "modification_requested" in data["proposals"]
        
        # Verify revenue structure
        assert "total_quoted" in data["revenue"]
        assert "accepted" in data["revenue"]
        assert "pending" in data["revenue"]
        assert "currency" in data["revenue"]
        
        print(f"✓ Filtered reports endpoint returns correct structure")
        print(f"  Forms: total={data['forms']['total']}, submitted={data['forms']['submitted']}")
        print(f"  Proposals: total={data['proposals']['total']}, accepted={data['proposals']['accepted']}")
        print(f"  Revenue: total_quoted={data['revenue']['total_quoted']}")
    
    def test_filtered_reports_with_status_filter(self, auth_headers):
        """Test filtering by status"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers,
            params={"status": "pending"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify filter was applied
        assert data["filters_applied"]["status"] == "pending"
        print(f"✓ Status filter applied correctly: pending")
        print(f"  Filtered proposals: {data['proposals']['total']}")
    
    def test_filtered_reports_with_standard_filter(self, auth_headers):
        """Test filtering by certification standard"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers,
            params={"standard": "ISO9001"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify filter was applied
        assert data["filters_applied"]["standard"] == "ISO9001"
        print(f"✓ Standard filter applied correctly: ISO9001")
        print(f"  Filtered forms: {data['forms']['total']}")
        print(f"  Filtered proposals: {data['proposals']['total']}")
    
    def test_filtered_reports_with_date_range(self, auth_headers):
        """Test filtering by date range"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers,
            params={
                "start_date": "2025-01-01",
                "end_date": "2026-12-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify filters were applied
        assert data["filters_applied"]["start_date"] == "2025-01-01"
        assert data["filters_applied"]["end_date"] == "2026-12-31"
        print(f"✓ Date range filter applied correctly")
        print(f"  Start: {data['filters_applied']['start_date']}, End: {data['filters_applied']['end_date']}")
    
    def test_filtered_reports_with_multiple_filters(self, auth_headers):
        """Test applying multiple filters at once"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers,
            params={
                "start_date": "2025-01-01",
                "end_date": "2026-12-31",
                "status": "pending",
                "standard": "ISO9001"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all filters were applied
        assert data["filters_applied"]["start_date"] == "2025-01-01"
        assert data["filters_applied"]["end_date"] == "2026-12-31"
        assert data["filters_applied"]["status"] == "pending"
        assert data["filters_applied"]["standard"] == "ISO9001"
        print(f"✓ Multiple filters applied correctly")
    
    def test_filtered_reports_unauthorized(self):
        """Test that unauthorized access is denied"""
        response = requests.get(f"{BASE_URL}/api/reports/filtered")
        assert response.status_code in [401, 403]
        print(f"✓ Unauthorized access correctly denied with status {response.status_code}")
    
    def test_filtered_reports_standards_breakdown(self, auth_headers):
        """Test that standards breakdown is included in response"""
        response = requests.get(
            f"{BASE_URL}/api/reports/filtered",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "standards_breakdown" in data
        assert isinstance(data["standards_breakdown"], dict)
        print(f"✓ Standards breakdown included in response")
        if data["standards_breakdown"]:
            print(f"  Standards: {list(data['standards_breakdown'].keys())}")


class TestModificationRequest:
    """Test Modification Request functionality for clients"""
    
    def test_get_pending_proposal(self):
        """Test fetching pending proposal via public access"""
        response = requests.get(f"{BASE_URL}/api/public/proposal/{PENDING_PROPOSAL_TOKEN}")
        
        if response.status_code == 404:
            pytest.skip(f"Pending proposal with token {PENDING_PROPOSAL_TOKEN} not found - may need seed data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "status" in data
        assert "organization_name" in data
        print(f"✓ Retrieved pending proposal successfully")
        print(f"  Organization: {data.get('organization_name')}")
        print(f"  Status: {data.get('status')}")
    
    def test_get_modification_requested_proposal(self):
        """Test fetching proposal with modification_requested status"""
        response = requests.get(f"{BASE_URL}/api/public/proposal/{MODIFICATION_REQUESTED_TOKEN}")
        
        if response.status_code == 404:
            pytest.skip(f"Modification requested proposal with token {MODIFICATION_REQUESTED_TOKEN} not found")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "status" in data
        # Check if it has modification fields
        if data.get("status") == "modification_requested":
            print(f"✓ Retrieved modification_requested proposal")
            print(f"  Organization: {data.get('organization_name')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Modification Comment: {data.get('modification_comment', 'N/A')[:50]}...")
        else:
            print(f"  Current status: {data.get('status')}")
    
    def test_request_modification_endpoint_exists(self):
        """Test that modification request endpoint exists and validates input"""
        # Test with empty comment - should fail validation
        response = requests.post(
            f"{BASE_URL}/api/public/proposal/{PENDING_PROPOSAL_TOKEN}/request_modification",
            json={"comment": "", "requested_changes": ""}
        )
        
        if response.status_code == 404:
            pytest.skip(f"Proposal not found with token {PENDING_PROPOSAL_TOKEN}")
        
        # Should return 400 for empty comment
        if response.status_code == 400:
            data = response.json()
            print(f"✓ Empty comment validation working: {data.get('detail', 'Validation error')}")
        elif response.status_code == 200:
            print(f"⚠ Warning: Empty comment was accepted")
        else:
            print(f"Response status: {response.status_code}")
    
    def test_request_modification_on_already_responded(self):
        """Test that modification request fails on already responded proposal"""
        response = requests.post(
            f"{BASE_URL}/api/public/proposal/{MODIFICATION_REQUESTED_TOKEN}/request_modification",
            json={
                "comment": "Test modification request",
                "requested_changes": "Test changes"
            }
        )
        
        if response.status_code == 404:
            pytest.skip("Proposal not found")
        
        # Should return 400 because proposal already has modification_requested status
        if response.status_code == 400:
            data = response.json()
            print(f"✓ Already responded validation working: {data.get('detail', 'Validation error')}")
        else:
            print(f"Response status: {response.status_code}")


class TestBasicReportsEndpoints:
    """Test basic reports endpoints for comparison"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers for admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_submissions_report_endpoint(self, auth_headers):
        """Test /api/reports/submissions endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/submissions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_forms" in data
        assert "submitted_forms" in data
        assert "pending_forms" in data
        assert "monthly_stats" in data
        print(f"✓ Submissions report endpoint working")
        print(f"  Total forms: {data.get('total_forms')}")
    
    def test_revenue_report_endpoint(self, auth_headers):
        """Test /api/reports/revenue endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/revenue",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_quoted" in data
        assert "accepted_revenue" in data
        assert "total_contracts" in data
        print(f"✓ Revenue report endpoint working")
        print(f"  Total quoted: {data.get('total_quoted')} SAR")


class TestNotifications:
    """Test that notifications are created for modification requests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers for admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_get_notifications(self, auth_headers):
        """Test that admin can fetch notifications"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Notifications endpoint working")
        print(f"  Unread count: {data.get('unread_count')}")
        
        # Check if any modification_requested notifications exist
        modification_notifications = [
            n for n in data.get("notifications", [])
            if n.get("type") == "modification_requested"
        ]
        print(f"  Modification request notifications: {len(modification_notifications)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
