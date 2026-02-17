"""
Iteration 16: Full E2E Workflow Test for Service Contract Management System
Tests the complete workflow: Admin login -> Create Form -> Client Fill -> Admin Quote -> Client Accept -> Agreement -> PDF
"""

import pytest
import requests
import os
import json
import time
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://grant-cert-manager.preview.emergentagent.com"

API_URL = f"{BASE_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Store test data
test_data = {
    "admin_token": None,
    "application_form_id": None,
    "application_form_access_token": None,
    "proposal_id": None,
    "proposal_access_token": None,
    "agreement_id": None,
}


class TestBackendHealth:
    """Test API health endpoints"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{API_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root responds: {data['message']}")


class TestAdminAuth:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        
        test_data["admin_token"] = data["token"]
        print(f"✓ Admin login successful: {data['user']['name']}")
    
    def test_admin_login_invalid_password(self):
        """Test admin login with wrong password"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid password correctly rejected")
    
    def test_auth_me_endpoint(self):
        """Test authenticated user info endpoint"""
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        print("✓ Auth me endpoint works")


class TestAdminDashboard:
    """Test admin dashboard data retrieval"""
    
    def test_get_application_forms(self):
        """Test getting application forms list"""
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{API_URL}/application-forms", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} application forms")
    
    def test_get_proposals(self):
        """Test getting proposals list"""
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{API_URL}/proposals", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} proposals")
    
    def test_get_contracts(self):
        """Test getting contracts list"""
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{API_URL}/contracts", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} contracts")


