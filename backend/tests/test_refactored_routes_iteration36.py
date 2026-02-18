"""
Test all refactored modular routes after major backend refactoring - Iteration 36
Tests: technical_reviews, customer_feedback, customer_feedback_public, 
       pre_transfer_reviews, certified_clients, suspended_clients, portal routes

This file tests the 7 features extracted from monolithic server.py into separate route files.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for all tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


# ================== TECHNICAL REVIEWS (BAC-F6-15) ==================

class TestTechnicalReviews:
    """Tests for /api/technical-reviews routes"""
    
    def test_get_technical_reviews(self, auth_token):
        """GET /api/technical-reviews - get all technical reviews"""
        response = requests.get(
            f"{BASE_URL}/api/technical-reviews",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/technical-reviews returns {len(response.json())} reviews")
    
    def test_create_and_crud_technical_review(self, auth_token):
        """POST, GET, PUT, DELETE /api/technical-reviews - full CRUD test"""
        # CREATE
        create_data = {
            "client_name": "TEST_Tech_Review_Client",
            "client_name_ar": "اختبار عميل",
            "location": "Test Location",
            "scope": "Quality Management",
            "ea_code": "EA-17",
            "standards": ["ISO 9001:2015"],
            "audit_type": "Initial Certification",
            "audit_dates": "2026-02-15 to 2026-02-17",
            "audit_team_members": ["Lead Auditor"],
            "technical_expert": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/technical-reviews",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        review_id = data["id"]
        print(f"✓ POST /api/technical-reviews created id={review_id}")
        
        # GET by ID
        response = requests.get(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["client_name"] == create_data["client_name"]
        print(f"✓ GET /api/technical-reviews/{review_id} verified persistence")
        
        # UPDATE
        update_data = {"review_comments": "Updated review comments"}
        response = requests.put(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_data
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/technical-reviews/{review_id} updated")
        
        # Verify update
        response = requests.get(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.json()["review_comments"] == "Updated review comments"
        print(f"✓ Update verified via GET")
        
        # DELETE
        response = requests.delete(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/technical-reviews/{review_id} success")
        
        # Verify deletion
        response = requests.get(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print(f"✓ Deletion verified - 404 returned")
    
    def test_technical_review_unauthorized(self):
        """GET /api/technical-reviews - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/technical-reviews")
        assert response.status_code == 403
        print(f"✓ Unauthenticated request correctly denied")


# ================== CUSTOMER FEEDBACK (BAC-F6-16) ==================

