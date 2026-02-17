"""
Test modular routes after refactoring from monolithic server.py
Tests: auth, notifications, sites, contacts, documents routes
Also verifies that monolith routes still work: auditors, certificates, forms
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

class TestAuthRoutes:
    """Tests for /api/auth/* modular routes"""
    
    def test_login_success(self):
        """POST /api/auth/login - successful authentication"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Token missing from response"
        assert "user" in data, "User missing from response"
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        assert isinstance(data["token"], str) and len(data["token"]) > 0
        print(f"✓ Login successful, token received")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@test.com", "password": "wrongpass"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid login correctly returns 401")
    
    def test_get_current_user(self):
        """GET /api/auth/me - get current user info with token"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = login_response.json()["token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Get me failed: {response.text}"
        
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "admin"
        print(f"✓ GET /api/auth/me returns correct user info")
    
    def test_get_me_without_token(self):
        """GET /api/auth/me - without token returns 403/401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Unauthenticated /api/auth/me correctly denied")


class TestNotificationRoutes:
    """Tests for /api/notifications/* modular routes"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_notifications(self, auth_token):
        """GET /api/notifications - get notifications list"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get notifications failed: {response.text}"
        
        data = response.json()
        assert "notifications" in data, "notifications key missing"
        assert "unread_count" in data, "unread_count key missing"
        assert isinstance(data["notifications"], list)
        assert isinstance(data["unread_count"], int)
        print(f"✓ GET /api/notifications returns list with unread_count={data['unread_count']}")
    
    def test_get_notifications_unauthorized(self):
        """GET /api/notifications - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Unauthenticated notifications request correctly denied")


class TestSiteRoutes:
    """Tests for /api/sites/* modular routes"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_sites(self, auth_token):
        """GET /api/sites - get sites list"""
        response = requests.get(
            f"{BASE_URL}/api/sites",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get sites failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Sites should return a list"
        print(f"✓ GET /api/sites returns {len(data)} sites")
    
    def test_create_site_and_verify(self, auth_token):
        """POST /api/sites - create site and GET to verify persistence"""
        # Create site
        site_data = {
            "name": "TEST_Site_Modular_Routes",
            "address": "123 Test Street",
            "city": "Test City",
            "country": "Test Country",
            "contact_name": "Test Contact",
            "contact_email": "test@example.com",
            "contact_phone": "+1234567890"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sites",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=site_data
        )
        assert response.status_code == 200, f"Create site failed: {response.text}"
        
        create_data = response.json()
        assert "id" in create_data, "Created site should have an ID"
        assert "message" in create_data
        
        site_id = create_data["id"]
        print(f"✓ POST /api/sites created site with id={site_id}")
        
        # Verify by getting all sites
        get_response = requests.get(
            f"{BASE_URL}/api/sites",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 200
        
        sites = get_response.json()
        created_site = next((s for s in sites if s.get("id") == site_id), None)
        assert created_site is not None, "Created site not found in list"
        assert created_site["name"] == site_data["name"]
        print(f"✓ Site persisted and verified via GET")
        
        # Cleanup - delete the site
        delete_response = requests.delete(
            f"{BASE_URL}/api/sites/{site_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code == 200
        print(f"✓ Test site deleted successfully")
    
    def test_get_sites_unauthorized(self):
        """GET /api/sites - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/sites")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Unauthenticated sites request correctly denied")


class TestContactRoutes:
    """Tests for /api/contacts/* modular routes"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_contacts(self, auth_token):
        """GET /api/contacts - get contact records list"""
        response = requests.get(
            f"{BASE_URL}/api/contacts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get contacts failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Contacts should return a list"
        print(f"✓ GET /api/contacts returns {len(data)} contact records")
    
    def test_get_contacts_unauthorized(self):
        """GET /api/contacts - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/contacts")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Unauthenticated contacts request correctly denied")


class TestDocumentRoutes:
    """Tests for /api/documents/* modular routes"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_documents(self, auth_token):
        """GET /api/documents - get documents list"""
        response = requests.get(
            f"{BASE_URL}/api/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get documents failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Documents should return a list"
        print(f"✓ GET /api/documents returns {len(data)} documents")
    
    def test_get_documents_unauthorized(self):
        """GET /api/documents - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/documents")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Unauthenticated documents request correctly denied")


class TestMonolithRoutes:
    """Tests to verify monolith routes still work after modular migration"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["token"]
    
    def test_get_auditors(self, auth_token):
        """GET /api/auditors - monolith route should still work"""
        response = requests.get(
            f"{BASE_URL}/api/auditors",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get auditors failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Auditors should return a list"
        print(f"✓ GET /api/auditors (monolith) returns {len(data)} auditors")
    
    def test_get_certificates(self, auth_token):
        """GET /api/certificates - monolith route should still work"""
        response = requests.get(
            f"{BASE_URL}/api/certificates",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get certificates failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Certificates should return a list"
        print(f"✓ GET /api/certificates (monolith) returns {len(data)} certificates")
    
    def test_get_forms(self, auth_token):
        """GET /api/forms - monolith route should still work"""
        response = requests.get(
            f"{BASE_URL}/api/forms",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get forms failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Forms should return a list"
        print(f"✓ GET /api/forms (monolith) returns {len(data)} forms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
