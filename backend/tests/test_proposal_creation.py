"""
Test Proposal Creation with Signature and Stamp Images
Tests the POST /api/proposals endpoint for creating proposals with large base64 images
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProposalCreation:
    """Test proposal creation with signature and stamp images"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_default_signatory(self):
        """Test GET /api/defaults/signatory returns signature and stamp"""
        response = requests.get(f"{BASE_URL}/api/defaults/signatory")
        assert response.status_code == 200
        
        data = response.json()
        assert "issuer_name" in data
        assert "issuer_designation" in data
        assert "issuer_signature" in data
        assert "issuer_stamp" in data
        
        # Verify signature and stamp are base64 data URIs
        assert data["issuer_signature"].startswith("data:image/png;base64,"), "Signature should be base64 data URI"
        assert data["issuer_stamp"].startswith("data:image/png;base64,"), "Stamp should be base64 data URI"
        
        # Verify images have significant size (not empty)
        sig_len = len(data["issuer_signature"])
        stamp_len = len(data["issuer_stamp"])
        assert sig_len > 1000, f"Signature too small: {sig_len} chars"
        assert stamp_len > 1000, f"Stamp too small: {stamp_len} chars"
        
        print(f"Signature size: {sig_len} chars")
        print(f"Stamp size: {stamp_len} chars")
    
    def test_create_proposal_with_valid_data(self, auth_headers):
        """Test creating a proposal with all required fields including signature/stamp"""
        # Get signatory defaults
        defaults_response = requests.get(f"{BASE_URL}/api/defaults/signatory")
        assert defaults_response.status_code == 200
        defaults = defaults_response.json()
        
        # Get a form with submitted status
        forms_response = requests.get(f"{BASE_URL}/api/application-forms", headers=auth_headers)
        assert forms_response.status_code == 200
        forms = forms_response.json()
        
        # Find a form that can have proposals created (any except pending)
        submitted_form = None
        for form in forms:
            # Allow submitted or under_review status
            if form.get("status") in ["submitted", "under_review"]:
                submitted_form = form
                break
        
        if not submitted_form:
            pytest.skip("No eligible form available for testing")
        
        # Create proposal payload with signature and stamp
        proposal_data = {
            "application_form_id": submitted_form["id"],
            "organization_name": "Test Company for Proposal",
            "organization_address": "123 Test Street",
            "organization_phone": "+966123456789",
            "contact_person": "Test Contact",
            "contact_position": "Manager",
            "contact_email": "test@example.com",  # Valid email required
            "standards": ["ISO9001", "ISO14001"],
            "scope": "Quality and Environmental Management",
            "total_employees": 100,
            "number_of_sites": 1,
            "audit_duration": {
                "stage_1": 2.0,
                "stage_2": 4.0,
                "surveillance_1": 2.0,
                "surveillance_2": 2.0,
                "recertification": 4.0
            },
            "service_fees": {
                "initial_certification": 10000,
                "surveillance_1": 5000,
                "surveillance_2": 5000,
                "recertification": 8000,
                "currency": "SAR"
            },
            "notes": "Test proposal",
            "validity_days": 30,
            "issuer_name": defaults["issuer_name"],
            "issuer_designation": defaults["issuer_designation"],
            "issuer_signature": defaults["issuer_signature"],
            "issuer_stamp": defaults["issuer_stamp"]
        }
        
        # Calculate payload size
        import json
        payload_size = len(json.dumps(proposal_data))
        print(f"Proposal payload size: {payload_size} bytes ({payload_size/1024:.1f} KB)")
        
        # Create proposal
        response = requests.post(
            f"{BASE_URL}/api/proposals",
            json=proposal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Proposal creation failed: {response.text}"
        
        proposal = response.json()
        assert "id" in proposal
        assert proposal["organization_name"] == "Test Company for Proposal"
        assert proposal["issuer_name"] == defaults["issuer_name"]
        assert proposal["issuer_signature"] == defaults["issuer_signature"]
        assert proposal["issuer_stamp"] == defaults["issuer_stamp"]
        
        print(f"Proposal created successfully with ID: {proposal['id']}")
    
    def test_create_proposal_invalid_email_returns_readable_error(self, auth_headers):
        """Test that invalid email returns a readable Pydantic error, not [object Object]"""
        # Get a form with submitted status
        forms_response = requests.get(f"{BASE_URL}/api/application-forms", headers=auth_headers)
        forms = forms_response.json()
        
        submitted_form = None
        for form in forms:
            if form.get("status") in ["submitted", "under_review"]:
                submitted_form = form
                break
        
        if not submitted_form:
            pytest.skip("No eligible form available for testing")
        
        # Create proposal with INVALID email
        proposal_data = {
            "application_form_id": submitted_form["id"],
            "organization_name": "Test Company",
            "organization_address": "Address",
            "organization_phone": "123",
            "contact_person": "Contact",
            "contact_position": "Position",
            "contact_email": "invalid-email-without-at-sign",  # INVALID
            "standards": ["ISO9001"],
            "scope": "Scope",
            "total_employees": 10,
            "number_of_sites": 1,
            "audit_duration": {
                "stage_1": 1, "stage_2": 1, "surveillance_1": 1,
                "surveillance_2": 1, "recertification": 1
            },
            "service_fees": {
                "initial_certification": 1000, "surveillance_1": 500,
                "surveillance_2": 500, "recertification": 800, "currency": "SAR"
            },
            "notes": "",
            "validity_days": 30,
            "issuer_name": "Test",
            "issuer_designation": "Test",
            "issuer_signature": "",
            "issuer_stamp": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/proposals",
            json=proposal_data,
            headers=auth_headers
        )
        
        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        
        error_detail = response.json().get("detail")
        assert error_detail is not None, "Error detail should be present"
        
        # Verify the error is a list (Pydantic format) with readable messages
        if isinstance(error_detail, list):
            for err in error_detail:
                assert "loc" in err or "msg" in err, "Error should have loc or msg"
                print(f"Validation error: {err}")
        
        # Verify it mentions email validation
        error_str = str(error_detail)
        assert "email" in error_str.lower() or "@" in error_str, \
            f"Error should mention email validation: {error_str}"
        
        print("Error handling test passed - returns readable validation error")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
