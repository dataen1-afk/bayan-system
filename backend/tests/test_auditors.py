"""
Auditor Management API Tests
Tests for CRUD operations on auditors and availability management
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

# Get BASE_URL from environment variable (production URL)
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Test auditor data
TEST_AUDITOR = {
    "employee_id": "TEST-001",
    "name": "TEST_John Smith",
    "name_ar": "جون سميث",
    "email": "test_john.smith@audit.com",
    "phone": "+966-11-1234567",
    "mobile": "+966-50-1234567",
    "specializations": ["ISO 9001", "ISO 14001"],
    "certification_level": "lead_auditor",
    "years_experience": 10,
    "certifications": ["IRCA Lead Auditor"],
    "max_audits_per_month": 8,
    "notes": "Test auditor for automated testing"
}

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, "No token in response"
    return data["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with authorization token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestAuditorCRUD:
    """Test CRUD operations for auditors"""
    
    created_auditor_id = None  # Class variable to store created auditor ID
    
    def test_01_list_auditors_empty_or_existing(self, auth_headers):
        """Test GET /api/auditors - List all auditors"""
        response = requests.get(f"{BASE_URL}/api/auditors", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} existing auditors")
        
        # If there are existing auditors, verify the structure
        if len(data) > 0:
            auditor = data[0]
            assert "id" in auditor, "Auditor should have an id"
            assert "name" in auditor, "Auditor should have a name"
            assert "email" in auditor, "Auditor should have an email"
            print(f"First auditor: {auditor.get('name')} ({auditor.get('email')})")
    
    def test_02_create_auditor(self, auth_headers):
        """Test POST /api/auditors - Create a new auditor"""
        # First, clean up any existing test auditor with same email
        existing = requests.get(f"{BASE_URL}/api/auditors", headers=auth_headers)
        if existing.status_code == 200:
            for auditor in existing.json():
                if auditor.get("email") == TEST_AUDITOR["email"]:
                    # Delete existing test auditor
                    requests.delete(f"{BASE_URL}/api/auditors/{auditor['id']}", headers=auth_headers)
                    print(f"Cleaned up existing test auditor: {auditor['id']}")
        
        response = requests.post(f"{BASE_URL}/api/auditors", json=TEST_AUDITOR, headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "auditor_id" in data, "Response should contain auditor_id"
        assert data.get("message") == "Auditor created", f"Unexpected message: {data.get('message')}"
        
        TestAuditorCRUD.created_auditor_id = data["auditor_id"]
        print(f"Created auditor with ID: {TestAuditorCRUD.created_auditor_id}")
    
    def test_03_get_auditor_by_id(self, auth_headers):
        """Test GET /api/auditors/{auditor_id} - Get single auditor details"""
        assert TestAuditorCRUD.created_auditor_id is not None, "Auditor ID not set from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        auditor = response.json()
        
        # Verify auditor data matches what was created
        assert auditor["id"] == TestAuditorCRUD.created_auditor_id
        assert auditor["name"] == TEST_AUDITOR["name"]
        assert auditor["email"] == TEST_AUDITOR["email"]
        assert auditor["certification_level"] == TEST_AUDITOR["certification_level"]
        assert auditor["specializations"] == TEST_AUDITOR["specializations"]
        assert auditor["status"] == "active"  # Default status
        print(f"Verified auditor: {auditor['name']}, Level: {auditor['certification_level']}")
    
    def test_04_update_auditor(self, auth_headers):
        """Test PUT /api/auditors/{auditor_id} - Update auditor"""
        assert TestAuditorCRUD.created_auditor_id is not None, "Auditor ID not set"
        
        updates = {
            "years_experience": 12,
            "max_audits_per_month": 10,
            "notes": "Updated via automated test"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            json=updates,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("message") == "Auditor updated", f"Unexpected message: {data.get('message')}"
        
        # Verify the update was persisted
        get_response = requests.get(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        updated_auditor = get_response.json()
        assert updated_auditor["years_experience"] == 12, "Years experience not updated"
        assert updated_auditor["max_audits_per_month"] == 10, "Max audits not updated"
        print(f"Updated auditor - experience: {updated_auditor['years_experience']} years")
    
    def test_05_set_auditor_availability(self, auth_headers):
        """Test POST /api/auditors/{auditor_id}/availability - Set availability"""
        assert TestAuditorCRUD.created_auditor_id is not None, "Auditor ID not set"
        
        # Set availability for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        availability_data = {
            "date": tomorrow,
            "is_available": False,
            "reason": "vacation"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}/availability",
            json=availability_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("message") == "Availability updated", f"Unexpected message: {data.get('message')}"
        
        # Verify availability was set
        get_response = requests.get(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        auditor = get_response.json()
        
        availability = auditor.get("availability", [])
        assert len(availability) > 0, "Availability array should not be empty"
        
        # Find the entry for tomorrow
        tomorrow_entry = next((a for a in availability if a.get("date") == tomorrow), None)
        assert tomorrow_entry is not None, f"No availability entry for {tomorrow}"
        assert tomorrow_entry["is_available"] == False, "Should be unavailable"
        assert tomorrow_entry["reason"] == "vacation", "Reason should be vacation"
        print(f"Set availability for {tomorrow}: unavailable (vacation)")
    
    def test_06_delete_auditor_soft_delete(self, auth_headers):
        """Test DELETE /api/auditors/{auditor_id} - Soft delete (deactivate)"""
        assert TestAuditorCRUD.created_auditor_id is not None, "Auditor ID not set"
        
        response = requests.delete(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("message") == "Auditor deactivated", f"Unexpected message: {data.get('message')}"
        
        # Verify auditor is now inactive (not deleted)
        get_response = requests.get(
            f"{BASE_URL}/api/auditors/{TestAuditorCRUD.created_auditor_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200, "Auditor should still exist after soft delete"
        auditor = get_response.json()
        assert auditor["status"] == "inactive", "Auditor status should be inactive"
        print(f"Auditor soft-deleted (status: {auditor['status']})")


class TestAuditorErrorHandling:
    """Test error cases for auditor API"""
    
    def test_get_nonexistent_auditor(self, auth_headers):
        """Test getting a non-existent auditor returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/auditors/nonexistent-id-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for non-existent auditor")
    
    def test_create_auditor_duplicate_email(self, auth_headers):
        """Test creating auditor with duplicate email returns 400"""
        # First create an auditor
        unique_auditor = {
            "name": "TEST_Duplicate Test",
            "email": "test_duplicate@audit.com",
            "phone": "+966-11-9999999",
            "certification_level": "auditor"
        }
        
        # Create first auditor
        response1 = requests.post(f"{BASE_URL}/api/auditors", json=unique_auditor, headers=auth_headers)
        
        if response1.status_code == 200:
            # Try to create another with same email
            response2 = requests.post(f"{BASE_URL}/api/auditors", json=unique_auditor, headers=auth_headers)
            assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"
            print("Correctly rejects duplicate email")
            
            # Cleanup
            auditor_id = response1.json().get("auditor_id")
            if auditor_id:
                requests.delete(f"{BASE_URL}/api/auditors/{auditor_id}", headers=auth_headers)
        else:
            # Auditor already exists from previous test run
            print("Auditor already exists, skipping duplicate test")
    
    def test_update_nonexistent_auditor(self, auth_headers):
        """Test updating non-existent auditor returns 404"""
        response = requests.put(
            f"{BASE_URL}/api/auditors/nonexistent-id-12345",
            json={"name": "New Name"},
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for updating non-existent auditor")
    
    def test_set_availability_nonexistent_auditor(self, auth_headers):
        """Test setting availability for non-existent auditor returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/auditors/nonexistent-id-12345/availability",
            json={"date": "2026-02-01", "is_available": True},
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for non-existent auditor availability")


class TestAuditorFiltering:
    """Test filtering capabilities for auditor list"""
    
    def test_filter_by_status(self, auth_headers):
        """Test filtering auditors by status"""
        response = requests.get(
            f"{BASE_URL}/api/auditors?status=active",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # All returned auditors should be active
        for auditor in data:
            assert auditor.get("status") == "active", f"Auditor {auditor.get('name')} has status {auditor.get('status')}"
        print(f"Filter by status=active returned {len(data)} auditors")
    
    def test_filter_by_specialization(self, auth_headers):
        """Test filtering auditors by specialization"""
        response = requests.get(
            f"{BASE_URL}/api/auditors?specialization=ISO 9001",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # All returned auditors should have ISO 9001 specialization
        for auditor in data:
            specs = auditor.get("specializations", [])
            assert "ISO 9001" in specs, f"Auditor {auditor.get('name')} missing ISO 9001 specialization"
        print(f"Filter by specialization=ISO 9001 returned {len(data)} auditors")


class TestAuditorAuthentication:
    """Test authentication requirements for auditor APIs"""
    
    def test_list_auditors_requires_auth(self):
        """Test that listing auditors requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auditors")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("List auditors correctly requires authentication")
    
    def test_create_auditor_requires_auth(self):
        """Test that creating auditor requires authentication"""
        response = requests.post(f"{BASE_URL}/api/auditors", json={
            "name": "Unauthorized Test",
            "email": "unauth@test.com"
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Create auditor correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
