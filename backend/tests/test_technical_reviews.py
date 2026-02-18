"""
Test suite for Technical Review and Certification Decision (BAC-F6-15) feature
Tests all CRUD operations, decision making, and certificate auto-generation
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bayan-verify-portal.preview.emergentagent.com').rstrip('/')

class TestTechnicalReviewsFeature:
    """Test Technical Review endpoints (BAC-F6-15)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - authenticate before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def test_01_list_technical_reviews(self):
        """Test GET /api/technical-reviews - List all technical reviews"""
        response = requests.get(f"{BASE_URL}/api/technical-reviews", headers=self.headers)
        assert response.status_code == 200, f"Failed to get technical reviews: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Found {len(data)} technical reviews")
        
        # Store for later tests
        self.existing_reviews = data
        
    def test_02_create_technical_review_manual(self):
        """Test POST /api/technical-reviews - Create manual technical review"""
        payload = {
            "stage2_report_id": "",  # Manual entry
            "client_name": "TEST_TechReview_Company",
            "client_name_ar": "شركة الاختبار",
            "location": "Riyadh, Saudi Arabia",
            "scope": "Manufacturing of electronic components",
            "ea_code": "19",
            "standards": ["ISO 9001:2015"],
            "audit_type": "CA",
            "audit_dates": "2026-02-01 to 2026-02-03",
            "audit_team_members": ["Ahmed Ali", "Mohammed Hassan"],
            "technical_expert": "Dr. Khalid Ibrahim"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to create technical review: {response.text}"
        data = response.json()
        assert 'id' in data, "Response should contain review id"
        print(f"✓ Created technical review with id: {data['id']}")
        
        # Store id for subsequent tests
        self.__class__.created_review_id = data['id']
        
    def test_03_get_single_technical_review(self):
        """Test GET /api/technical-reviews/{id} - Get single review with checklist"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if not review_id:
            pytest.skip("No review ID from previous test")
            
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        assert response.status_code == 200, f"Failed to get technical review: {response.text}"
        data = response.json()
        
        # Verify structure
        assert data['client_name'] == "TEST_TechReview_Company", "Client name mismatch"
        assert data['standards'] == ["ISO 9001:2015"], "Standards mismatch"
        assert 'checklist_items' in data, "Should contain checklist items"
        assert len(data['checklist_items']) > 0, "Checklist should have items"
        assert data['status'] == 'draft', "Initial status should be 'draft'"
        
        # Verify checklist structure
        first_item = data['checklist_items'][0]
        assert 'category' in first_item, "Checklist item should have category"
        assert 'item' in first_item, "Checklist item should have item"
        assert 'checked' in first_item, "Checklist item should have checked status"
        
        print(f"✓ Review has {len(data['checklist_items'])} checklist items")
        
    def test_04_update_technical_review(self):
        """Test PUT /api/technical-reviews/{id} - Update review including checklist"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if not review_id:
            pytest.skip("No review ID from previous test")
            
        # First get current data
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        review = response.json()
        
        # Update checklist items (mark some as checked)
        updated_checklist = review.get('checklist_items', [])
        for i, item in enumerate(updated_checklist[:5]):  # Update first 5 items
            item['checked'] = True
            item['remarks'] = f"Verified - Test {i+1}"
        
        update_payload = {
            "technical_reviewer": "Eng. Fahad Al-Saud",
            "review_date": "2026-02-04",
            "checklist_items": updated_checklist,
            "review_comments": "All documentation verified and complete"
        }
        
        response = requests.put(f"{BASE_URL}/api/technical-reviews/{review_id}", json=update_payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to update technical review: {response.text}"
        
        # Verify update
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        data = response.json()
        assert data['technical_reviewer'] == "Eng. Fahad Al-Saud", "Technical reviewer not updated"
        assert data['review_date'] == "2026-02-04", "Review date not updated"
        
        # Verify checklist was updated
        verified_count = sum(1 for item in data['checklist_items'] if item.get('checked') == True)
        assert verified_count >= 5, f"Expected at least 5 checked items, got {verified_count}"
        
        print(f"✓ Updated review with {verified_count} verified checklist items")
        
    def test_05_make_decision_issue_certificate(self):
        """Test POST /api/technical-reviews/{id}/make-decision - Make certification decision"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if not review_id:
            pytest.skip("No review ID from previous test")
            
        decision_payload = {
            "certification_decision": "issue_certificate",
            "decision_comments": "All requirements met. Recommend certificate issuance."
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{review_id}/make-decision", json=decision_payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to make decision: {response.text}"
        
        # Verify status changed to decision_made
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        data = response.json()
        assert data['status'] == 'decision_made', "Status should be 'decision_made'"
        assert data['certification_decision'] == 'issue_certificate', "Decision not recorded"
        
        print("✓ Decision made: issue_certificate")
        
    def test_06_approve_and_auto_issue_certificate(self):
        """Test POST /api/technical-reviews/{id}/approve - Approve and auto-issue certificate"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if not review_id:
            pytest.skip("No review ID from previous test")
            
        approval_payload = {
            "approved_by": "Abdullah Al-Rashid",
            "approval_date": "2026-02-05"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{review_id}/approve", json=approval_payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to approve: {response.text}"
        data = response.json()
        
        # Should have certificate info since decision was 'issue_certificate'
        assert 'certificate' in data, "Response should contain certificate info"
        assert 'certificate_number' in data['certificate'], "Should have certificate number"
        
        # Store certificate number for verification
        cert_number = data['certificate']['certificate_number']
        print(f"✓ Certificate auto-generated: {cert_number}")
        
        # Verify review status updated
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        review_data = response.json()
        assert review_data['status'] == 'certificate_issued', "Status should be 'certificate_issued'"
        assert review_data['certificate_number'] == cert_number, "Certificate number should be stored"
        assert review_data['approved_by'] == "Abdullah Al-Rashid", "Approver not recorded"
        
        # Verify certificate was actually created in certificates collection
        certs_response = requests.get(f"{BASE_URL}/api/certificates", headers=self.headers)
        certs = certs_response.json()
        matching_cert = [c for c in certs if c.get('certificate_number') == cert_number]
        assert len(matching_cert) > 0, f"Certificate {cert_number} not found in certificates"
        
        print(f"✓ Certificate {cert_number} verified in certificates collection")
        
    def test_07_generate_pdf(self):
        """Test GET /api/technical-reviews/{id}/pdf - Generate PDF"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if not review_id:
            pytest.skip("No review ID from previous test")
            
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}/pdf", headers=self.headers)
        assert response.status_code == 200, f"Failed to generate PDF: {response.text}"
        assert 'application/pdf' in response.headers.get('content-type', ''), "Response should be PDF"
        assert len(response.content) > 1000, "PDF should have content"
        
        print(f"✓ PDF generated: {len(response.content)} bytes")
        
    def test_08_create_and_delete_review(self):
        """Test DELETE /api/technical-reviews/{id} - Delete review"""
        # Create a new review to delete
        payload = {
            "client_name": "TEST_DELETE_Company",
            "standards": ["ISO 14001:2015"],
            "audit_type": "SA"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to create: {response.text}"
        delete_id = response.json()['id']
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/technical-reviews/{delete_id}", headers=self.headers)
        assert response.status_code == 200, f"Failed to delete: {response.text}"
        
        # Verify deletion
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{delete_id}", headers=self.headers)
        assert response.status_code == 404, "Deleted review should not be found"
        
        print("✓ Delete operation successful")
        
    def test_09_make_decision_reject(self):
        """Test making reject decision"""
        # Create a new review for rejection
        payload = {
            "client_name": "TEST_REJECT_Company",
            "standards": ["ISO 45001:2018"],
            "audit_type": "CA"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200
        reject_id = response.json()['id']
        
        # Make reject decision
        decision_payload = {
            "certification_decision": "reject_certificate",
            "decision_comments": "Major nonconformities not addressed"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{reject_id}/make-decision", json=decision_payload, headers=self.headers)
        assert response.status_code == 200, f"Failed to make reject decision: {response.text}"
        
        # Approve (should NOT issue certificate)
        approval_payload = {
            "approved_by": "Test Approver",
            "approval_date": "2026-02-05"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{reject_id}/approve", json=approval_payload, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should NOT have certificate
        assert 'certificate' not in data or data.get('certificate') is None, "Rejected review should not have certificate"
        
        # Verify status is 'approved' not 'certificate_issued'
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{reject_id}", headers=self.headers)
        review_data = response.json()
        assert review_data['status'] == 'approved', "Status should be 'approved' (not certificate_issued)"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/technical-reviews/{reject_id}", headers=self.headers)
        
        print("✓ Reject decision workflow correct - no certificate issued")
        
    def test_10_make_decision_needs_review(self):
        """Test making 'needs_review' decision"""
        # Create a new review
        payload = {
            "client_name": "TEST_NEEDS_REVIEW_Company",
            "standards": ["ISO 27001:2022"],
            "audit_type": "RA"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200
        review_id = response.json()['id']
        
        # Make needs_review decision
        decision_payload = {
            "certification_decision": "needs_review",
            "decision_comments": "Additional technical review required for IT security controls"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{review_id}/make-decision", json=decision_payload, headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify status
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        data = response.json()
        assert data['certification_decision'] == 'needs_review', "Decision not recorded"
        assert data['status'] == 'decision_made', "Status should be decision_made"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        
        print("✓ 'needs_review' decision workflow correct")
        
    def test_11_invalid_decision(self):
        """Test invalid certification decision"""
        # Create a new review
        payload = {
            "client_name": "TEST_INVALID_Decision",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200
        review_id = response.json()['id']
        
        # Try invalid decision
        decision_payload = {
            "certification_decision": "invalid_decision",
            "decision_comments": "Test"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews/{review_id}/make-decision", json=decision_payload, headers=self.headers)
        assert response.status_code == 400, "Should reject invalid decision"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        
        print("✓ Invalid decision correctly rejected")
        
    def test_12_list_with_status_filter(self):
        """Test listing reviews with status filter"""
        response = requests.get(f"{BASE_URL}/api/technical-reviews?status=certificate_issued", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # All results should have certificate_issued status
        for review in data:
            assert review['status'] == 'certificate_issued', f"Filter not working: {review['status']}"
            
        print(f"✓ Status filter working: {len(data)} certificate_issued reviews")
        
    def test_13_cleanup_test_data(self):
        """Cleanup test data created during tests"""
        review_id = getattr(self.__class__, 'created_review_id', None)
        if review_id:
            # Delete the main test review
            response = requests.delete(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
            # May already be deleted or have certificate, so just log
            print(f"Cleanup: Review {review_id} delete status: {response.status_code}")
            
        # Clean up any remaining TEST_ prefixed reviews
        response = requests.get(f"{BASE_URL}/api/technical-reviews", headers=self.headers)
        if response.status_code == 200:
            reviews = response.json()
            for review in reviews:
                if review.get('client_name', '').startswith('TEST_'):
                    del_resp = requests.delete(f"{BASE_URL}/api/technical-reviews/{review['id']}", headers=self.headers)
                    print(f"Cleanup: Deleted TEST review {review['id']}: {del_resp.status_code}")
                    
        print("✓ Test data cleanup complete")


class TestTechnicalReviewEdgeCases:
    """Edge case tests for technical reviews"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        self.token = response.json()['token']
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def test_get_nonexistent_review(self):
        """Test getting a review that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/technical-reviews/nonexistent-id-12345", headers=self.headers)
        assert response.status_code == 404, "Should return 404"
        
    def test_update_nonexistent_review(self):
        """Test updating a review that doesn't exist"""
        response = requests.put(f"{BASE_URL}/api/technical-reviews/nonexistent-id-12345", 
                               json={"client_name": "Test"}, headers=self.headers)
        assert response.status_code == 404, "Should return 404"
        
    def test_delete_nonexistent_review(self):
        """Test deleting a review that doesn't exist"""
        response = requests.delete(f"{BASE_URL}/api/technical-reviews/nonexistent-id-12345", headers=self.headers)
        assert response.status_code == 404, "Should return 404"
        
    def test_create_with_minimal_data(self):
        """Test creating review with only required field"""
        payload = {
            "client_name": "TEST_MINIMAL_Company"
        }
        
        response = requests.post(f"{BASE_URL}/api/technical-reviews", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Should create with minimal data: {response.text}"
        review_id = response.json()['id']
        
        # Verify default checklist was created
        response = requests.get(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        data = response.json()
        assert len(data['checklist_items']) > 0, "Should have default checklist"
        assert data['status'] == 'draft', "Should be draft status"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/technical-reviews/{review_id}", headers=self.headers)
        print("✓ Minimal data creation works")
        
    def test_unauthorized_access(self):
        """Test accessing without auth token"""
        response = requests.get(f"{BASE_URL}/api/technical-reviews")
        # Should fail without auth
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("✓ Unauthorized access blocked")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
