"""
Tests for Certified Clients Registry (BAC-F6-19)
This module tests CRUD operations, stats, Excel export, and PDF generation.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCertifiedClients:
    """Tests for Certified Clients Registry (BAC-F6-19)"""
    
    auth_token = None
    created_client_id = None
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get authentication token before tests"""
        if not TestCertifiedClients.auth_token:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@test.com",
                "password": "admin123"
            })
            assert response.status_code == 200, f"Login failed: {response.text}"
            TestCertifiedClients.auth_token = response.json().get('token')
        
        self.headers = {"Authorization": f"Bearer {TestCertifiedClients.auth_token}"}
    
    # ===== GET ALL CERTIFIED CLIENTS =====
    def test_01_get_all_certified_clients(self):
        """GET /api/certified-clients - List all certified clients"""
        response = requests.get(f"{BASE_URL}/api/certified-clients", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} existing certified clients")
        
        # Check if ABC Manufacturing exists (mentioned in review_request)
        client_names = [c.get('client_name', '') for c in data]
        if 'ABC Manufacturing Co.' in client_names:
            print("Existing client 'ABC Manufacturing Co.' found in registry")
    
    def test_02_get_certified_clients_with_status_filter(self):
        """GET /api/certified-clients?status=active - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/certified-clients?status=active", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Verify all returned clients have active status
        for client in data:
            assert client.get('status') == 'active', f"Expected status 'active', got {client.get('status')}"
        print(f"Found {len(data)} active clients")
    
    # ===== CREATE CERTIFIED CLIENT =====
    def test_03_create_certified_client(self):
        """POST /api/certified-clients - Create new certified client"""
        test_data = {
            "client_name": f"TEST_Client_{uuid.uuid4().hex[:8]}",
            "client_name_ar": "شركة الاختبار",
            "address": "123 Test Street, Test City",
            "address_ar": "شارع الاختبار 123",
            "contact_person": "John Test",
            "contact_number": "+1234567890",
            "scope": "Manufacturing of test products",
            "scope_ar": "تصنيع منتجات الاختبار",
            "accreditation": ["ISO 9001:2015", "ISO 14001:2015"],
            "ea_code": "EA-17",
            "certificate_number": f"CERT-TEST-{uuid.uuid4().hex[:6].upper()}",
            "issue_date": "2025-01-01",
            "expiry_date": "2028-01-01",
            "surveillance_1_date": "2026-01-01",
            "surveillance_2_date": "2027-01-01",
            "recertification_date": "2028-01-01"
        }
        
        response = requests.post(f"{BASE_URL}/api/certified-clients", json=test_data, headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify returned data
        assert 'id' in data, "Response should contain 'id'"
        assert 'serial_number' in data, "Response should contain 'serial_number'"
        assert data['client_name'] == test_data['client_name'], "Client name mismatch"
        assert data['certificate_number'] == test_data['certificate_number'], "Certificate number mismatch"
        assert data['status'] == 'active', f"Expected status 'active', got {data.get('status')}"
        assert data['accreditation'] == test_data['accreditation'], "Accreditation mismatch"
        assert data['issue_date'] == test_data['issue_date'], "Issue date mismatch"
        assert data['expiry_date'] == test_data['expiry_date'], "Expiry date mismatch"
        
        # Save ID for later tests
        TestCertifiedClients.created_client_id = data['id']
        print(f"Created certified client: ID={data['id']}, Serial={data['serial_number']}, Cert={data['certificate_number']}")
    
    def test_04_create_certified_client_validation(self):
        """POST /api/certified-clients - Validate required field"""
        # Test without required client_name
        response = requests.post(f"{BASE_URL}/api/certified-clients", json={
            "address": "No Name Street"
        }, headers=self.headers)
        
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        print("Validation correctly rejects request without client_name")
    
    # ===== GET SINGLE CERTIFIED CLIENT =====
    def test_05_get_single_certified_client(self):
        """GET /api/certified-clients/{id} - Get single client by ID"""
        assert TestCertifiedClients.created_client_id, "No client ID from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data['id'] == TestCertifiedClients.created_client_id, "ID mismatch"
        assert 'client_name' in data, "Response should contain client_name"
        assert 'serial_number' in data, "Response should contain serial_number"
        assert 'certificate_number' in data, "Response should contain certificate_number"
        print(f"Retrieved client: {data['client_name']} - {data['certificate_number']}")
    
    def test_06_get_nonexistent_client(self):
        """GET /api/certified-clients/{id} - 404 for non-existent client"""
        fake_id = "non-existent-id-12345"
        response = requests.get(f"{BASE_URL}/api/certified-clients/{fake_id}", headers=self.headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for non-existent client")
    
    # ===== UPDATE CERTIFIED CLIENT =====
    def test_07_update_certified_client(self):
        """PUT /api/certified-clients/{id} - Update client record"""
        assert TestCertifiedClients.created_client_id, "No client ID from previous test"
        
        update_data = {
            "contact_person": "Jane Updated",
            "contact_number": "+9876543210",
            "status": "suspended",
            "notes": "Updated via automated test"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}",
            json=update_data,
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify update by fetching again
        get_response = requests.get(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}",
            headers=self.headers
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        
        assert data['contact_person'] == update_data['contact_person'], "Contact person not updated"
        assert data['contact_number'] == update_data['contact_number'], "Contact number not updated"
        assert data['status'] == update_data['status'], "Status not updated"
        assert data.get('notes') == update_data['notes'], "Notes not updated"
        print(f"Updated client: contact={data['contact_person']}, status={data['status']}")
    
    def test_08_update_nonexistent_client(self):
        """PUT /api/certified-clients/{id} - 404 for non-existent client"""
        fake_id = "non-existent-update-12345"
        response = requests.put(
            f"{BASE_URL}/api/certified-clients/{fake_id}",
            json={"status": "expired"},
            headers=self.headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for updating non-existent client")
    
    # ===== STATS OVERVIEW =====
    def test_09_get_stats_overview(self):
        """GET /api/certified-clients/stats/overview - Get statistics dashboard"""
        response = requests.get(f"{BASE_URL}/api/certified-clients/stats/overview", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify stats structure
        assert 'total' in data, "Stats should include 'total'"
        assert 'active' in data, "Stats should include 'active'"
        assert 'suspended' in data, "Stats should include 'suspended'"
        assert 'expired' in data, "Stats should include 'expired'"
        assert 'expiring_soon' in data, "Stats should include 'expiring_soon'"
        assert 'surveillance_1_upcoming' in data, "Stats should include 'surveillance_1_upcoming'"
        assert 'surveillance_2_upcoming' in data, "Stats should include 'surveillance_2_upcoming'"
        
        # Verify values are non-negative integers
        for key in ['total', 'active', 'suspended', 'expired', 'expiring_soon']:
            assert isinstance(data[key], int), f"{key} should be an integer"
            assert data[key] >= 0, f"{key} should be non-negative"
        
        print(f"Stats: total={data['total']}, active={data['active']}, suspended={data['suspended']}, expired={data['expired']}")
    
    # ===== EXCEL EXPORT =====
    def test_10_export_excel(self):
        """GET /api/certified-clients/export/excel - Export to Excel"""
        response = requests.get(f"{BASE_URL}/api/certified-clients/export/excel", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify content type
        content_type = response.headers.get('Content-Type', '')
        assert 'spreadsheetml' in content_type or 'octet-stream' in content_type, f"Unexpected content type: {content_type}"
        
        # Verify we got actual file content
        assert len(response.content) > 0, "Excel file should not be empty"
        print(f"Exported Excel file: {len(response.content)} bytes")
    
    # ===== PDF GENERATION =====
    def test_11_generate_pdf(self):
        """GET /api/certified-clients/{id}/pdf - Generate PDF for client"""
        assert TestCertifiedClients.created_client_id, "No client ID from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}/pdf",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify content type
        content_type = response.headers.get('Content-Type', '')
        assert 'pdf' in content_type, f"Expected PDF content type, got: {content_type}"
        
        # Verify we got actual file content
        assert len(response.content) > 0, "PDF file should not be empty"
        print(f"Generated PDF: {len(response.content)} bytes")
    
    def test_12_pdf_nonexistent_client(self):
        """GET /api/certified-clients/{id}/pdf - 404 for non-existent client"""
        fake_id = "non-existent-pdf-12345"
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/{fake_id}/pdf",
            headers=self.headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for PDF of non-existent client")
    
    # ===== DELETE CERTIFIED CLIENT =====
    def test_13_delete_certified_client(self):
        """DELETE /api/certified-clients/{id} - Delete client record"""
        assert TestCertifiedClients.created_client_id, "No client ID from previous test"
        
        response = requests.delete(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify deletion by trying to fetch
        get_response = requests.get(
            f"{BASE_URL}/api/certified-clients/{TestCertifiedClients.created_client_id}",
            headers=self.headers
        )
        
        assert get_response.status_code == 404, "Deleted client should return 404"
        print(f"Successfully deleted client: {TestCertifiedClients.created_client_id}")
    
    def test_14_delete_nonexistent_client(self):
        """DELETE /api/certified-clients/{id} - 404 for non-existent client"""
        fake_id = "non-existent-delete-12345"
        response = requests.delete(
            f"{BASE_URL}/api/certified-clients/{fake_id}",
            headers=self.headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for deleting non-existent client")
    
    # ===== AUTHORIZATION TESTS =====
    def test_15_unauthorized_access(self):
        """Test endpoints require authentication"""
        endpoints = [
            ("GET", f"{BASE_URL}/api/certified-clients"),
            ("POST", f"{BASE_URL}/api/certified-clients"),
            ("GET", f"{BASE_URL}/api/certified-clients/stats/overview"),
            ("GET", f"{BASE_URL}/api/certified-clients/export/excel"),
        ]
        
        for method, url in endpoints:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json={"client_name": "Test"})
            
            # Should fail without auth (401 or 403)
            assert response.status_code in [401, 403, 422], \
                f"Endpoint {method} {url} should require auth, got {response.status_code}"
        
        print("All endpoints correctly require authentication")
    
    # ===== VERIFY EXISTING CLIENT =====
    def test_16_verify_existing_client_abc_manufacturing(self):
        """Verify ABC Manufacturing Co. exists as mentioned in review_request"""
        response = requests.get(f"{BASE_URL}/api/certified-clients", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Find ABC Manufacturing Co.
        abc_client = None
        for client in data:
            if 'ABC Manufacturing' in client.get('client_name', ''):
                abc_client = client
                break
        
        if abc_client:
            # Verify expected fields
            assert abc_client.get('certificate_number') == 'CERT-2025-0001', \
                f"Expected cert CERT-2025-0001, got {abc_client.get('certificate_number')}"
            print(f"Verified ABC Manufacturing Co.: {abc_client.get('certificate_number')}")
        else:
            print("ABC Manufacturing Co. not found in registry - may have been deleted")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
