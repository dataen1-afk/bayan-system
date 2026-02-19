"""
Test Certification Agreement Feature
Tests for the new Certification Agreement form workflow
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-audit-hub-1.preview.emergentagent.com')

# Known test data from the main agent
TEST_ACCESS_TOKEN = "7e9465b4-fa2d-4ba9-8baf-05e5d32cd971"  # Proposal already accepted

class TestAgreementEndpoints:
    """Test Certification Agreement API endpoints"""
    
    def test_get_agreement_status_pending(self):
        """Test GET /api/public/agreement/{access_token} returns pending status"""
        response = requests.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data
        # Status should be "pending" if agreement not yet submitted
        # or "submitted" if already submitted
        assert data["status"] in ["pending", "submitted"]
        
        if data["status"] == "pending":
            assert "proposal" in data
            proposal = data["proposal"]
            assert proposal["status"] == "accepted"
            print(f"Agreement status is pending, proposal data available")
        else:
            assert "agreement" in data
            print(f"Agreement already submitted")
        
        print(f"TEST PASSED: GET agreement status returned {data['status']}")
    
    def test_get_agreement_invalid_token(self):
        """Test GET /api/public/agreement with invalid token returns 404"""
        invalid_token = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/public/agreement/{invalid_token}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("TEST PASSED: Invalid token returns 404")
    
    def test_get_proposal_status_accepted(self):
        """Test GET /api/public/proposal/{access_token} returns accepted status"""
        response = requests.get(f"{BASE_URL}/api/public/proposal/{TEST_ACCESS_TOKEN}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "accepted" or data["status"] == "agreement_signed", \
            f"Expected 'accepted' or 'agreement_signed', got {data['status']}"
        assert "organization_name" in data
        assert "standards" in data
        assert len(data["standards"]) > 0
        
        print(f"TEST PASSED: Proposal status is {data['status']}, org: {data['organization_name']}")
    
    def test_submit_agreement_validation_required_fields(self):
        """Test POST /api/public/agreement/{access_token}/submit validates required fields"""
        # First check if agreement already submitted
        status_response = requests.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        if status_response.json().get("status") == "submitted":
            print("TEST SKIPPED: Agreement already submitted")
            return
        
        # Test with missing required fields
        incomplete_data = {
            "organization_name": "Test Org",
            # Missing other required fields
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}/submit",
            json=incomplete_data
        )
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
        print("TEST PASSED: Missing required fields return 422 validation error")
    
    def test_submit_agreement_requires_accepted_proposal(self):
        """Test that agreement submission requires an accepted proposal"""
        # Use a non-existent token
        fake_token = str(uuid.uuid4())
        
        complete_data = {
            "organization_name": "Test Organization",
            "organization_address": "Test Address",
            "selected_standards": ["ISO9001"],
            "other_standard": "",
            "scope_of_services": "Test scope",
            "sites": ["Site 1"],
            "signatory_name": "Test Signatory",
            "signatory_position": "CEO",
            "signatory_date": datetime.now().strftime("%Y-%m-%d"),
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/agreement/{fake_token}/submit",
            json=complete_data
        )
        
        # Should return 404 for non-existent proposal
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("TEST PASSED: Non-existent proposal returns 404")


class TestFullAgreementFlow:
    """Test the complete agreement submission flow"""
    
    def test_agreement_submission_flow(self):
        """Test the complete flow: Check proposal -> Submit agreement"""
        # Step 1: Check proposal status
        proposal_response = requests.get(f"{BASE_URL}/api/public/proposal/{TEST_ACCESS_TOKEN}")
        assert proposal_response.status_code == 200
        
        proposal = proposal_response.json()
        print(f"Proposal status: {proposal['status']}")
        
        if proposal['status'] not in ['accepted', 'agreement_signed']:
            print(f"TEST SKIPPED: Proposal not accepted (status: {proposal['status']})")
            return
        
        # Step 2: Check current agreement status
        agreement_status_response = requests.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        assert agreement_status_response.status_code == 200
        
        agreement_status = agreement_status_response.json()
        
        if agreement_status['status'] == 'submitted':
            print("TEST INFO: Agreement already submitted, verifying data structure")
            assert "agreement" in agreement_status
            agreement = agreement_status["agreement"]
            assert "organization_name" in agreement
            assert "selected_standards" in agreement
            assert "acknowledgements" in agreement
            print("TEST PASSED: Agreement data structure is valid")
            return
        
        # Step 3: Submit agreement (only if not already submitted)
        print("Submitting new agreement...")
        agreement_data = {
            "organization_name": proposal.get("organization_name", "Test Organization"),
            "organization_address": proposal.get("organization_address", "Test Address"),
            "selected_standards": proposal.get("standards", ["ISO9001"]),
            "other_standard": "",
            "scope_of_services": proposal.get("scope", "Test scope of services"),
            "sites": ["Main Office - Test Address"],
            "signatory_name": "Test Signatory Name",
            "signatory_position": "Managing Director",
            "signatory_date": datetime.now().strftime("%Y-%m-%d"),
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            }
        }
        
        submit_response = requests.post(
            f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}/submit",
            json=agreement_data
        )
        
        if submit_response.status_code == 400:
            # Agreement already submitted
            assert "already been submitted" in submit_response.text.lower()
            print("TEST INFO: Agreement already submitted (expected)")
        else:
            assert submit_response.status_code == 200, f"Expected 200, got {submit_response.status_code}: {submit_response.text}"
            result = submit_response.json()
            assert "message" in result
            assert "agreement_id" in result
            print(f"TEST PASSED: Agreement submitted, ID: {result['agreement_id']}")
        
        # Step 4: Verify agreement status updated
        final_status_response = requests.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        assert final_status_response.status_code == 200
        
        final_status = final_status_response.json()
        # Status should be 'submitted' after successful submission
        assert final_status['status'] == 'submitted'
        print("TEST PASSED: Agreement status is now 'submitted'")
    
    def test_duplicate_agreement_submission_fails(self):
        """Test that submitting agreement twice fails"""
        # Check if agreement exists
        status_response = requests.get(f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}")
        
        if status_response.json().get("status") != "submitted":
            print("TEST SKIPPED: Agreement not yet submitted")
            return
        
        # Try to submit again
        duplicate_data = {
            "organization_name": "Test Organization",
            "organization_address": "Test Address",
            "selected_standards": ["ISO9001"],
            "other_standard": "",
            "scope_of_services": "Test scope",
            "sites": ["Site 1"],
            "signatory_name": "Test Signatory",
            "signatory_position": "CEO",
            "signatory_date": datetime.now().strftime("%Y-%m-%d"),
            "acknowledgements": {
                "certificationRules": True,
                "publicDirectory": True,
                "certificationCommunication": True,
                "surveillanceSchedule": True,
                "nonconformityResolution": True,
                "feesAndPayment": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/agreement/{TEST_ACCESS_TOKEN}/submit",
            json=duplicate_data
        )
        
        # Should return 400 - agreement already submitted or proposal status changed
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        # Error can be "already submitted" OR "must be accepted" (if proposal status changed to agreement_signed)
        error_msg = response.text.lower()
        assert "already" in error_msg or "accepted" in error_msg, \
            f"Expected error about already submitted or status, got: {response.text}"
        print("TEST PASSED: Duplicate submission correctly rejected")


class TestProposalWorkflow:
    """Test the proposal acceptance to agreement flow"""
    
    def test_public_proposal_has_correct_fields(self):
        """Test that public proposal endpoint returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/public/proposal/{TEST_ACCESS_TOKEN}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Required fields for agreement pre-filling
        required_fields = [
            "id", "organization_name", "organization_address", "standards",
            "scope", "number_of_sites", "status"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"TEST PASSED: Public proposal contains all required fields")
        print(f"  - Organization: {data['organization_name']}")
        print(f"  - Standards: {data['standards']}")
        print(f"  - Sites: {data['number_of_sites']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
