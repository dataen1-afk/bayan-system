"""
Test Pre-Transfer Review (BAC-F6-17) API Endpoints
Tests CRUD operations, make-decision, and PDF generation
"""

import pytest
import requests
import os
import uuid

# Get backend URL from environment - must be set
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is required")

class TestPreTransferReviews:
    """Pre-Transfer Review CRUD Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth token
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@test.com", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Authentication failed - skipping tests")
        
        yield
        
        # Cleanup: Delete any test-created pre-transfer reviews
        try:
            reviews = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews").json()
            for review in reviews:
                if review.get('client_name', '').startswith('TEST_'):
                    self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review['id']}")
        except:
            pass
    
    def test_01_auth_working(self):
        """Test authentication is working"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth check failed: {response.text}"
        user = response.json()
        assert 'email' in user
        print(f"✓ Authenticated as: {user['email']}")
    
    def test_02_get_all_pre_transfer_reviews(self):
        """Test GET /api/pre-transfer-reviews - List all reviews"""
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews")
        assert response.status_code == 200, f"GET failed: {response.text}"
        
        reviews = response.json()
        assert isinstance(reviews, list)
        print(f"✓ Found {len(reviews)} pre-transfer reviews")
        
        # If there's existing data, verify structure
        if len(reviews) > 0:
            review = reviews[0]
            assert 'id' in review
            assert 'client_name' in review
            assert 'status' in review
            print(f"✓ First review: {review.get('client_name')} - Status: {review.get('status')}")
    
    def test_03_create_pre_transfer_review(self):
        """Test POST /api/pre-transfer-reviews - Create new review"""
        test_client_name = f"TEST_Manufacturing_{uuid.uuid4().hex[:6]}"
        
        create_data = {
            "client_name": test_client_name,
            "client_name_ar": "شركة اختبار للتصنيع",
            "client_address": "123 Industrial Area, Riyadh",
            "client_phone": "+966 12 345 6789",
            "enquiry_reference": f"ENQ-{uuid.uuid4().hex[:6]}",
            "transfer_reason": "Better service and coverage",
            "existing_cb": "ABC Certification",
            "certificate_number": "ABC-2024-12345",
            "validity": "2024-01-01 to 2027-01-01",
            "scope": "Manufacturing of electronic components",
            "sites": "Main factory, Warehouse",
            "eac_code": "19",
            "standards": ["ISO 9001:2015", "ISO 14001:2015"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/pre-transfer-reviews", json=create_data)
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        result = response.json()
        assert 'id' in result, "Response should contain 'id'"
        assert result.get('message') == "Pre-transfer review created"
        
        # Store the ID for later tests
        self.created_id = result['id']
        print(f"✓ Created pre-transfer review: {result['id']}")
        
        # Verify by getting the review
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{result['id']}")
        assert get_response.status_code == 200, f"GET after create failed: {get_response.text}"
        
        created_review = get_response.json()
        assert created_review['client_name'] == test_client_name
        assert created_review['existing_cb'] == "ABC Certification"
        assert created_review['status'] == "draft"
        assert 'checklist' in created_review
        print(f"✓ Verified created review data - Status: {created_review['status']}")
    
    def test_04_create_minimal_review(self):
        """Test creating review with only required field (client_name)"""
        test_client_name = f"TEST_Minimal_{uuid.uuid4().hex[:6]}"
        
        create_data = {
            "client_name": test_client_name
        }
        
        response = self.session.post(f"{BASE_URL}/api/pre-transfer-reviews", json=create_data)
        assert response.status_code == 200, f"Minimal create failed: {response.text}"
        
        result = response.json()
        review_id = result['id']
        
        # Verify default checklist is initialized
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert get_response.status_code == 200
        
        review = get_response.json()
        assert 'checklist' in review
        # Verify default checklist items
        checklist = review['checklist']
        assert 'suspension_status' in checklist
        assert 'within_bac_scope' in checklist
        print(f"✓ Created minimal review with default checklist")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_05_get_single_review(self):
        """Test GET /api/pre-transfer-reviews/{id} - Get specific review"""
        # First create a review
        test_client_name = f"TEST_GetSingle_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": test_client_name, "existing_cb": "Test CB", "certificate_number": "CERT-001"}
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Get the review
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert response.status_code == 200, f"GET single failed: {response.text}"
        
        review = response.json()
        assert review['id'] == review_id
        assert review['client_name'] == test_client_name
        assert review['existing_cb'] == "Test CB"
        assert review['certificate_number'] == "CERT-001"
        print(f"✓ Retrieved single review: {review['client_name']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_06_get_nonexistent_review(self):
        """Test GET for non-existent review returns 404"""
        fake_id = f"nonexistent-{uuid.uuid4().hex}"
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{fake_id}")
        assert response.status_code == 404, f"Expected 404 for nonexistent review, got {response.status_code}"
        print("✓ Non-existent review returns 404")
    
    def test_07_update_pre_transfer_review(self):
        """Test PUT /api/pre-transfer-reviews/{id} - Update review"""
        # First create a review
        test_client_name = f"TEST_Update_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": test_client_name, "existing_cb": "Old CB"}
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Update the review
        update_data = {
            "existing_cb": "New Updated CB",
            "certificate_number": "CERT-UPDATED-001",
            "checklist": {
                "suspension_status": False,
                "threat_of_suspension": False,
                "within_bac_scope": True,
                "previous_reports_available": True
            },
            "has_previous_audit_report": True,
            "has_previous_certificates": True,
            "certification_cycle_stage": "After 1st Surveillance Audit"
        }
        
        response = self.session.put(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}", json=update_data)
        assert response.status_code == 200, f"Update failed: {response.text}"
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert get_response.status_code == 200
        
        updated_review = get_response.json()
        assert updated_review['existing_cb'] == "New Updated CB"
        assert updated_review['certificate_number'] == "CERT-UPDATED-001"
        assert updated_review['checklist']['within_bac_scope'] == True
        assert updated_review['has_previous_audit_report'] == True
        assert updated_review['certification_cycle_stage'] == "After 1st Surveillance Audit"
        print(f"✓ Updated pre-transfer review - New CB: {updated_review['existing_cb']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_08_update_nonexistent_review(self):
        """Test PUT for non-existent review returns 404"""
        fake_id = f"nonexistent-{uuid.uuid4().hex}"
        response = self.session.put(
            f"{BASE_URL}/api/pre-transfer-reviews/{fake_id}",
            json={"client_name": "Updated Name"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent review update returns 404")
    
    def test_09_delete_pre_transfer_review(self):
        """Test DELETE /api/pre-transfer-reviews/{id} - Delete review"""
        # First create a review
        test_client_name = f"TEST_Delete_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": test_client_name}
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Delete the review
        response = self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert response.status_code == 200, f"Delete failed: {response.text}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert get_response.status_code == 404, "Review should not exist after deletion"
        print(f"✓ Deleted pre-transfer review: {review_id}")
    
    def test_10_delete_nonexistent_review(self):
        """Test DELETE for non-existent review returns 404"""
        fake_id = f"nonexistent-{uuid.uuid4().hex}"
        response = self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{fake_id}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent review delete returns 404")
    
    def test_11_make_decision_approve(self):
        """Test POST /api/pre-transfer-reviews/{id}/make-decision - Approve"""
        # First create a review
        test_client_name = f"TEST_Approve_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={
                "client_name": test_client_name,
                "existing_cb": "Test CB",
                "certificate_number": "CERT-APPROVE-001"
            }
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Make approval decision
        decision_data = {
            "transfer_decision": "approved",
            "reviewed_by": "Quality Manager",
            "review_date": "2026-01-18",
            "approved_by": "Certification Manager",
            "approval_date": "2026-01-18"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/make-decision",
            json=decision_data
        )
        assert response.status_code == 200, f"Decision failed: {response.text}"
        
        result = response.json()
        assert "approved" in result.get('message', '').lower()
        
        # Verify the decision was applied
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert get_response.status_code == 200
        
        review = get_response.json()
        assert review['transfer_decision'] == "approved"
        assert review['status'] == "decision_made"
        assert review['reviewed_by'] == "Quality Manager"
        assert review['approved_by'] == "Certification Manager"
        print(f"✓ Made approval decision - Status: {review['status']}, Decision: {review['transfer_decision']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_12_make_decision_reject(self):
        """Test POST /api/pre-transfer-reviews/{id}/make-decision - Reject"""
        # First create a review
        test_client_name = f"TEST_Reject_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={
                "client_name": test_client_name,
                "existing_cb": "Test CB"
            }
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Make rejection decision
        decision_data = {
            "transfer_decision": "rejected",
            "decision_reason": "Client has outstanding major non-conformities",
            "reviewed_by": "Quality Manager",
            "review_date": "2026-01-18",
            "approved_by": "Certification Manager",
            "approval_date": "2026-01-18"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/make-decision",
            json=decision_data
        )
        assert response.status_code == 200, f"Rejection failed: {response.text}"
        
        # Verify the decision was applied
        get_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
        assert get_response.status_code == 200
        
        review = get_response.json()
        assert review['transfer_decision'] == "rejected"
        assert review['status'] == "decision_made"
        assert review['decision_reason'] == "Client has outstanding major non-conformities"
        print(f"✓ Made rejection decision - Reason: {review['decision_reason']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_13_make_decision_invalid(self):
        """Test invalid decision value returns 400"""
        # First create a review
        test_client_name = f"TEST_InvalidDec_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": test_client_name}
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Try invalid decision
        response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/make-decision",
            json={"transfer_decision": "invalid_decision"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid decision, got {response.status_code}"
        print("✓ Invalid decision returns 400")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_14_make_decision_nonexistent(self):
        """Test make-decision for non-existent review returns 404"""
        fake_id = f"nonexistent-{uuid.uuid4().hex}"
        response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{fake_id}/make-decision",
            json={"transfer_decision": "approved"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent review decision returns 404")
    
    def test_15_get_pdf(self):
        """Test GET /api/pre-transfer-reviews/{id}/pdf - PDF generation"""
        # First create a review with complete data
        test_client_name = f"TEST_PDF_{uuid.uuid4().hex[:6]}"
        create_response = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={
                "client_name": test_client_name,
                "client_name_ar": "شركة اختبار",
                "client_address": "Test Address",
                "client_phone": "+966 12 345 6789",
                "enquiry_reference": "ENQ-PDF-001",
                "existing_cb": "Previous CB",
                "certificate_number": "CERT-PDF-001",
                "validity": "2024-2027",
                "scope": "Test Scope",
                "sites": "Site 1, Site 2",
                "eac_code": "19",
                "standards": ["ISO 9001:2015"]
            }
        )
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Update checklist and make decision for complete PDF
        self.session.put(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}",
            json={
                "checklist": {
                    "suspension_status": False,
                    "threat_of_suspension": False,
                    "minor_nc_outstanding": False,
                    "major_nc_outstanding": False,
                    "legal_representation": False,
                    "complaints_handled": True,
                    "within_bac_scope": True,
                    "previous_reports_available": True
                }
            }
        )
        
        # Make decision
        self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/make-decision",
            json={
                "transfer_decision": "approved",
                "reviewed_by": "QM",
                "approved_by": "CM"
            }
        )
        
        # Get PDF
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/pdf")
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert response.headers.get('content-type') == 'application/pdf'
        
        # Verify PDF content
        pdf_content = response.content
        assert len(pdf_content) > 1000, "PDF content seems too small"
        assert pdf_content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"✓ Generated PDF - Size: {len(pdf_content)} bytes")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{review_id}")
    
    def test_16_get_pdf_nonexistent(self):
        """Test PDF generation for non-existent review returns 404"""
        fake_id = f"nonexistent-{uuid.uuid4().hex}"
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{fake_id}/pdf")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent review PDF returns 404")
    
    def test_17_filter_by_status(self):
        """Test GET /api/pre-transfer-reviews?status=X - Filter by status"""
        # Create reviews with different statuses
        reviews_to_create = []
        
        # Create draft review
        draft_name = f"TEST_Draft_{uuid.uuid4().hex[:6]}"
        draft_resp = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": draft_name}
        )
        assert draft_resp.status_code == 200
        reviews_to_create.append(draft_resp.json()['id'])
        
        # Create and approve another review
        decision_name = f"TEST_Decision_{uuid.uuid4().hex[:6]}"
        decision_resp = self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            json={"client_name": decision_name}
        )
        assert decision_resp.status_code == 200
        decision_id = decision_resp.json()['id']
        reviews_to_create.append(decision_id)
        
        # Approve it
        self.session.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{decision_id}/make-decision",
            json={"transfer_decision": "approved"}
        )
        
        # Filter by draft status
        draft_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews?status=draft")
        assert draft_response.status_code == 200
        draft_reviews = draft_response.json()
        assert all(r['status'] == 'draft' for r in draft_reviews if r.get('client_name', '').startswith('TEST_'))
        print(f"✓ Filtered by draft - Found {len([r for r in draft_reviews if r['status'] == 'draft'])} draft reviews")
        
        # Filter by decision_made status
        decision_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews?status=decision_made")
        assert decision_response.status_code == 200
        decision_reviews = decision_response.json()
        assert all(r['status'] == 'decision_made' for r in decision_reviews)
        print(f"✓ Filtered by decision_made - Found {len(decision_reviews)} reviews with decisions")
        
        # Get all (no filter)
        all_response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews")
        assert all_response.status_code == 200
        all_reviews = all_response.json()
        print(f"✓ All reviews (no filter) - Found {len(all_reviews)} total reviews")
        
        # Cleanup
        for rid in reviews_to_create:
            self.session.delete(f"{BASE_URL}/api/pre-transfer-reviews/{rid}")
    
    def test_18_existing_review_from_dev(self):
        """Test accessing the existing review created during development"""
        known_id = "3b72fd5c-10dd-4c27-af8a-58305c54e5bf"
        
        response = self.session.get(f"{BASE_URL}/api/pre-transfer-reviews/{known_id}")
        
        if response.status_code == 200:
            review = response.json()
            print(f"✓ Found existing dev review: {review.get('client_name')}")
            print(f"  - Status: {review.get('status')}")
            print(f"  - Decision: {review.get('transfer_decision', 'pending')}")
            print(f"  - Existing CB: {review.get('existing_cb', 'N/A')}")
        elif response.status_code == 404:
            print("✓ Dev review was cleaned up or doesn't exist (acceptable)")
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
    
    def test_19_unauthorized_access(self):
        """Test that unauthorized requests are rejected"""
        # Create session without auth
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        # Try to access without token
        response = unauth_session.get(f"{BASE_URL}/api/pre-transfer-reviews")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Unauthorized access correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