class TestCustomerFeedback:
    """Tests for /api/customer-feedback routes"""
    
    def test_get_customer_feedback(self, auth_token):
        """GET /api/customer-feedback - get all feedback"""
        response = requests.get(
            f"{BASE_URL}/api/customer-feedback",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/customer-feedback returns {len(response.json())} items")
    
    def test_create_and_crud_customer_feedback(self, auth_token):
        """POST, GET, PUT, DELETE /api/customer-feedback - full CRUD test"""
        # CREATE
        create_data = {
            "organization_name": "TEST_Feedback_Org",
            "organization_name_ar": "منظمة اختبار",
            "audit_type": "Initial Certification",
            "standards": ["ISO 9001:2015"],
            "audit_date": "2026-02-15",
            "lead_auditor": "Test Auditor",
            "auditor": "Test Auditor 2"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/customer-feedback",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "access_token" in data
        feedback_id = data["id"]
        access_token = data["access_token"]
        print(f"✓ POST /api/customer-feedback created id={feedback_id}, access_token={access_token[:8]}...")
        
        # GET by ID
        response = requests.get(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["organization_name"] == create_data["organization_name"]
        assert "questions" in fetched and isinstance(fetched["questions"], list)
        print(f"✓ GET /api/customer-feedback/{feedback_id} verified - {len(fetched['questions'])} default questions")
        
        # UPDATE
        update_data = {"suggestions": "Great service!"}
        response = requests.put(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_data
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/customer-feedback/{feedback_id} updated")
        
        # REVIEW endpoint
        review_data = {
            "reviewed_by": "Admin Reviewer",
            "review_comments": "Feedback acknowledged"
        }
        response = requests.post(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}/review",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=review_data
        )
        assert response.status_code == 200
        print(f"✓ POST /api/customer-feedback/{feedback_id}/review success")
        
        # DELETE
        response = requests.delete(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/customer-feedback/{feedback_id} success")
    
    def test_customer_feedback_unauthorized(self):
        """GET /api/customer-feedback - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/customer-feedback")
        assert response.status_code == 403
        print(f"✓ Unauthenticated request correctly denied")


# ================== PUBLIC FEEDBACK (BAC-F6-16 Public) ==================

class TestPublicFeedback:
    """Tests for /api/public/feedback/{token} routes (no auth required)"""
    
    def test_public_feedback_flow(self, auth_token):
        """Test full public feedback submission flow"""
        # First create a feedback form (admin)
        create_data = {
            "organization_name": "TEST_Public_Feedback_Org",
            "audit_type": "Surveillance",
            "standards": ["ISO 14001:2015"],
            "audit_date": "2026-02-20",
            "lead_auditor": "Lead Auditor Test"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/customer-feedback",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200
        feedback_id = response.json()["id"]
        access_token = response.json()["access_token"]
        print(f"✓ Created feedback form with access_token={access_token[:8]}...")
        
        # GET public feedback form (no auth)
        response = requests.get(f"{BASE_URL}/api/public/feedback/{access_token}")
        assert response.status_code == 200, f"Public GET failed: {response.text}"
        
        public_data = response.json()
        assert public_data["organization_name"] == create_data["organization_name"]
        assert "questions" in public_data
        print(f"✓ GET /api/public/feedback/{access_token[:8]}... returns form with {len(public_data['questions'])} questions")
        
        # POST public feedback submission (no auth)
        submit_data = {
            "questions": [{"index": 0, "rating": 5}, {"index": 1, "rating": 4}],
            "want_same_team": True,
            "suggestions": "Public submission test",
            "respondent_name": "Test Client",
            "respondent_designation": "Manager"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/feedback/{access_token}/submit",
            json=submit_data
        )
        assert response.status_code == 200, f"Public submit failed: {response.text}"
        
        result = response.json()
        assert "overall_score" in result
        assert "evaluation_result" in result
        print(f"✓ POST /api/public/feedback/{access_token[:8]}../submit success - score={result['overall_score']}%")
        
        # Verify submission reflects in admin view
        response = requests.get(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        admin_view = response.json()
        assert admin_view["status"] == "submitted"
        print(f"✓ Admin view shows status='submitted' after public submission")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        print(f"✓ Test feedback deleted")
    
    def test_public_feedback_invalid_token(self):
        """GET /api/public/feedback/{invalid} - returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/feedback/invalid-token-12345")
        assert response.status_code == 404
        print(f"✓ Invalid access token returns 404")


# ================== PRE-TRANSFER REVIEWS (BAC-F6-17) ==================

class TestPreTransferReviews:
    """Tests for /api/pre-transfer-reviews routes"""
    
    def test_get_pre_transfer_reviews(self, auth_token):
        """GET /api/pre-transfer-reviews - get all reviews"""
        response = requests.get(
            f"{BASE_URL}/api/pre-transfer-reviews",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/pre-transfer-reviews returns {len(response.json())} reviews")
    
    def test_create_and_crud_pre_transfer_review(self, auth_token):
        """POST, GET, PUT, DELETE /api/pre-transfer-reviews - full CRUD test"""
        # CREATE
        create_data = {
            "client_name": "TEST_Pre_Transfer_Client",
            "client_name_ar": "عميل نقل اختبار",
            "client_address": "Test Address 123",
            "client_phone": "+966123456789",
            "enquiry_reference": "ENQ-2026-001",
            "transfer_reason": "Change of CB",
            "existing_cb": "Previous CB Name",
            "certificate_number": "CERT-OLD-001",
            "validity": "2027-01-01",
            "scope": "Quality Management System",
            "sites": "1",
            "eac_code": "EA-17",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        review_id = data["id"]
        print(f"✓ POST /api/pre-transfer-reviews created id={review_id}")
        
        # GET by ID
        response = requests.get(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["client_name"] == create_data["client_name"]
        assert "checklist" in fetched
        print(f"✓ GET /api/pre-transfer-reviews/{review_id} verified - checklist has {len(fetched['checklist'])} items")
        
        # UPDATE
        update_data = {"decision_reason": "All requirements met"}
        response = requests.put(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_data
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/pre-transfer-reviews/{review_id} updated")
        
        # MAKE DECISION endpoint
        decision_data = {
            "transfer_decision": "approved",
            "decision_reason": "Transfer approved after review",
            "reviewed_by": "Admin Reviewer",
            "approved_by": "Manager"
        }
        response = requests.post(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/make-decision",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=decision_data
        )
        assert response.status_code == 200
        print(f"✓ POST /api/pre-transfer-reviews/{review_id}/make-decision success")
        
        # DELETE
        response = requests.delete(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/pre-transfer-reviews/{review_id} success")
    
    def test_pre_transfer_reviews_unauthorized(self):
        """GET /api/pre-transfer-reviews - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/pre-transfer-reviews")
        assert response.status_code == 403
        print(f"✓ Unauthenticated request correctly denied")


# ================== CERTIFIED CLIENTS (BAC-F6-19) ==================

class TestCertifiedClients:
    """Tests for /api/certified-clients routes"""
    
    def test_get_certified_clients(self, auth_token):
        """GET /api/certified-clients - get all certified clients"""
        response = requests.get(
            f"{BASE_URL}/api/certified-clients",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/certified-clients returns {len(response.json())} clients")
    
    def test_get_certified_clients_stats(self, auth_token):
        """GET /api/certified-clients/stats/overview - get statistics"""
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/stats/overview",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        stats = response.json()
        assert "total" in stats
        assert "active" in stats
        assert "suspended" in stats
        print(f"✓ GET /api/certified-clients/stats/overview - total={stats['total']}, active={stats['active']}")
    
    def test_create_and_crud_certified_client(self, auth_token):
        """POST, GET, PUT, DELETE /api/certified-clients - full CRUD test"""
        # CREATE
        create_data = {
            "client_name": "TEST_Certified_Client",
            "client_name_ar": "عميل معتمد اختبار",
            "address": "Test Address",
            "address_ar": "عنوان اختبار",
            "contact_person": "John Test",
            "contact_number": "+966123456789",
            "scope": "Manufacturing of widgets",
            "scope_ar": "تصنيع الأدوات",
            "accreditation": ["ISO 9001:2015", "ISO 14001:2015"],
            "ea_code": "EA-17",
            "certificate_number": "TEST-CERT-001",
            "issue_date": "2026-01-01",
            "expiry_date": "2029-01-01",
            "surveillance_1_date": "2027-01-01",
            "surveillance_2_date": "2028-01-01",
            "recertification_date": "2029-01-01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/certified-clients",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "serial_number" in data
        client_id = data["id"]
        print(f"✓ POST /api/certified-clients created id={client_id}, serial_number={data['serial_number']}")
        
        # GET by ID
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["client_name"] == create_data["client_name"]
        print(f"✓ GET /api/certified-clients/{client_id} verified persistence")
        
        # UPDATE
        update_data = {"notes": "Test notes updated"}
        response = requests.put(
            f"{BASE_URL}/api/certified-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_data
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/certified-clients/{client_id} updated")
        
        # DELETE
        response = requests.delete(
            f"{BASE_URL}/api/certified-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/certified-clients/{client_id} success")
    
    def test_certified_clients_excel_export(self, auth_token):
        """GET /api/certified-clients/export/excel - Excel export"""
        response = requests.get(
            f"{BASE_URL}/api/certified-clients/export/excel",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Excel export failed: {response.text}"
        assert "spreadsheetml" in response.headers.get("Content-Type", "")
        print(f"✓ GET /api/certified-clients/export/excel returns Excel file")
    
    def test_certified_clients_unauthorized(self):
        """GET /api/certified-clients - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/certified-clients")
        assert response.status_code == 403
        print(f"✓ Unauthenticated request correctly denied")


# ================== SUSPENDED CLIENTS (BAC-F6-20) ==================

class TestSuspendedClients:
    """Tests for /api/suspended-clients routes"""
    
    def test_get_suspended_clients(self, auth_token):
        """GET /api/suspended-clients - get all suspended clients"""
        response = requests.get(
            f"{BASE_URL}/api/suspended-clients",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/suspended-clients returns {len(response.json())} clients")
    
    def test_get_suspended_clients_stats(self, auth_token):
        """GET /api/suspended-clients/stats/overview - get statistics"""
        response = requests.get(
            f"{BASE_URL}/api/suspended-clients/stats/overview",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        stats = response.json()
        assert "total" in stats
        assert "suspended" in stats
        assert "reinstated" in stats
        print(f"✓ GET /api/suspended-clients/stats/overview - total={stats['total']}, suspended={stats['suspended']}")
    
    def test_create_and_crud_suspended_client(self, auth_token):
        """POST, GET, PUT, DELETE /api/suspended-clients - full CRUD test"""
        # CREATE
        create_data = {
            "client_name": "TEST_Suspended_Client",
            "client_name_ar": "عميل موقوف اختبار",
            "address": "Test Address",
            "address_ar": "عنوان اختبار",
            "registration_date": "2025-01-01",
            "suspended_on": "2026-02-01",
            "reason_for_suspension": "Failure to address nonconformities",
            "reason_for_suspension_ar": "فشل في معالجة عدم المطابقة",
            "future_action": "Reinstatement upon resolution",
            "remarks": "Under monitoring"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/suspended-clients",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "serial_number" in data
        client_id = data["id"]
        print(f"✓ POST /api/suspended-clients created id={client_id}, serial_number={data['serial_number']}")
        
        # GET by ID
        response = requests.get(
            f"{BASE_URL}/api/suspended-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["client_name"] == create_data["client_name"]
        print(f"✓ GET /api/suspended-clients/{client_id} verified persistence")
        
        # UPDATE
        update_data = {"remarks": "Updated remarks"}
        response = requests.put(
            f"{BASE_URL}/api/suspended-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=update_data
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/suspended-clients/{client_id} updated")
        
        # LIFT SUSPENSION endpoint
        lift_data = {
            "new_status": "reinstated",
            "lifted_reason": "All nonconformities resolved"
        }
        response = requests.post(
            f"{BASE_URL}/api/suspended-clients/{client_id}/lift-suspension",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=lift_data
        )
        assert response.status_code == 200
        print(f"✓ POST /api/suspended-clients/{client_id}/lift-suspension success")
        
        # DELETE
        response = requests.delete(
            f"{BASE_URL}/api/suspended-clients/{client_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/suspended-clients/{client_id} success")
    
    def test_suspended_clients_excel_export(self, auth_token):
        """GET /api/suspended-clients/export/excel - Excel export"""
        response = requests.get(
            f"{BASE_URL}/api/suspended-clients/export/excel",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Excel export failed: {response.text}"
        assert "spreadsheetml" in response.headers.get("Content-Type", "")
        print(f"✓ GET /api/suspended-clients/export/excel returns Excel file")
    
    def test_suspended_clients_unauthorized(self):
        """GET /api/suspended-clients - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/suspended-clients")
        assert response.status_code == 403
        print(f"✓ Unauthenticated request correctly denied")


# ================== PORTAL ROUTES (RFQ & Contact) ==================

class TestPortalRoutes:
    """Tests for /api/public/rfq and /api/public/contact routes"""
    
    def test_submit_rfq_public(self):
        """POST /api/public/rfq - submit RFQ without auth"""
        rfq_data = {
            "company_name": "TEST_RFQ_Company",
            "contact_name": "Test Contact",
            "email": "test@example.com",
            "phone": "+966123456789",
            "employees": "50-100",
            "sites": "2",
            "standards": ["ISO 9001:2015", "ISO 14001:2015"],
            "message": "Request for quote from testing"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        assert response.status_code == 200, f"RFQ submit failed: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "id" in data
        print(f"✓ POST /api/public/rfq success - id={data['id']}")
        
        # Return ID for cleanup
        return data["id"]
    
    def test_submit_contact_public(self):
        """POST /api/public/contact - submit contact form without auth"""
        contact_data = {
            "name": "Test Contact Person",
            "email": "testcontact@example.com",
            "subject": "Test Inquiry",
            "message": "This is a test contact message"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/contact", json=contact_data)
        assert response.status_code == 200, f"Contact submit failed: {response.text}"
        
        data = response.json()
        assert "message" in data
        print(f"✓ POST /api/public/contact success")
    
    def test_get_rfq_requests_admin(self, auth_token):
        """GET /api/rfq-requests - admin gets RFQ list"""
        response = requests.get(
            f"{BASE_URL}/api/rfq-requests",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/rfq-requests returns {len(response.json())} requests")
    
    def test_get_contact_messages_admin(self, auth_token):
        """GET /api/contact-messages - admin gets contact messages list"""
        response = requests.get(
            f"{BASE_URL}/api/contact-messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert isinstance(response.json(), list)
        print(f"✓ GET /api/contact-messages returns {len(response.json())} messages")
    
    def test_update_rfq_request_status(self, auth_token):
        """PUT /api/rfq-requests/{id} - update status"""
        # First create an RFQ
        rfq_data = {
            "company_name": "TEST_RFQ_Update",
            "contact_name": "Test",
            "email": "test@example.com",
            "phone": "+966123456789",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        rfq_id = response.json()["id"]
        
        # Update status
        response = requests.put(
            f"{BASE_URL}/api/rfq-requests/{rfq_id}?status=reviewed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ PUT /api/rfq-requests/{rfq_id} status update success")
        
        # Delete
        response = requests.delete(
            f"{BASE_URL}/api/rfq-requests/{rfq_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"✓ DELETE /api/rfq-requests/{rfq_id} success")
    
    def test_rfq_requests_unauthorized(self):
        """GET /api/rfq-requests - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/rfq-requests")
        assert response.status_code == 403
        print(f"✓ Unauthenticated /api/rfq-requests correctly denied")
    
    def test_contact_messages_unauthorized(self):
        """GET /api/contact-messages - without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/contact-messages")
        assert response.status_code == 403
        print(f"✓ Unauthenticated /api/contact-messages correctly denied")


# ================== PDF GENERATION TESTS ==================

class TestPDFGeneration:
    """Test PDF generation endpoints for refactored routes"""
    
    def test_technical_review_pdf(self, auth_token):
        """GET /api/technical-reviews/{id}/pdf - generate PDF"""
        # Create a technical review
        create_data = {
            "client_name": "TEST_PDF_Tech_Review",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/technical-reviews",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        review_id = response.json()["id"]
        
        # Generate PDF
        response = requests.get(
            f"{BASE_URL}/api/technical-reviews/{review_id}/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert "application/pdf" in response.headers.get("Content-Type", "")
        print(f"✓ GET /api/technical-reviews/{review_id}/pdf returns PDF")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/technical-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    def test_customer_feedback_pdf(self, auth_token):
        """GET /api/customer-feedback/{id}/pdf - generate PDF"""
        # Create feedback
        create_data = {
            "organization_name": "TEST_PDF_Feedback",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/customer-feedback",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        feedback_id = response.json()["id"]
        
        # Generate PDF
        response = requests.get(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert "application/pdf" in response.headers.get("Content-Type", "")
        print(f"✓ GET /api/customer-feedback/{feedback_id}/pdf returns PDF")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/customer-feedback/{feedback_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    def test_pre_transfer_review_pdf(self, auth_token):
        """GET /api/pre-transfer-reviews/{id}/pdf - generate PDF"""
        # Create review
        create_data = {
            "client_name": "TEST_PDF_PreTransfer",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/pre-transfer-reviews",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=create_data
        )
        review_id = response.json()["id"]
        
        # Generate PDF
        response = requests.get(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert "application/pdf" in response.headers.get("Content-Type", "")
        print(f"✓ GET /api/pre-transfer-reviews/{review_id}/pdf returns PDF")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/pre-transfer-reviews/{review_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
