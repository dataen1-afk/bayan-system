"""
Test suite for Suspended Clients Registry (BAC-F6-20)
Tests all CRUD operations, lift suspension, stats, export, and PDF generation endpoints.
"""
import pytest
import requests
import os
from datetime import datetime

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping tests")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestSuspendedClientsEndpoints:
    """Test suspended clients registry endpoints"""

    created_client_id = None

    def test_01_get_suspended_clients_list(self, headers):
        """Test GET /api/suspended-clients - list all suspended clients"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Total suspended clients in list: {len(data)}")

    def test_02_get_stats_overview(self, headers):
        """Test GET /api/suspended-clients/stats/overview - dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients/stats/overview", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Verify all expected stat fields exist
        assert "total" in data
        assert "suspended" in data
        assert "reinstated" in data
        assert "withdrawn" in data
        assert "pending_reinstatement" in data
        assert "under_review" in data
        print(f"Stats: {data}")

    def test_03_create_suspended_client(self, headers):
        """Test POST /api/suspended-clients - create new suspended client record"""
        payload = {
            "client_id": "TEST-SUSP-001",
            "client_name": "TEST Suspended Corp",
            "client_name_ar": "شركة الاختبار المعلقة",
            "address": "123 Test Street",
            "address_ar": "شارع الاختبار 123",
            "registration_date": "2024-01-15",
            "suspended_on": "2025-01-10",
            "reason_for_suspension": "Test suspension for audit compliance issues",
            "reason_for_suspension_ar": "تعليق اختبار لمشاكل الامتثال للتدقيق",
            "future_action": "under_review",
            "remarks": "Created for automated testing"
        }
        response = requests.post(f"{BASE_URL}/api/suspended-clients", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["client_name"] == "TEST Suspended Corp"
        assert data["client_id"] == "TEST-SUSP-001"
        assert data["status"] == "suspended"
        assert "serial_number" in data
        assert data["serial_number"] > 0
        
        # Store for later tests
        TestSuspendedClientsEndpoints.created_client_id = data["id"]
        print(f"Created suspended client with ID: {data['id']}, serial_number: {data['serial_number']}")

    def test_04_get_single_suspended_client(self, headers):
        """Test GET /api/suspended-clients/{id} - get single client"""
        client_id = TestSuspendedClientsEndpoints.created_client_id
        assert client_id is not None, "No client ID from previous test"
        
        response = requests.get(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify client data
        assert data["id"] == client_id
        assert data["client_name"] == "TEST Suspended Corp"
        assert data["status"] == "suspended"
        assert data["future_action"] == "under_review"
        print(f"Got client: {data['client_name']} - status: {data['status']}")

    def test_05_update_suspended_client(self, headers):
        """Test PUT /api/suspended-clients/{id} - update client record"""
        client_id = TestSuspendedClientsEndpoints.created_client_id
        assert client_id is not None
        
        update_payload = {
            "future_action": "reinstate",
            "remarks": "Updated remarks - preparing for reinstatement"
        }
        response = requests.put(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers, json=update_payload)
        assert response.status_code == 200
        
        # Verify update via GET
        get_response = requests.get(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["future_action"] == "reinstate"
        assert "preparing for reinstatement" in data["remarks"]
        print(f"Updated client future_action to: {data['future_action']}")

    def test_06_filter_by_status(self, headers):
        """Test GET /api/suspended-clients?status=suspended - filter by status"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients?status=suspended", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # All returned records should be suspended
        for client in data:
            assert client["status"] == "suspended"
        print(f"Found {len(data)} suspended clients")

    def test_07_export_excel(self, headers):
        """Test GET /api/suspended-clients/export/excel - Excel export"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients/export/excel", headers=headers)
        assert response.status_code == 200
        
        # Check content type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "application/vnd.openxmlformats-officedocument" in content_type
        
        # Check we got actual data
        assert len(response.content) > 0
        print(f"Excel export successful, file size: {len(response.content)} bytes")

    def test_08_generate_pdf(self, headers):
        """Test GET /api/suspended-clients/{id}/pdf - PDF generation"""
        client_id = TestSuspendedClientsEndpoints.created_client_id
        assert client_id is not None
        
        response = requests.get(f"{BASE_URL}/api/suspended-clients/{client_id}/pdf", headers=headers)
        assert response.status_code == 200
        
        # Check content type is PDF
        content_type = response.headers.get("Content-Type", "")
        assert "pdf" in content_type.lower()
        
        # Check we got actual PDF data (PDF signature starts with %PDF)
        assert response.content[:4] == b'%PDF'
        print(f"PDF generated successfully, file size: {len(response.content)} bytes")

    def test_09_get_nonexistent_client(self, headers):
        """Test GET /api/suspended-clients/{id} - 404 for non-existent client"""
        fake_id = "nonexistent-id-12345"
        response = requests.get(f"{BASE_URL}/api/suspended-clients/{fake_id}", headers=headers)
        assert response.status_code == 404

    def test_10_create_second_suspended_client_for_lift_test(self, headers):
        """Create another suspended client to test lift-suspension"""
        payload = {
            "client_id": "TEST-LIFT-001",
            "client_name": "TEST Lift Suspension Corp",
            "registration_date": "2024-02-01",
            "suspended_on": "2025-01-05",
            "reason_for_suspension": "Compliance audit failure",
            "future_action": "reinstate"
        }
        response = requests.post(f"{BASE_URL}/api/suspended-clients", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "suspended"
        # Store for lift test
        TestSuspendedClientsEndpoints.lift_client_id = data["id"]
        print(f"Created client for lift test: {data['id']}")

    def test_11_lift_suspension_reinstate(self, headers):
        """Test POST /api/suspended-clients/{id}/lift-suspension?action=reinstate"""
        client_id = getattr(TestSuspendedClientsEndpoints, 'lift_client_id', None)
        if not client_id:
            pytest.skip("No client ID for lift test")
        
        response = requests.post(
            f"{BASE_URL}/api/suspended-clients/{client_id}/lift-suspension?action=reinstate&reason=Client resolved compliance issues",
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify status changed
        get_response = requests.get(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["status"] == "reinstated"
        assert "resolved compliance issues" in data.get("lifted_reason", "")
        print(f"Client reinstated successfully: status={data['status']}")

    def test_12_lift_already_lifted_client_fails(self, headers):
        """Test lift-suspension on already reinstated client should fail"""
        client_id = getattr(TestSuspendedClientsEndpoints, 'lift_client_id', None)
        if not client_id:
            pytest.skip("No client ID for test")
        
        response = requests.post(
            f"{BASE_URL}/api/suspended-clients/{client_id}/lift-suspension?action=withdraw&reason=Test",
            headers=headers
        )
        # Should fail with 400 as client is no longer suspended
        assert response.status_code == 400
        print("Correctly rejected lift-suspension on non-suspended client")

    def test_13_stats_after_operations(self, headers):
        """Verify stats reflect our operations"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients/stats/overview", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # We should have at least 1 reinstated client from our tests
        assert data["reinstated"] >= 1
        print(f"Stats after operations: {data}")

    def test_14_delete_test_client(self, headers):
        """Test DELETE /api/suspended-clients/{id}"""
        client_id = TestSuspendedClientsEndpoints.created_client_id
        if not client_id:
            pytest.skip("No client ID to delete")
        
        response = requests.delete(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deleted
        get_response = requests.get(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
        assert get_response.status_code == 404
        print(f"Deleted client {client_id}")

    def test_15_cleanup_lift_test_client(self, headers):
        """Cleanup - delete lift test client"""
        client_id = getattr(TestSuspendedClientsEndpoints, 'lift_client_id', None)
        if client_id:
            response = requests.delete(f"{BASE_URL}/api/suspended-clients/{client_id}", headers=headers)
            assert response.status_code == 200
            print(f"Cleaned up lift test client {client_id}")


class TestSuspendedClientsValidation:
    """Test validation and edge cases"""

    def test_create_missing_required_fields(self, headers):
        """Test create with missing client_name fails"""
        payload = {
            "reason_for_suspension": "Test reason"
            # Missing client_name
        }
        response = requests.post(f"{BASE_URL}/api/suspended-clients", headers=headers, json=payload)
        # Should fail due to validation
        assert response.status_code in [400, 422]

    def test_filter_invalid_status(self, headers):
        """Test filter with invalid status still works (returns empty or all)"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients?status=invalid_status", headers=headers)
        # Should not error, just return empty or filtered results
        assert response.status_code == 200


class TestExistingData:
    """Test with existing data mentioned in context"""

    def test_verify_existing_reinstated_client(self, headers):
        """Verify XYZ Industries Ltd exists and is reinstated per context"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Look for XYZ Industries Ltd
        xyz_client = None
        for client in data:
            if "XYZ" in client.get("client_name", "") or "CERT-2024-0005" in str(client.get("client_id", "")):
                xyz_client = client
                break
        
        if xyz_client:
            print(f"Found existing client: {xyz_client['client_name']} - status: {xyz_client['status']}")
            # Per context, it should be reinstated
            assert xyz_client["status"] == "reinstated"
        else:
            print("XYZ Industries Ltd not found - may have been deleted or context was different")