class TestFullWorkflow:
    """Test the complete workflow from form creation to contract PDF"""
    
    def test_01_admin_creates_application_form(self):
        """Step 1: Admin creates application form for a client"""
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        
        # Create new application form with client info
        timestamp = int(time.time())
        client_info = {
            "name": f"TEST_John Smith_{timestamp}",
            "company_name": f"TEST_Acme Corporation_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "phone": "+966500000000"
        }
        
        response = requests.post(
            f"{API_URL}/application-forms",
            headers=headers,
            json={"client_info": client_info}
        )
        
        assert response.status_code == 200, f"Failed to create form: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "access_token" in data
        assert data["status"] == "pending"
        
        test_data["application_form_id"] = data["id"]
        test_data["application_form_access_token"] = data["access_token"]
        
        print(f"✓ Application form created: {data['id'][:8]}")
        print(f"  Access token: {data['access_token'][:8]}...")
    
    def test_02_public_form_accessible(self):
        """Step 2: Public form link works without login"""
        if not test_data["application_form_access_token"]:
            pytest.skip("No form access token available")
        
        token = test_data["application_form_access_token"]
        response = requests.get(f"{API_URL}/public/form/{token}")
        
        assert response.status_code == 200, f"Public form not accessible: {response.text}"
        
        data = response.json()
        assert "client_info" in data
        assert data["status"] == "pending"
        print(f"✓ Public form accessible: Company = {data['client_info']['company_name'][:20]}...")
    
    def test_03_client_submits_form(self):
        """Step 3: Client fills and submits the form"""
        if not test_data["application_form_access_token"]:
            pytest.skip("No form access token available")
        
        token = test_data["application_form_access_token"]
        
        # Submit form with company data
        company_data = {
            "dateOfApplication": datetime.now().strftime("%Y-%m-%d"),
            "companyName": "TEST Acme Corporation",
            "address": "123 Test Street, Riyadh",
            "phoneNumber": "+966500000000",
            "email": "test@example.com",
            "contactPerson": "John Smith",
            "designation": "Quality Manager",
            "certificationSchemes": ["ISO9001", "ISO14001"],
            "certificationProgram": "initial",
            "numberOfSites": 1,
            "totalEmployees": "50",
            "declarationName": "John Smith",
            "declarationDesignation": "CEO",
            "declarationAgreed": True
        }
        
        response = requests.post(
            f"{API_URL}/public/form/{token}/submit",
            json={"company_data": company_data}
        )
        
        assert response.status_code == 200, f"Form submission failed: {response.text}"
        
        data = response.json()
        assert data["status"] == "submitted"
        print("✓ Client form submitted successfully")
    
    def test_04_admin_sees_submitted_form(self):
        """Step 4: Admin sees submitted form with audit calculation"""
        if not test_data["admin_token"] or not test_data["application_form_id"]:
            pytest.skip("Missing admin token or form ID")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        form_id = test_data["application_form_id"]
        
        response = requests.get(f"{API_URL}/application-forms/{form_id}", headers=headers)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "submitted"
        
        # Check if audit calculation is present
        if data.get("audit_calculation"):
            print(f"✓ Admin sees submitted form with audit calculation")
            print(f"  Calculated audit days: {data['audit_calculation'].get('final_total_md', 'N/A')}")
        else:
            print("✓ Admin sees submitted form (no audit calculation - may be due to cert selection)")
    
    def test_05_admin_creates_proposal(self):
        """Step 5: Admin creates a proposal/quotation from the form"""
        if not test_data["admin_token"] or not test_data["application_form_id"]:
            pytest.skip("Missing admin token or form ID")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        
        proposal_data = {
            "application_form_id": test_data["application_form_id"],
            "organization_name": "TEST Acme Corporation",
            "organization_address": "123 Test Street, Riyadh, Saudi Arabia",
            "organization_phone": "+966500000000",
            "contact_person": "John Smith",
            "contact_position": "Quality Manager",
            "contact_email": "john@acme.com",
            "standards": ["ISO9001", "ISO14001"],
            "scope": "Manufacturing of electronic components",
            "total_employees": 50,
            "number_of_sites": 1,
            "audit_duration": {
                "stage_1": 1.0,
                "stage_2": 2.0,
                "surveillance_1": 1.0,
                "surveillance_2": 1.0,
                "recertification": 2.0
            },
            "service_fees": {
                "initial_certification": 15000.0,
                "surveillance_1": 5000.0,
                "surveillance_2": 5000.0,
                "recertification": 10000.0,
                "currency": "SAR"
            },
            "notes": "Test proposal for workflow verification",
            "validity_days": 30
        }
        
        response = requests.post(
            f"{API_URL}/proposals",
            headers=headers,
            json=proposal_data
        )
        
        assert response.status_code == 200, f"Failed to create proposal: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "access_token" in data
        assert data["total_amount"] == 35000.0
        
        test_data["proposal_id"] = data["id"]
        test_data["proposal_access_token"] = data["access_token"]
        
        print(f"✓ Proposal created: {data['id'][:8]}")
        print(f"  Total amount: {data['total_amount']} SAR")
    
    def test_06_public_proposal_accessible(self):
        """Step 6: Public proposal link works"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        response = requests.get(f"{API_URL}/public/proposal/{token}")
        
        assert response.status_code == 200, f"Public proposal not accessible: {response.text}"
        
        data = response.json()
        assert data["status"] == "pending"
        assert data["total_amount"] == 35000.0
        print(f"✓ Public proposal accessible: {data['organization_name']}")
    
    def test_07_client_accepts_proposal(self):
        """Step 7: Client accepts the proposal"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        
        response = requests.post(
            f"{API_URL}/public/proposal/{token}/respond",
            json={
                "status": "accepted",
                "signatory_name": "John Smith",
                "signatory_designation": "CEO"
            }
        )
        
        assert response.status_code == 200, f"Failed to accept proposal: {response.text}"
        print("✓ Client accepted the proposal")
    
    def test_08_agreement_page_accessible(self):
        """Step 8: Certification Agreement page accessible after acceptance"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        
        # Get agreement status
        response = requests.get(f"{API_URL}/public/agreement/{token}")
        
        # Should be accessible (either pending or not yet submitted)
        assert response.status_code in [200, 400], f"Agreement endpoint error: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Agreement page accessible, status: {data.get('status', 'pending')}")
        else:
            print("✓ Agreement page ready for submission")
    
    def test_09_client_submits_agreement(self):
        """Step 9: Client fills and submits the certification agreement"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        
        # Create a simple base64 signature placeholder (1x1 white PNG)
        signature_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        stamp_base64 = signature_base64  # Same placeholder for testing
        
        agreement_data = {
            "organization_name": "TEST Acme Corporation",
            "organization_address": "123 Test Street, Riyadh, Saudi Arabia",
            "selected_standards": ["ISO9001", "ISO14001"],
            "other_standard": "",
            "scope_of_services": "Manufacturing of electronic components",
            "sites": ["Head Office - 123 Test Street, Riyadh"],
            "signatory_name": "John Smith",
            "signatory_position": "CEO",
            "signatory_date": datetime.now().strftime("%Y-%m-%d"),
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            },
            "signature_image": signature_base64,
            "stamp_image": stamp_base64
        }
        
        response = requests.post(
            f"{API_URL}/public/agreement/{token}/submit",
            json=agreement_data
        )
        
        assert response.status_code == 200, f"Failed to submit agreement: {response.text}"
        
        data = response.json()
        assert "agreement_id" in data
        test_data["agreement_id"] = data["agreement_id"]
        
        print(f"✓ Agreement submitted: {data['agreement_id'][:8]}")
    
    def test_10_admin_can_download_pdf(self):
        """Step 10: Admin can download the contract PDF"""
        if not test_data["admin_token"] or not test_data["agreement_id"]:
            pytest.skip("Missing admin token or agreement ID")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        agreement_id = test_data["agreement_id"]
        
        # Test standard PDF endpoint
        response = requests.get(
            f"{API_URL}/contracts/{agreement_id}/pdf",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to get PDF: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000  # PDF should have some content
        
        print(f"✓ Standard PDF generated: {len(response.content)} bytes")
    
    def test_11_admin_can_download_bilingual_pdf(self):
        """Step 11: Admin can download the bilingual contract PDF"""
        if not test_data["admin_token"] or not test_data["agreement_id"]:
            pytest.skip("Missing admin token or agreement ID")
        
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        agreement_id = test_data["agreement_id"]
        
        # Test bilingual PDF endpoint
        response = requests.get(
            f"{API_URL}/contracts/{agreement_id}/pdf/bilingual",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to get bilingual PDF: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000  # PDF should have some content
        
        print(f"✓ Bilingual PDF generated: {len(response.content)} bytes")
    
    def test_12_public_can_download_pdf(self):
        """Step 12: Public PDF endpoint works"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        
        # Test public PDF endpoint
        response = requests.get(f"{API_URL}/public/contracts/{token}/pdf")
        
        assert response.status_code == 200, f"Public PDF not accessible: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        
        print(f"✓ Public PDF endpoint works: {len(response.content)} bytes")
    
    def test_13_public_can_download_bilingual_pdf(self):
        """Step 13: Public bilingual PDF endpoint works"""
        if not test_data["proposal_access_token"]:
            pytest.skip("No proposal access token available")
        
        token = test_data["proposal_access_token"]
        
        # Test public bilingual PDF endpoint
        response = requests.get(f"{API_URL}/public/contracts/{token}/pdf/bilingual")
        
        assert response.status_code == 200, f"Public bilingual PDF not accessible: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        
        print(f"✓ Public bilingual PDF endpoint works: {len(response.content)} bytes")


class TestCleanup:
    """Cleanup test data (optional)"""
    
    def test_verify_workflow_complete(self):
        """Verify all test data was created successfully"""
        print("\n=== Workflow Test Summary ===")
        print(f"Application Form ID: {test_data.get('application_form_id', 'N/A')[:8]}...")
        print(f"Proposal ID: {test_data.get('proposal_id', 'N/A')[:8]}...")
        print(f"Agreement ID: {test_data.get('agreement_id', 'N/A')[:8]}...")
        
        # All should be created
        assert test_data.get("application_form_id"), "Application form was not created"
        assert test_data.get("proposal_id"), "Proposal was not created"
        assert test_data.get("agreement_id"), "Agreement was not created"
        
        print("✓ Full E2E workflow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
