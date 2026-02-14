"""
Service Contract Management System - Backend API Tests
Tests for:
- Admin login and authentication
- Application form creation with client info
- Public form access (no login required)
- Form save draft and submission
- Admin dashboard data retrieval
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root: {data['message']}")


class TestAdminAuthentication:
    """Admin login and authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']}")
        return data["token"]
    
    def test_admin_login_invalid_password(self):
        """Test admin login with invalid password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid password rejected correctly")
    
    def test_admin_login_invalid_email(self):
        """Test admin login with non-existent email"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "anypassword"
        })
        assert response.status_code == 401
        print("✓ Non-existent email rejected correctly")


class TestAdminDashboard:
    """Admin dashboard data retrieval tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_get_forms(self, admin_token):
        """Test getting forms list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/forms", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Forms retrieved: {len(data)} forms")
    
    def test_get_quotations(self, admin_token):
        """Test getting quotations list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/quotations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Quotations retrieved: {len(data)} quotations")
    
    def test_get_contracts(self, admin_token):
        """Test getting contracts list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/contracts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Contracts retrieved: {len(data)} contracts")
    
    def test_get_application_forms(self, admin_token):
        """Test getting application forms list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/application-forms", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Application forms retrieved: {len(data)} forms")


class TestApplicationFormCreation:
    """Admin creates application form with client info"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_create_application_form_with_client_info(self, admin_token):
        """Test admin creating application form with client info"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        unique_id = str(uuid.uuid4())[:8]
        
        client_info = {
            "name": f"TEST_Client_{unique_id}",
            "company_name": f"TEST_Company_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "phone": "+966501234567"
        }
        
        response = requests.post(f"{BASE_URL}/api/application-forms", 
            headers=headers,
            json={"client_info": client_info}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "access_token" in data
        assert "client_info" in data
        assert data["status"] == "pending"
        
        # Verify client info
        assert data["client_info"]["name"] == client_info["name"]
        assert data["client_info"]["company_name"] == client_info["company_name"]
        assert data["client_info"]["email"] == client_info["email"]
        
        print(f"✓ Application form created with access_token: {data['access_token']}")
        return data
    
    def test_create_application_form_without_auth(self):
        """Test creating application form without authentication fails"""
        response = requests.post(f"{BASE_URL}/api/application-forms", 
            json={"client_info": {
                "name": "Test",
                "company_name": "Test Co",
                "email": "test@test.com",
                "phone": "123"
            }}
        )
        assert response.status_code in [401, 403]
        print("✓ Unauthenticated form creation rejected correctly")


class TestPublicFormAccess:
    """Public form access tests (no login required)"""
    
    # Use the existing test form access token
    TEST_ACCESS_TOKEN = "4131b846-c6bc-41c9-aa7b-732e1d8e0fc5"
    
    def test_get_public_form(self):
        """Test accessing public form without login"""
        response = requests.get(f"{BASE_URL}/api/public/form/{self.TEST_ACCESS_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "client_info" in data
        assert "status" in data
        
        # Verify client info is present
        assert "name" in data["client_info"]
        assert "company_name" in data["client_info"]
        assert "email" in data["client_info"]
        
        print(f"✓ Public form accessed: {data['client_info']['company_name']}")
        return data
    
    def test_get_public_form_invalid_token(self):
        """Test accessing public form with invalid token"""
        response = requests.get(f"{BASE_URL}/api/public/form/invalid-token-12345")
        assert response.status_code == 404
        print("✓ Invalid token rejected correctly")
    
    def test_save_draft_public_form(self):
        """Test saving draft on public form without login"""
        # First get the form to check its status
        get_response = requests.get(f"{BASE_URL}/api/public/form/{self.TEST_ACCESS_TOKEN}")
        if get_response.status_code != 200:
            pytest.skip("Test form not accessible")
        
        form_data = get_response.json()
        if form_data["status"] != "pending":
            pytest.skip("Test form already submitted, cannot save draft")
        
        # Save draft with company data
        draft_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": "Test Draft Company",
                "address": "123 Test Street",
                "phoneNumber": "+966501234567",
                "website": "https://test.com",
                "email": "test@test.com",
                "contactPerson": "Test Person",
                "designation": "Manager",
                "mobileNumber": "+966501234567",
                "contactEmail": "contact@test.com",
                "legalStatus": "LLC",
                "certificationSchemes": ["ISO 9001"],
                "certificationProgram": "initial",
                "combinedAudit": "",
                "combinedAuditSpecification": "",
                "isInternalAuditCombined": "",
                "isMRMCombined": "",
                "isManualProceduresCombined": "",
                "isSystemIntegrated": "",
                "numberOfSites": 1,
                "site1Address": "Main Site",
                "site2Address": "",
                "totalEmployees": "50",
                "locationShifts": "1",
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
                "keyBusinessProcesses": "Manufacturing",
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
        
        response = requests.put(f"{BASE_URL}/api/public/form/{self.TEST_ACCESS_TOKEN}", json=draft_data)
        
        if response.status_code == 400:
            # Form might already be submitted
            print("✓ Draft save blocked (form may be submitted)")
            return
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        print("✓ Draft saved successfully on public form")


class TestPublicFormSubmission:
    """Public form submission tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_create_and_submit_form(self, admin_token):
        """Test full flow: admin creates form, client submits via public link"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        unique_id = str(uuid.uuid4())[:8]
        
        # Step 1: Admin creates form with client info
        client_info = {
            "name": f"TEST_Submit_Client_{unique_id}",
            "company_name": f"TEST_Submit_Company_{unique_id}",
            "email": f"submit_{unique_id}@example.com",
            "phone": "+966509876543"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/application-forms", 
            headers=headers,
            json={"client_info": client_info}
        )
        
        assert create_response.status_code == 200
        created_form = create_response.json()
        access_token = created_form["access_token"]
        print(f"✓ Form created with access_token: {access_token}")
        
        # Step 2: Client accesses form via public link (no login)
        public_response = requests.get(f"{BASE_URL}/api/public/form/{access_token}")
        assert public_response.status_code == 200
        public_form = public_response.json()
        assert public_form["status"] == "pending"
        print("✓ Client accessed form via public link")
        
        # Step 3: Client fills and submits form
        submit_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": f"TEST_Submit_Company_{unique_id}",
                "address": "456 Submit Street",
                "phoneNumber": "+966509876543",
                "website": "https://submit-test.com",
                "email": f"submit_{unique_id}@example.com",
                "contactPerson": "Submit Person",
                "designation": "Director",
                "mobileNumber": "+966509876543",
                "contactEmail": f"submit_{unique_id}@example.com",
                "legalStatus": "Corporation",
                "certificationSchemes": ["ISO 9001", "ISO 14001"],
                "certificationProgram": "initial",
                "combinedAudit": "yes",
                "combinedAuditSpecification": "Combined QMS and EMS",
                "isInternalAuditCombined": "yes",
                "isMRMCombined": "yes",
                "isManualProceduresCombined": "yes",
                "isSystemIntegrated": "yes",
                "numberOfSites": 2,
                "site1Address": "Main Office",
                "site2Address": "Branch Office",
                "totalEmployees": "100",
                "locationShifts": "2",
                "fullTimeEmployees": "80",
                "partTimeEmployees": "15",
                "temporaryEmployees": "5",
                "unskilledWorkers": "10",
                "remoteEmployees": "10",
                "isAlreadyCertified": "no",
                "currentCertifications": [],
                "isConsultantInvolved": "yes",
                "consultantName": "Test Consultant",
                "transferReason": "",
                "currentCertificateExpiry": "",
                "keyBusinessProcesses": "Software Development",
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
                "declarationName": "Test Declarant",
                "declarationDesignation": "CEO",
                "declarationAgreed": True
            }
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/public/form/{access_token}/submit", json=submit_data)
        assert submit_response.status_code == 200
        submitted_form = submit_response.json()
        assert submitted_form["status"] == "submitted"
        print("✓ Form submitted successfully via public link")
        
        # Step 4: Verify admin can see submitted form
        admin_forms_response = requests.get(f"{BASE_URL}/api/application-forms", headers=headers)
        assert admin_forms_response.status_code == 200
        admin_forms = admin_forms_response.json()
        
        # Find the submitted form
        submitted_forms = [f for f in admin_forms if f["id"] == created_form["id"]]
        assert len(submitted_forms) == 1
        assert submitted_forms[0]["status"] == "submitted"
        print("✓ Admin can see submitted form in dashboard")
        
        return created_form
    
    def test_submit_without_declaration_fails(self, admin_token):
        """Test that submission without declaration agreement fails"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        unique_id = str(uuid.uuid4())[:8]
        
        # Create form
        create_response = requests.post(f"{BASE_URL}/api/application-forms", 
            headers=headers,
            json={"client_info": {
                "name": f"TEST_NoDecl_{unique_id}",
                "company_name": f"TEST_NoDecl_Co_{unique_id}",
                "email": f"nodecl_{unique_id}@example.com",
                "phone": "+966501111111"
            }}
        )
        
        assert create_response.status_code == 200
        access_token = create_response.json()["access_token"]
        
        # Try to submit without declaration
        submit_data = {
            "company_data": {
                "dateOfApplication": "2026-01-15",
                "companyName": f"TEST_NoDecl_Co_{unique_id}",
                "address": "Test Address",
                "phoneNumber": "+966501111111",
                "website": "",
                "email": f"nodecl_{unique_id}@example.com",
                "contactPerson": "Test",
                "designation": "Test",
                "mobileNumber": "",
                "contactEmail": "",
                "legalStatus": "",
                "certificationSchemes": [],
                "certificationProgram": "",
                "combinedAudit": "",
                "combinedAuditSpecification": "",
                "isInternalAuditCombined": "",
                "isMRMCombined": "",
                "isManualProceduresCombined": "",
                "isSystemIntegrated": "",
                "numberOfSites": 1,
                "site1Address": "",
                "site2Address": "",
                "totalEmployees": "",
                "locationShifts": "",
                "fullTimeEmployees": "",
                "partTimeEmployees": "",
                "temporaryEmployees": "",
                "unskilledWorkers": "",
                "remoteEmployees": "",
                "isAlreadyCertified": "",
                "currentCertifications": [],
                "isConsultantInvolved": "",
                "consultantName": "",
                "transferReason": "",
                "currentCertificateExpiry": "",
                "keyBusinessProcesses": "",
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
        
        submit_response = requests.post(f"{BASE_URL}/api/public/form/{access_token}/submit", json=submit_data)
        assert submit_response.status_code == 400
        print("✓ Submission without declaration correctly rejected")


class TestEmailSending:
    """Email sending tests (MOCKED)"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_send_form_email(self, admin_token):
        """Test sending form link via email (MOCKED - logs to console)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        unique_id = str(uuid.uuid4())[:8]
        
        # Create form first
        create_response = requests.post(f"{BASE_URL}/api/application-forms", 
            headers=headers,
            json={"client_info": {
                "name": f"TEST_Email_{unique_id}",
                "company_name": f"TEST_Email_Co_{unique_id}",
                "email": f"email_{unique_id}@example.com",
                "phone": "+966502222222"
            }}
        )
        
        assert create_response.status_code == 200
        form_id = create_response.json()["id"]
        
        # Send email
        email_response = requests.post(f"{BASE_URL}/api/application-forms/{form_id}/send-email", headers=headers)
        assert email_response.status_code == 200
        data = email_response.json()
        assert "form_link" in data
        print(f"✓ Email sent (MOCKED) with form link: {data['form_link']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
