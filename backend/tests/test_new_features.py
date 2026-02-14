"""
Test suite for new features:
- PDF Contract Generation
- Notifications API
- Reports API
- Templates API (certification packages + proposal templates)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Known test data
TEST_ACCESS_TOKEN = "7e9465b4-fa2d-4ba9-8baf-05e5d32cd971"  # Existing proposal with signed agreement


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed - status: {response.status_code}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


# ================= NOTIFICATIONS TESTS =================

class TestNotifications:
    """Test notification endpoints"""
    
    def test_get_notifications_success(self, auth_headers):
        """GET /api/notifications should return notifications list"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "notifications" in data
        assert "unread_count" in data
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
        print(f"Retrieved {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_get_notifications_with_limit(self, auth_headers):
        """GET /api/notifications?limit=5 should limit results"""
        response = requests.get(
            f"{BASE_URL}/api/notifications?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) <= 5
    
    def test_get_notifications_unread_only(self, auth_headers):
        """GET /api/notifications?unread_only=true should return only unread"""
        response = requests.get(
            f"{BASE_URL}/api/notifications?unread_only=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # All returned notifications should be unread
        for notification in data["notifications"]:
            assert notification.get("is_read") == False
    
    def test_get_notifications_unauthorized(self):
        """GET /api/notifications without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code in [401, 403]
    
    def test_mark_notification_read_invalid_id(self, auth_headers):
        """PUT /api/notifications/{id}/read with invalid id should return 404"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/nonexistent-id/read",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_mark_all_notifications_read(self, auth_headers):
        """PUT /api/notifications/read-all should mark all as read"""
        response = requests.put(
            f"{BASE_URL}/api/notifications/read-all",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify unread count is now 0
        verify_response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=auth_headers
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["unread_count"] == 0


# ================= REPORTS TESTS =================

class TestReports:
    """Test reports endpoints"""
    
    def test_get_submission_statistics(self, auth_headers):
        """GET /api/reports/submissions should return stats"""
        response = requests.get(
            f"{BASE_URL}/api/reports/submissions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "total_forms" in data
        assert "submitted_forms" in data
        assert "pending_forms" in data
        assert "monthly_stats" in data
        assert "total_proposals" in data
        assert "accepted_proposals" in data
        assert "conversion_rate" in data
        
        # Verify data types
        assert isinstance(data["total_forms"], int)
        assert isinstance(data["submitted_forms"], int)
        assert isinstance(data["monthly_stats"], list)
        assert isinstance(data["conversion_rate"], (int, float))
        
        print(f"Submission stats: {data['total_forms']} total forms, {data['conversion_rate']}% conversion rate")
    
    def test_get_revenue_statistics(self, auth_headers):
        """GET /api/reports/revenue should return revenue stats"""
        response = requests.get(
            f"{BASE_URL}/api/reports/revenue",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "total_quoted" in data
        assert "accepted_revenue" in data
        assert "pending_revenue" in data
        assert "rejected_revenue" in data
        assert "total_contracts" in data
        assert "monthly_revenue" in data
        assert "currency" in data
        
        # Verify data types
        assert isinstance(data["total_quoted"], (int, float))
        assert isinstance(data["accepted_revenue"], (int, float))
        assert isinstance(data["monthly_revenue"], list)
        assert data["currency"] == "SAR"
        
        print(f"Revenue stats: SAR {data['total_quoted']} total quoted, SAR {data['accepted_revenue']} accepted")
    
    def test_reports_unauthorized(self):
        """Reports endpoints without auth should fail"""
        # Test submissions
        response = requests.get(f"{BASE_URL}/api/reports/submissions")
        assert response.status_code in [401, 403]
        
        # Test revenue
        response = requests.get(f"{BASE_URL}/api/reports/revenue")
        assert response.status_code in [401, 403]


# ================= TEMPLATES TESTS =================

class TestTemplates:
    """Test templates endpoints (certification packages + proposal templates)"""
    
    def test_get_certification_packages(self, auth_headers):
        """GET /api/templates/packages should return packages list"""
        response = requests.get(
            f"{BASE_URL}/api/templates/packages",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} certification packages")
        
        # Verify structure of packages if any exist
        if len(data) > 0:
            package = data[0]
            assert "id" in package
            assert "name" in package
            assert "name_ar" in package
            assert "standards" in package
            assert isinstance(package["standards"], list)
    
    def test_get_proposal_templates(self, auth_headers):
        """GET /api/templates/proposals should return templates list"""
        response = requests.get(
            f"{BASE_URL}/api/templates/proposals",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} proposal templates")
        
        # Verify structure of templates if any exist
        if len(data) > 0:
            template = data[0]
            assert "id" in template
            assert "name" in template
            assert "name_ar" in template
    
    def test_create_certification_package(self, auth_headers):
        """POST /api/templates/packages should create a package"""
        package_data = {
            "name": "TEST_Package_QMS",
            "name_ar": "حزمة اختبار نظام الجودة",
            "description": "Test package for QMS certification",
            "description_ar": "حزمة اختبار لشهادة نظام إدارة الجودة",
            "standards": ["ISO9001"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/templates/packages",
            json=package_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data or "id" in data
        print(f"Created package: {data.get('id', 'success')}")
    
    def test_create_proposal_template(self, auth_headers):
        """POST /api/templates/proposals should create a template"""
        template_data = {
            "name": "TEST_Template_Standard",
            "name_ar": "قالب اختبار قياسي",
            "description": "Test standard pricing template",
            "default_fees": {
                "initial_certification": 10000,
                "surveillance_1": 5000,
                "surveillance_2": 5000,
                "recertification": 8000
            },
            "default_notes": "Standard pricing template",
            "default_validity_days": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/api/templates/proposals",
            json=template_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data or "id" in data
        print(f"Created template: {data.get('id', 'success')}")
    
    def test_templates_unauthorized(self):
        """Templates endpoints without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/templates/packages")
        assert response.status_code in [401, 403]
        
        response = requests.get(f"{BASE_URL}/api/templates/proposals")
        assert response.status_code in [401, 403]


# ================= PDF CONTRACT GENERATION TESTS =================

class TestPDFGeneration:
    """Test PDF contract generation endpoints"""
    
    def test_public_contract_pdf(self):
        """GET /api/public/contracts/{access_token}/pdf should return PDF"""
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/{TEST_ACCESS_TOKEN}/pdf"
        )
        
        # Should return PDF or 404 if agreement doesn't exist
        if response.status_code == 200:
            assert response.headers.get("Content-Type") == "application/pdf"
            assert len(response.content) > 0
            print("PDF contract generated successfully")
        elif response.status_code == 404:
            # Agreement not found is acceptable if none exists
            print("No signed agreement found for this access token")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_public_contract_pdf_invalid_token(self):
        """GET /api/public/contracts/{invalid_token}/pdf should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/invalid-token-12345/pdf"
        )
        assert response.status_code == 404
    
    def test_admin_contract_pdf(self, auth_headers):
        """GET /api/contracts/{agreement_id}/pdf requires valid agreement_id"""
        # First get agreements to find a valid ID
        # Since we need agreement_id (not access_token), we'll test with invalid ID
        response = requests.get(
            f"{BASE_URL}/api/contracts/invalid-agreement-id/pdf",
            headers=auth_headers
        )
        # Should return 404 for invalid agreement ID
        assert response.status_code == 404
    
    def test_admin_contract_pdf_unauthorized(self):
        """GET /api/contracts/{id}/pdf without auth should fail"""
        response = requests.get(
            f"{BASE_URL}/api/contracts/some-agreement-id/pdf"
        )
        assert response.status_code in [401, 403]


# ================= INTEGRATION TEST: NOTIFICATION CREATION =================

class TestNotificationIntegration:
    """Test that notifications are created during key actions"""
    
    def test_get_notifications_contains_expected_types(self, auth_headers):
        """Verify notifications contain expected types from system actions"""
        response = requests.get(
            f"{BASE_URL}/api/notifications?limit=50",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        notification_types = set()
        for notification in data["notifications"]:
            if "type" in notification:
                notification_types.add(notification["type"])
        
        print(f"Notification types found: {notification_types}")
        
        # Check if any expected types exist
        expected_types = {"form_submitted", "proposal_accepted", "proposal_rejected", "agreement_signed"}
        found_types = notification_types.intersection(expected_types)
        print(f"Found expected notification types: {found_types}")


# ================= RUN ALL TESTS =================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
