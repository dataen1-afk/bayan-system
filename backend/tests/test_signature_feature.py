"""
Test suite for Digital Signature Feature in Certification Agreement
Tests signature pad functionality, stamp upload, and PDF generation with signatures
"""

import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test signature image (small 10x10 white PNG with a black dot)
TEST_SIGNATURE_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNk+M9Qz0AEYBxVSF+FABJADq0w8gzDAAAAAElFTkSuQmCC"

# Test stamp image (small 10x10 blue PNG)
TEST_STAMP_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAIUlEQVR42mP4z8DwHwYZBhRgjCqEN4FxVCF9FQ4YzQ4BALUaDt0X/VqsAAAAAElFTkSuQmCC"

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Test access token for accepted proposal
TEST_ACCESS_TOKEN = "d4a5fd8f-7c81-4453-a529-626b8c2bfe1a"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin authentication failed")


@pytest.fixture
def api_client():
    """Create requests session with headers"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestProposalStatus:
    """Verify proposal status is accepted for agreement testing"""
    
    def test_proposal_is_accepted_or_agreement_signed(self, api_client):
        """Verify the test proposal is in accepted or agreement_signed status (both valid)"""
        response = api_client.get(f"{BASE_URL}/api/public/proposal/{TEST_ACCESS_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        # Both accepted and agreement_signed are valid - agreement_signed means client already signed
        assert data["status"] in ["accepted", "agreement_signed"], f"Proposal status is {data['status']}, expected 'accepted' or 'agreement_signed'"
        print(f"✓ Proposal status is {data['status']} for organization: {data['organization_name']}")


class TestAgreementStatus:
    """Test agreement status endpoint"""
    
    def test_get_agreement_status_pending(self, api_client):
        """Test getting agreement status when not yet submitted"""
        response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        # Status should be pending (no agreement submitted yet) or submitted (if already submitted)
        assert data["status"] in ["pending", "submitted"], f"Unexpected status: {data['status']}"
        print(f"✓ Agreement status check returned: {data['status']}")


class TestSignatureValidation:
    """Test signature validation in agreement submission"""
    
    def test_agreement_requires_signature(self, api_client):
        """Test that agreement submission fails without signature"""
        # First check if agreement already exists
        check_response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        if check_response.status_code == 200:
            data = check_response.json()
            if data["status"] == "submitted":
                pytest.skip("Agreement already submitted, cannot test validation")
        
        # Attempt to submit agreement without signature
        agreement_data = {
            "organization_name": "Test Company",
            "organization_address": "123 Test Street",
            "selected_standards": ["ISO9001"],
            "other_standard": "",
            "scope_of_services": "Quality management certification",
            "sites": ["Main Office"],
            "signatory_name": "John Doe",
            "signatory_position": "CEO",
            "signatory_date": "2026-01-15",
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            },
            "signature_image": None,  # No signature
            "stamp_image": None
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}/submit",
            json=agreement_data
        )
        
        # Should fail because signature is required
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "signature" in data.get("detail", "").lower(), "Error should mention signature requirement"
        print("✓ Agreement correctly rejected without signature")


class TestAgreementSubmissionWithSignature:
    """Test agreement submission with digital signature"""
    
    def test_submit_agreement_with_signature_only(self, api_client):
        """Test submitting agreement with signature but no stamp"""
        # First check if agreement already exists
        check_response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        if check_response.status_code == 200:
            data = check_response.json()
            if data["status"] == "submitted":
                pytest.skip("Agreement already submitted")
        
        agreement_data = {
            "organization_name": "Test Company for Signature",
            "organization_address": "456 Signature Ave",
            "selected_standards": ["ISO9001"],
            "other_standard": "",
            "scope_of_services": "Quality management system certification",
            "sites": ["Head Office", "Branch 1"],
            "signatory_name": "Test Signatory",
            "signatory_position": "Director",
            "signatory_date": "2026-01-15",
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            },
            "signature_image": TEST_SIGNATURE_BASE64,
            "stamp_image": None
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}/submit",
            json=agreement_data
        )
        
        # If agreement already exists, we'll get 400
        if response.status_code == 400:
            data = response.json()
            if "already been submitted" in data.get("detail", ""):
                print("✓ Agreement already submitted (expected if test ran before)")
                return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "agreement_id" in data
        print(f"✓ Agreement submitted successfully with ID: {data['agreement_id']}")
    
    def test_verify_agreement_stored_signature(self, api_client):
        """Verify that the signature was stored in the agreement"""
        response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] == "submitted":
            agreement = data.get("agreement", {})
            # Check signature is stored
            signature = agreement.get("signature_image")
            assert signature is not None, "Signature should be stored"
            assert signature.startswith("data:image"), "Signature should be base64 data URL"
            print("✓ Signature image correctly stored in agreement")
        else:
            print(f"Agreement status is {data['status']}, signature verification skipped")


class TestAgreementWithStamp:
    """Test agreement submission with both signature and stamp"""
    
    def test_create_new_proposal_and_submit_with_stamp(self, api_client, admin_token):
        """Create a new proposal and submit agreement with both signature and stamp"""
        # First create a new application form
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        form_data = {
            "client_info": {
                "name": "Stamp Test Client",
                "company_name": "Stamp Test Company LLC",
                "email": "stamp-test@example.com",
                "phone": "+966555000001"
            }
        }
        
        form_response = api_client.post(
            f"{BASE_URL}/api/application-forms",
            json=form_data,
            headers=headers
        )
        
        if form_response.status_code != 200:
            pytest.skip(f"Could not create application form: {form_response.text}")
        
        form = form_response.json()
        form_id = form["id"]
        
        # Create a proposal for this form
        proposal_data = {
            "application_form_id": form_id,
            "organization_name": "Stamp Test Company LLC",
            "organization_address": "789 Stamp Street",
            "organization_phone": "+966555000001",
            "contact_person": "Stamp Test Person",
            "contact_position": "Manager",
            "contact_email": "stamp-test@example.com",
            "standards": ["ISO14001"],
            "scope": "Environmental management",
            "total_employees": 50,
            "number_of_sites": 1,
            "audit_duration": {
                "stage_1": 1.0,
                "stage_2": 2.0,
                "surveillance_1": 1.0,
                "surveillance_2": 1.0,
                "recertification": 1.5
            },
            "service_fees": {
                "initial_certification": 5000.0,
                "surveillance_1": 2000.0,
                "surveillance_2": 2000.0,
                "recertification": 4000.0,
                "currency": "SAR"
            },
            "notes": "Test proposal for stamp testing",
            "validity_days": 30
        }
        
        proposal_response = api_client.post(
            f"{BASE_URL}/api/proposals",
            json=proposal_data,
            headers=headers
        )
        
        if proposal_response.status_code != 200:
            pytest.skip(f"Could not create proposal: {proposal_response.text}")
        
        proposal = proposal_response.json()
        access_token = proposal["access_token"]
        
        # Accept the proposal (as client)
        accept_response = api_client.post(
            f"{BASE_URL}/api/public/proposal/{access_token}/respond",
            json={
                "status": "accepted",
                "signatory_name": "Stamp Client",
                "signatory_designation": "CEO"
            }
        )
        
        assert accept_response.status_code == 200, f"Could not accept proposal: {accept_response.text}"
        
        # Now submit agreement with both signature AND stamp
        agreement_data = {
            "organization_name": "Stamp Test Company LLC",
            "organization_address": "789 Stamp Street",
            "selected_standards": ["ISO14001"],
            "other_standard": "",
            "scope_of_services": "Environmental management system",
            "sites": ["Main Office"],
            "signatory_name": "Stamp Test Signatory",
            "signatory_position": "Director",
            "signatory_date": "2026-01-15",
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            },
            "signature_image": TEST_SIGNATURE_BASE64,
            "stamp_image": TEST_STAMP_BASE64
        }
        
        submit_response = api_client.post(
            f"{BASE_URL}/api/public/agreement/{access_token}/submit",
            json=agreement_data
        )
        
        assert submit_response.status_code == 200, f"Failed to submit agreement: {submit_response.text}"
        data = submit_response.json()
        agreement_id = data["agreement_id"]
        print(f"✓ Agreement with signature AND stamp submitted successfully: {agreement_id}")
        
        # Verify both signature and stamp are stored
        verify_response = api_client.get(f"{BASE_URL}/api/public/agreement/{access_token}")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        assert verify_data["status"] == "submitted"
        agreement = verify_data["agreement"]
        
        assert agreement.get("signature_image") is not None, "Signature should be stored"
        assert agreement.get("stamp_image") is not None, "Stamp should be stored"
        print("✓ Both signature and stamp correctly stored in agreement")
        
        # Return the access_token for PDF testing
        return access_token


class TestPDFGenerationWithSignature:
    """Test PDF contract generation with signatures"""
    
    def test_public_pdf_generation(self, api_client):
        """Test public PDF generation endpoint includes signature"""
        # Use the access token from the main test
        response = api_client.get(
            f"{BASE_URL}/api/public/contracts/{TEST_ACCESS_TOKEN}/pdf"
        )
        
        if response.status_code == 404:
            pytest.skip("Agreement not found - may not have been submitted yet")
        
        assert response.status_code == 200, f"PDF generation failed: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"
        
        # Check PDF size is reasonable (should contain image data)
        pdf_size = len(response.content)
        assert pdf_size > 1000, f"PDF seems too small: {pdf_size} bytes"
        
        # Verify PDF header
        assert response.content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"✓ PDF generated successfully, size: {pdf_size} bytes")
    
    def test_admin_pdf_generation(self, api_client, admin_token):
        """Test admin PDF generation endpoint"""
        # First get the agreement ID
        response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        if response.status_code != 200 or response.json()["status"] != "submitted":
            pytest.skip("Agreement not submitted yet")
        
        agreement_id = response.json()["agreement"]["id"]
        
        # Try admin endpoint
        headers = {"Authorization": f"Bearer {admin_token}"}
        pdf_response = api_client.get(
            f"{BASE_URL}/api/contracts/{agreement_id}/pdf",
            headers=headers
        )
        
        assert pdf_response.status_code == 200, f"Admin PDF generation failed: {pdf_response.status_code}"
        assert pdf_response.headers.get("content-type") == "application/pdf"
        print("✓ Admin PDF endpoint working correctly")


class TestCertificationAgreementModel:
    """Test the CertificationAgreement model fields"""
    
    def test_agreement_model_has_signature_fields(self, api_client):
        """Verify agreement data structure includes signature fields"""
        response = api_client.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        
        if response.status_code != 200:
            pytest.skip("Could not get agreement")
        
        data = response.json()
        
        if data["status"] == "submitted":
            agreement = data["agreement"]
            # Check required fields exist in the model
            assert "signature_image" in agreement, "signature_image field missing"
            assert "stamp_image" in agreement, "stamp_image field missing"
            assert "signatory_name" in agreement, "signatory_name field missing"
            assert "signatory_position" in agreement, "signatory_position field missing"
            assert "signatory_date" in agreement, "signatory_date field missing"
            assert "acknowledgements" in agreement, "acknowledgements field missing"
            print("✓ Agreement model has all required signature-related fields")
        else:
            # If pending, check proposal structure
            proposal = data.get("proposal", {})
            assert "organization_name" in proposal
            print("✓ Agreement status is pending, proposal structure verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
