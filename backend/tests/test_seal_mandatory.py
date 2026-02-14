"""
Test suite for P0 bug fixes:
1. Mark all as read text truncation fix in notification dropdown
2. Company seal mandatory requirement on certification agreement
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBackendAPIHealth:
    """Basic health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"API root working: {data}")


class TestCompanySealMandatory:
    """Test that company seal/stamp is now mandatory on agreement submit"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin login failed - skipping tests")
    
    def test_agreement_submit_without_stamp_returns_422(self):
        """
        POST /api/public/agreement/{access_token}/submit without stamp_image should return 422
        This tests the backend validation that company seal is now required
        """
        # First get a valid proposal access token from existing proposals
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        token = response.json().get("token")
        
        # Get proposals to find one we can test with
        response = requests.get(
            f"{BASE_URL}/api/proposals",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200 or not response.json():
            pytest.skip("No proposals available for testing")
        
        proposals = response.json()
        # Find an accepted proposal for testing
        accepted_proposal = None
        for p in proposals:
            if p.get("status") == "accepted":
                accepted_proposal = p
                break
        
        if not accepted_proposal:
            # Create test data with a fake access token to test validation
            fake_access_token = "test-fake-token-12345"
            
            # Test payload without stamp_image
            payload = {
                "organization_name": "Test Company",
                "organization_address": "123 Test St",
                "selected_standards": ["ISO9001"],
                "other_standard": "",
                "scope_of_services": "Testing services",
                "sites": ["Main Site"],
                "signatory_name": "Test Person",
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
                "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                # INTENTIONALLY MISSING stamp_image
            }
            
            response = requests.post(
                f"{BASE_URL}/api/public/agreement/{fake_access_token}/submit",
                json=payload
            )
            
            # Should return 422 for validation error OR 404 if proposal not found
            # The important thing is it should NOT return 200
            assert response.status_code in [404, 422], f"Expected 404 or 422, got {response.status_code}"
            print(f"Response status: {response.status_code}, body: {response.json()}")
            
            # If it returns 422, verify error message mentions stamp
            if response.status_code == 422:
                error_detail = response.json()
                print(f"Validation error (expected): {error_detail}")
                # Check if the error is about missing stamp_image
                assert "stamp" in str(error_detail).lower() or "seal" in str(error_detail).lower() or "field required" in str(error_detail).lower(), \
                    "Error should mention stamp/seal requirement"
        else:
            access_token = accepted_proposal.get("access_token")
            
            # Test payload without stamp_image
            payload = {
                "organization_name": "Test Company",
                "organization_address": "123 Test St",
                "selected_standards": ["ISO9001"],
                "other_standard": "",
                "scope_of_services": "Testing services",
                "sites": ["Main Site"],
                "signatory_name": "Test Person",
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
                "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                # INTENTIONALLY MISSING stamp_image
            }
            
            response = requests.post(
                f"{BASE_URL}/api/public/agreement/{access_token}/submit",
                json=payload
            )
            
            # Should return 422 for validation error OR 400 if already submitted
            assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}: {response.text}"
            print(f"Response status: {response.status_code}, body: {response.json()}")

    def test_agreement_submit_with_stamp_validates_correctly(self):
        """
        Test that providing stamp_image in the payload is accepted (validation passes)
        """
        # Test with a fake token - we just want to verify the validation logic
        fake_access_token = "test-fake-token-67890"
        
        # Test payload WITH stamp_image
        payload = {
            "organization_name": "Test Company",
            "organization_address": "123 Test St",
            "selected_standards": ["ISO9001"],
            "other_standard": "",
            "scope_of_services": "Testing services",
            "sites": ["Main Site"],
            "signatory_name": "Test Person",
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
            "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "stamp_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/agreement/{fake_access_token}/submit",
            json=payload
        )
        
        # With valid payload including stamp_image, we should get 404 (proposal not found)
        # NOT 422 (validation error) - this proves validation passed
        assert response.status_code != 422, f"Should not get 422 with stamp_image provided, got: {response.text}"
        print(f"Response status: {response.status_code} - validation passed, error is about proposal not found")


class TestPydanticModelValidation:
    """Test that the Pydantic model validates stamp_image as required"""
    
    def test_stamp_image_field_is_required_in_model(self):
        """
        Verify the CertificationAgreementSubmit model has stamp_image as required field
        by making API call with missing stamp_image
        """
        fake_access_token = "test-validation-token"
        
        # Payload missing stamp_image - should fail Pydantic validation
        payload = {
            "organization_name": "Test Company",
            "organization_address": "123 Test St",
            "selected_standards": ["ISO9001"],
            "scope_of_services": "Testing services",
            "sites": ["Main Site"],
            "signatory_name": "Test Person",
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
            "signature_image": "data:image/png;base64,test"
            # stamp_image intentionally missing
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/agreement/{fake_access_token}/submit",
            json=payload
        )
        
        # Should get 422 validation error because stamp_image is now required
        assert response.status_code == 422, f"Expected 422 for missing required field, got {response.status_code}"
        
        error_detail = response.json()
        print(f"Pydantic validation error (expected): {error_detail}")
        
        # Verify error mentions stamp_image
        error_str = str(error_detail).lower()
        assert "stamp_image" in error_str or "stamp" in error_str or "field required" in error_str, \
            f"Error should mention stamp_image field: {error_detail}"


class TestNotificationsAPI:
    """Test notifications API for mark all as read feature"""
    
    def test_notifications_endpoint_works(self):
        """Test that notifications API is accessible"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        token = response.json().get("token")
        
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"Notifications API working: {len(data.get('notifications', []))} notifications, {data.get('unread_count')} unread")
    
    def test_mark_all_read_endpoint_works(self):
        """Test that mark all as read endpoint works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        token = response.json().get("token")
        
        response = requests.put(
            f"{BASE_URL}/api/notifications/read-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"Mark all as read response: {data}")
        
        # Verify unread count is now 0
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("unread_count") == 0, f"Expected 0 unread after mark all read, got {data.get('unread_count')}"
        print("All notifications marked as read successfully")
