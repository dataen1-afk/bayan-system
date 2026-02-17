"""
Iteration 15 Tests: Bilingual PDF, Google Calendar Status API, Documents Page
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://facility-grants.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def admin_auth():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return {"Authorization": f"Bearer {response.json()['token']}"}
    pytest.skip(f"Admin login failed: {response.text}")


@pytest.fixture(scope="module")
def signed_contract(admin_auth):
    """Find an existing signed contract for PDF testing"""
    response = requests.get(f"{BASE_URL}/api/proposals", headers=admin_auth)
    if response.status_code == 200:
        proposals = response.json()
        signed = [p for p in proposals if p.get('status') == 'agreement_signed']
        if signed:
            return signed[0]
    return None


class TestGoogleCalendarStatusAPI:
    """Test Google Calendar status endpoint"""
    
    def test_calendar_status_endpoint_returns_200(self, admin_auth):
        """Test /api/calendar/status returns 200 with proper structure"""
        response = requests.get(f"{BASE_URL}/api/calendar/status", headers=admin_auth)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check structure
        assert "enabled" in data, "Missing 'enabled' field"
        assert "configured" in data, "Missing 'configured' field"
        assert "connected" in data, "Missing 'connected' field"
        assert "message" in data, "Missing 'message' field"
        
        # Since GOOGLE_CLIENT_ID not set, should return not configured
        assert data["configured"] == False, "Expected configured=False when GOOGLE_CLIENT_ID not set"
        assert data["enabled"] == False, "Expected enabled=False when not configured"
        print(f"Calendar status: {data}")
    
    def test_calendar_status_without_auth_returns_401(self):
        """Test /api/calendar/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/calendar/status")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestBilingualPDFEndpoints:
    """Test Bilingual PDF download endpoints"""
    
    def test_admin_bilingual_pdf_endpoint_structure(self, admin_auth, signed_contract):
        """Test admin bilingual PDF endpoint returns valid PDF"""
        if not signed_contract:
            pytest.skip("No signed contract found for testing")
        
        # First find the agreement for this proposal
        agreement_response = requests.get(
            f"{BASE_URL}/api/public/agreement/{signed_contract['access_token']}",
            headers=admin_auth
        )
        
        if agreement_response.status_code != 200 or agreement_response.json().get('status') != 'submitted':
            pytest.skip("No submitted agreement found")
        
        agreement = agreement_response.json().get('agreement')
        agreement_id = agreement.get('id') if agreement else None
        
        if not agreement_id:
            pytest.skip("Could not find agreement ID")
        
        # Test bilingual PDF endpoint
        response = requests.get(
            f"{BASE_URL}/api/contracts/{agreement_id}/pdf/bilingual",
            headers=admin_auth
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert 'application/pdf' in response.headers.get('Content-Type', ''), "Expected PDF content type"
        
        # Check PDF header
        content = response.content
        assert content[:4] == b'%PDF', "Response should be a valid PDF file"
        print(f"Bilingual PDF generated successfully, size: {len(content)} bytes")
    
    def test_public_bilingual_pdf_endpoint(self, signed_contract):
        """Test public bilingual PDF endpoint returns valid PDF"""
        if not signed_contract:
            pytest.skip("No signed contract found for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/{signed_contract['access_token']}/pdf/bilingual"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert 'application/pdf' in response.headers.get('Content-Type', ''), "Expected PDF content type"
        
        # Check PDF header
        content = response.content
        assert content[:4] == b'%PDF', "Response should be a valid PDF file"
        print(f"Public bilingual PDF generated successfully, size: {len(content)} bytes")
    
    def test_public_standard_pdf_still_works(self, signed_contract):
        """Test standard PDF endpoint still works"""
        if not signed_contract:
            pytest.skip("No signed contract found for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/{signed_contract['access_token']}/pdf"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'application/pdf' in response.headers.get('Content-Type', ''), "Expected PDF content type"
        print(f"Standard PDF still works, size: {len(response.content)} bytes")
    
    def test_bilingual_pdf_invalid_token_returns_404(self):
        """Test bilingual PDF with invalid token returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/invalid-token-12345/pdf/bilingual"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestDocumentsAPI:
    """Test Documents API endpoints"""
    
    def test_get_documents_endpoint(self, admin_auth):
        """Test GET /api/documents returns list"""
        response = requests.get(f"{BASE_URL}/api/documents", headers=admin_auth)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of documents"
        print(f"Documents count: {len(data)}")
    
    def test_create_document(self, admin_auth):
        """Test POST /api/documents creates a document"""
        import base64
        
        # Create a small test file content
        test_content = b"Test document content for iteration 15"
        file_base64 = base64.b64encode(test_content).decode()
        
        response = requests.post(
            f"{BASE_URL}/api/documents",
            headers=admin_auth,
            json={
                "name": "TEST_iteration15_doc.txt",
                "file_type": "text/plain",
                "category": "test",
                "file_data": file_base64,  # API expects file_data not content
                "related_type": "test",
                "related_id": "test-123"
            }
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data or "message" in data, "Expected id or success message in response"
        print(f"Document created: {data}")
        
        # Return document ID for cleanup
        return data.get("id")
    
    def test_documents_without_auth_returns_401(self):
        """Test /api/documents requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"


class TestAdminDashboardContractButtons:
    """Test that contracts tab has both PDF download buttons"""
    
    def test_proposals_endpoint_returns_access_token(self, admin_auth):
        """Test that proposals include access_token for PDF download"""
        response = requests.get(f"{BASE_URL}/api/proposals", headers=admin_auth)
        
        assert response.status_code == 200
        proposals = response.json()
        
        if proposals:
            signed = [p for p in proposals if p.get('status') == 'agreement_signed']
            if signed:
                proposal = signed[0]
                assert 'access_token' in proposal, "Proposal should have access_token for PDF download"
                assert 'organization_name' in proposal, "Proposal should have organization_name"
                print(f"Found signed contract: {proposal['organization_name']} with access_token")


class TestHealthCheck:
    """Basic health checks"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
    
    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
