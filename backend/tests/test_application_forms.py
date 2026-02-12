"""
Backend API Tests for Service Contract Management System
Tests: Authentication, Application Forms, Form Assignment, and CRUD operations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_CREDENTIALS = {"email": "admin@test.com", "password": "admin123"}
CLIENT_CREDENTIALS = {"email": "client@test.com", "password": "client123"}


class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_CREDENTIALS["email"]
        assert data["user"]["role"] == "admin"
    
    def test_client_login_success(self):
        """Test client login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == CLIENT_CREDENTIALS["email"]
        assert data["user"]["role"] == "client"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
    
    def test_get_me_with_valid_token(self):
        """Test /auth/me endpoint with valid token"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        token = login_response.json()["token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_CREDENTIALS["email"]
    
    def test_get_me_without_token(self):
        """Test /auth/me endpoint without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403]


class TestAdminClientManagement:
    """Admin client management tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_get_clients_as_admin(self, admin_token):
        """Test getting client list as admin"""
        response = requests.get(
            f"{BASE_URL}/api/users/clients",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify all returned users are clients
        for user in data:
            assert user.get("role") == "client"
    
    def test_get_clients_as_client_forbidden(self):
        """Test that clients cannot access client list"""
        # Login as client
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        token = login_response.json()["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/users/clients",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestApplicationForms:
    """Application form CRUD tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Client authentication failed")
    
    @pytest.fixture
    def client_id(self, admin_token):
        """Get client ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/users/clients",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]["id"]
        pytest.skip("No clients found")
    
    def test_create_application_form_as_admin(self, admin_token, client_id):
        """Test admin creating an application form for a client"""
        response = requests.post(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"client_id": client_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["client_id"] == client_id
        assert data["status"] == "pending"
        assert data["company_data"] is None
        return data["id"]
    
    def test_create_application_form_as_client_forbidden(self, client_token, client_id):
        """Test that clients cannot create application forms"""
        response = requests.post(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {client_token}"},
            json={"client_id": client_id}
        )
        assert response.status_code == 403
    
    def test_get_application_forms_as_admin(self, admin_token):
        """Test admin getting all application forms"""
        response = requests.get(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_application_forms_as_client(self, client_token):
        """Test client getting their application forms"""
        response = requests.get(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_save_draft_application_form(self, admin_token, client_token, client_id):
        """Test saving draft of application form"""
        # First create a form as admin
        create_response = requests.post(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"client_id": client_id}
        )
        assert create_response.status_code == 200
        form_id = create_response.json()["id"]
        
        # Save draft as client
        draft_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": "TEST_Draft Company",
                "address": "123 Test Street",
                "phoneNumber": "+966 12 345 6789",
                "website": "https://test.com",
                "email": "test@company.com",
                "contactPerson": "John Doe",
                "designation": "Manager",
                "mobileNumber": "+966 50 123 4567",
                "contactEmail": "john@company.com",
                "legalStatus": "private",
                "certificationSchemes": ["ISO9001"],
                "certificationProgram": "initial",
                "combinedAudit": "",
                "combinedAuditSpecification": "",
                "isInternalAuditCombined": "",
                "isMRMCombined": "",
                "isManualProceduresCombined": "",
                "isSystemIntegrated": "",
                "numberOfSites": 1,
                "site1Address": "123 Test Street",
                "site2Address": "",
                "totalEmployees": "50",
                "locationShifts": "2",
                "fullTimeEmployees": "40",
                "partTimeEmployees": "10",
                "temporaryEmployees": "0",
                "unskilledWorkers": "5",
                "remoteEmployees": "5",
                "isAlreadyCertified": "no",
                "currentCertifications": [],
                "isConsultantInvolved": "no",
                "consultantName": "",
                "transferReason": "",
                "currentCertificateExpiry": "",
                "keyBusinessProcesses": "Manufacturing and Quality Control",
                "hasEnvironmentAspectRegister": "",
                "hasEnvironmentalManual": "",
                "hasEnvironmentalAuditProgram": "",
                "numberOfHACCPStudies": "",
                "numberOfProcessLines": "",
                "processingType": "",
                "hazardsIdentified": "",
                "criticalRisks": "",
                "annualEnergyConsumption": "",
                "numberOfEnergySources": "",
                "numberOfSEUs": "",
                "productsInRange": "",
                "medicalDeviceTypes": [],
                "sterilizationType": "",
                "numberOfDeviceFiles": "",
                "applicableLegislations": "",
                "exportCountries": "",
                "productStandards": "",
                "intendedUse": "",
                "outsourceProcesses": "",
                "businessComplexity": "",
                "processStandard": "",
                "managementSystemLevel": "",
                "itEnvironmentComplexity": "",
                "outsourcingDependency": "",
                "systemDevelopment": "",
                "declarationName": "",
                "declarationDesignation": "",
                "declarationAgreed": False
            }
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/application-forms/{form_id}",
            headers={"Authorization": f"Bearer {client_token}"},
            json=draft_data
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["company_data"]["companyName"] == "TEST_Draft Company"
        assert updated_data["status"] == "pending"  # Still pending after draft save
        
        # Verify persistence with GET
        get_response = requests.get(
            f"{BASE_URL}/api/application-forms/{form_id}",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert get_response.status_code == 200
        fetched_data = get_response.json()
        assert fetched_data["company_data"]["companyName"] == "TEST_Draft Company"
    
    def test_submit_application_form(self, admin_token, client_token, client_id):
        """Test submitting a completed application form"""
        # First create a form as admin
        create_response = requests.post(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"client_id": client_id}
        )
        assert create_response.status_code == 200
        form_id = create_response.json()["id"]
        
        # Submit form with complete data
        submit_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": "TEST_Submitted Company",
                "address": "456 Submit Street",
                "phoneNumber": "+966 12 345 6789",
                "website": "https://submitted.com",
                "email": "submit@company.com",
                "contactPerson": "Jane Doe",
                "designation": "Director",
                "mobileNumber": "+966 50 987 6543",
                "contactEmail": "jane@company.com",
                "legalStatus": "public",
                "certificationSchemes": ["ISO9001", "ISO14001"],
                "certificationProgram": "initial",
                "combinedAudit": "yes",
                "combinedAuditSpecification": "ISO 9001 + ISO 14001",
                "isInternalAuditCombined": "yes",
                "isMRMCombined": "yes",
                "isManualProceduresCombined": "yes",
                "isSystemIntegrated": "yes",
                "numberOfSites": 2,
                "site1Address": "456 Submit Street",
                "site2Address": "789 Branch Road",
                "totalEmployees": "100",
                "locationShifts": "3",
                "fullTimeEmployees": "80",
                "partTimeEmployees": "15",
                "temporaryEmployees": "5",
                "unskilledWorkers": "10",
                "remoteEmployees": "10",
                "isAlreadyCertified": "no",
                "currentCertifications": [],
                "isConsultantInvolved": "yes",
                "consultantName": "Quality Consultants Inc",
                "transferReason": "",
                "currentCertificateExpiry": "",
                "keyBusinessProcesses": "Manufacturing, Quality Control, Environmental Management",
                "hasEnvironmentAspectRegister": "yes",
                "hasEnvironmentalManual": "yes",
                "hasEnvironmentalAuditProgram": "yes",
                "numberOfHACCPStudies": "",
                "numberOfProcessLines": "",
                "processingType": "",
                "hazardsIdentified": "",
                "criticalRisks": "",
                "annualEnergyConsumption": "",
                "numberOfEnergySources": "",
                "numberOfSEUs": "",
                "productsInRange": "",
                "medicalDeviceTypes": [],
                "sterilizationType": "",
                "numberOfDeviceFiles": "",
                "applicableLegislations": "",
                "exportCountries": "",
                "productStandards": "",
                "intendedUse": "",
                "outsourceProcesses": "",
                "businessComplexity": "",
                "processStandard": "",
                "managementSystemLevel": "",
                "itEnvironmentComplexity": "",
                "outsourcingDependency": "",
                "systemDevelopment": "",
                "declarationName": "Jane Doe",
                "declarationDesignation": "Director",
                "declarationAgreed": True
            }
        }
        
        submit_response = requests.post(
            f"{BASE_URL}/api/application-forms/{form_id}/submit",
            headers={"Authorization": f"Bearer {client_token}"},
            json=submit_data
        )
        assert submit_response.status_code == 200
        submitted_data = submit_response.json()
        assert submitted_data["status"] == "submitted"
        assert submitted_data["submitted_at"] is not None
    
    def test_submit_without_declaration_fails(self, admin_token, client_token, client_id):
        """Test that submitting without declaration agreement fails"""
        # First create a form as admin
        create_response = requests.post(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"client_id": client_id}
        )
        assert create_response.status_code == 200
        form_id = create_response.json()["id"]
        
        # Try to submit without declaration
        submit_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": "TEST_No Declaration Company",
                "address": "123 Test Street",
                "phoneNumber": "+966 12 345 6789",
                "website": "",
                "email": "test@company.com",
                "contactPerson": "Test Person",
                "designation": "Manager",
                "mobileNumber": "+966 50 123 4567",
                "contactEmail": "test@company.com",
                "legalStatus": "private",
                "certificationSchemes": ["ISO9001"],
                "certificationProgram": "initial",
                "combinedAudit": "",
                "combinedAuditSpecification": "",
                "isInternalAuditCombined": "",
                "isMRMCombined": "",
                "isManualProceduresCombined": "",
                "isSystemIntegrated": "",
                "numberOfSites": 1,
                "site1Address": "123 Test Street",
                "site2Address": "",
                "totalEmployees": "50",
                "locationShifts": "",
                "fullTimeEmployees": "",
                "partTimeEmployees": "",
                "temporaryEmployees": "",
                "unskilledWorkers": "",
                "remoteEmployees": "",
                "isAlreadyCertified": "no",
                "currentCertifications": [],
                "isConsultantInvolved": "no",
                "consultantName": "",
                "transferReason": "",
                "currentCertificateExpiry": "",
                "keyBusinessProcesses": "Testing",
                "hasEnvironmentAspectRegister": "",
                "hasEnvironmentalManual": "",
                "hasEnvironmentalAuditProgram": "",
                "numberOfHACCPStudies": "",
                "numberOfProcessLines": "",
                "processingType": "",
                "hazardsIdentified": "",
                "criticalRisks": "",
                "annualEnergyConsumption": "",
                "numberOfEnergySources": "",
                "numberOfSEUs": "",
                "productsInRange": "",
                "medicalDeviceTypes": [],
                "sterilizationType": "",
                "numberOfDeviceFiles": "",
                "applicableLegislations": "",
                "exportCountries": "",
                "productStandards": "",
                "intendedUse": "",
                "outsourceProcesses": "",
                "businessComplexity": "",
                "processStandard": "",
                "managementSystemLevel": "",
                "itEnvironmentComplexity": "",
                "outsourcingDependency": "",
                "systemDevelopment": "",
                "declarationName": "",
                "declarationDesignation": "",
                "declarationAgreed": False  # Not agreed
            }
        }
        
        submit_response = requests.post(
            f"{BASE_URL}/api/application-forms/{form_id}/submit",
            headers={"Authorization": f"Bearer {client_token}"},
            json=submit_data
        )
        assert submit_response.status_code == 400


class TestLegacyForms:
    """Legacy form endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Client authentication failed")
    
    def test_get_forms_as_admin(self, admin_token):
        """Test admin getting all forms"""
        response = requests.get(
            f"{BASE_URL}/api/forms",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_forms_as_client(self, client_token):
        """Test client getting their forms"""
        response = requests.get(
            f"{BASE_URL}/api/forms",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestQuotations:
    """Quotation endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Client authentication failed")
    
    def test_get_quotations_as_admin(self, admin_token):
        """Test admin getting all quotations"""
        response = requests.get(
            f"{BASE_URL}/api/quotations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_quotations_as_client(self, client_token):
        """Test client getting their quotations"""
        response = requests.get(
            f"{BASE_URL}/api/quotations",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestContracts:
    """Contract endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    @pytest.fixture
    def client_token(self):
        """Get client authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CLIENT_CREDENTIALS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Client authentication failed")
    
    def test_get_contracts_as_admin(self, admin_token):
        """Test admin getting all contracts"""
        response = requests.get(
            f"{BASE_URL}/api/contracts",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_contracts_as_client(self, client_token):
        """Test client getting their contracts"""
        response = requests.get(
            f"{BASE_URL}/api/contracts",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
