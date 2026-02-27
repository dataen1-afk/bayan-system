"""
Job Orders (BACF6-06) Backend API Tests
Tests the full workflow: create job order → approve → send to auditor → auditor confirms/declines
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-audit-flow.preview.emergentagent.com')

class TestJobOrdersAPI:
    """Test Job Order CRUD operations and workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    # ========== LIST JOB ORDERS ==========
    def test_list_job_orders(self):
        """GET /api/job-orders - list all job orders"""
        response = requests.get(f"{BASE_URL}/api/job-orders", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} job orders")
    
    # ========== GET EXISTING JOB ORDER ==========
    def test_get_existing_job_order(self):
        """GET /api/job-orders/{id} - get existing job order by ID"""
        order_id = "132bc0dc-a699-47dc-b4eb-94ef8f8c3273"
        response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["auditor_name"] == "Ahmed Al-Rashid"
        assert data["auditor_name_ar"] == "أحمد الراشد"
        assert data["position"] == "Lead Auditor"
        assert data["organization_name"] == "Test Company for Proposal"
        assert "ISO9001" in data["standards"]
        assert data["manager_approved"] == True
        assert data["status"] == "pending_auditor"
        print(f"Job order details verified: {data['auditor_name']} - {data['organization_name']}")
    
    # ========== TEST PDF GENERATION ==========
    def test_get_job_order_pdf(self):
        """GET /api/job-orders/{id}/pdf - generate PDF"""
        order_id = "132bc0dc-a699-47dc-b4eb-94ef8f8c3273"
        response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}/pdf", headers=self.headers)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 50000, "PDF should be at least 50KB"
        print(f"PDF generated successfully: {len(response.content)} bytes")
    
    # ========== SEND TO AUDITOR ==========
    def test_send_to_auditor(self):
        """POST /api/job-orders/{id}/send-to-auditor - get confirmation link"""
        order_id = "132bc0dc-a699-47dc-b4eb-94ef8f8c3273"
        response = requests.post(f"{BASE_URL}/api/job-orders/{order_id}/send-to-auditor", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "link" in data
        assert "job-order-confirm" in data["link"]
        print(f"Auditor confirmation link: {data['link']}")
    
    # ========== PUBLIC ACCESS TESTS ==========
    def test_public_job_order_access(self):
        """GET /api/public/job-orders/{token} - public access for auditor"""
        access_token = "07f9a708-f65f-4810-9626-6d701eaf931d"
        response = requests.get(f"{BASE_URL}/api/public/job-orders/{access_token}")
        assert response.status_code == 200
        data = response.json()
        assert data["auditor_name"] == "Ahmed Al-Rashid"
        assert data["organization_name"] == "Test Company for Proposal"
        assert data["position"] == "Lead Auditor"
        assert data["status"] == "pending_auditor"
        assert data["certification_manager"] == "Admin"
        print(f"Public access verified for auditor: {data['auditor_name']}")
    
    def test_public_job_order_invalid_token(self):
        """GET /api/public/job-orders/{token} - invalid token returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/job-orders/invalid-token-12345")
        assert response.status_code == 404
        print("Invalid token correctly returns 404")
    
    # ========== CREATE JOB ORDER ==========
    def test_create_job_order(self):
        """POST /api/job-orders - create new job order"""
        # Get approved audit program and active auditor
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert programs_response.status_code == 200
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        assert auditors_response.status_code == 200
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not approved_programs:
            pytest.skip("No approved audit programs available")
        if not active_auditors:
            pytest.skip("No active auditors available")
        
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": active_auditors[0]["id"],
            "position": "Auditor",
            "audit_type": "Stage 1",
            "audit_date": "2026-04-15"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "access_token" in data
        
        # Verify created order
        order_response = requests.get(f"{BASE_URL}/api/job-orders/{data['id']}", headers=self.headers)
        assert order_response.status_code == 200
        order_data = order_response.json()
        assert order_data["position"] == "Auditor"
        assert order_data["audit_type"] == "Stage 1"
        assert order_data["audit_date"] == "2026-04-15"
        assert order_data["status"] == "pending_approval"
        
        # Store for cleanup
        self.test_job_order_id = data['id']
        print(f"Created job order: {data['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/job-orders/{data['id']}", headers=self.headers)
    
    # ========== APPROVE JOB ORDER ==========
    def test_approve_job_order_workflow(self):
        """Test approve job order workflow"""
        # Get approved audit program and active auditor
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not approved_programs or not active_auditors:
            pytest.skip("Need approved program and active auditor")
        
        # Create a new order
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": active_auditors[0]["id"],
            "position": "Technical Expert",
            "audit_type": "Recertification",
            "audit_date": "2026-05-20"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        assert create_response.status_code == 200
        order_id = create_response.json()["id"]
        
        # Verify it's pending approval
        get_response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        assert get_response.json()["status"] == "pending_approval"
        assert get_response.json()["manager_approved"] == False
        
        # Approve it
        approve_response = requests.post(f"{BASE_URL}/api/job-orders/{order_id}/approve", headers=self.headers)
        assert approve_response.status_code == 200
        
        # Verify it's now pending_auditor
        get_response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        assert get_response.json()["status"] == "pending_auditor"
        assert get_response.json()["manager_approved"] == True
        print(f"Approve workflow completed for order: {order_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
    
    # ========== AUDITOR CONFIRMATION ==========
    def test_auditor_confirm_workflow(self):
        """Test auditor confirmation via public endpoint"""
        # Get approved audit program and active auditor
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not approved_programs or not active_auditors:
            pytest.skip("Need approved program and active auditor")
        
        # Create and approve order
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": active_auditors[0]["id"],
            "position": "Lead Auditor",
            "audit_type": "Stage 2",
            "audit_date": "2026-06-10"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        order_data = create_response.json()
        order_id = order_data["id"]
        access_token = order_data["access_token"]
        
        # Approve
        requests.post(f"{BASE_URL}/api/job-orders/{order_id}/approve", headers=self.headers)
        
        # Auditor confirms via public endpoint
        confirm_response = requests.post(
            f"{BASE_URL}/api/public/job-orders/{access_token}/confirm",
            json={"confirmed": True, "unable_reason": ""}
        )
        assert confirm_response.status_code == 200
        
        # Verify it's confirmed
        get_response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        order = get_response.json()
        assert order["status"] == "confirmed"
        assert order["auditor_confirmed"] == True
        print(f"Auditor confirmed order: {order_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
    
    def test_auditor_decline_workflow(self):
        """Test auditor decline with reason"""
        # Get approved audit program and active auditor
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not approved_programs or not active_auditors:
            pytest.skip("Need approved program and active auditor")
        
        # Create and approve order
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": active_auditors[0]["id"],
            "position": "Auditor",
            "audit_type": "Surveillance 1",
            "audit_date": "2026-07-15"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        order_data = create_response.json()
        order_id = order_data["id"]
        access_token = order_data["access_token"]
        
        # Approve
        requests.post(f"{BASE_URL}/api/job-orders/{order_id}/approve", headers=self.headers)
        
        # Auditor declines with reason
        decline_reason = "TEST_Schedule conflict with another commitment"
        decline_response = requests.post(
            f"{BASE_URL}/api/public/job-orders/{access_token}/confirm",
            json={"confirmed": False, "unable_reason": decline_reason}
        )
        assert decline_response.status_code == 200
        
        # Verify it's rejected
        get_response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        order = get_response.json()
        assert order["status"] == "rejected"
        assert order["auditor_confirmed"] == False
        assert order["unable_reason"] == decline_reason
        print(f"Auditor declined order: {order_id} - Reason: {decline_reason}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
    
    # ========== DELETE JOB ORDER ==========
    def test_delete_job_order(self):
        """DELETE /api/job-orders/{id} - delete job order"""
        # Create a test order first
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not approved_programs or not active_auditors:
            pytest.skip("Need approved program and active auditor")
        
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": active_auditors[0]["id"],
            "position": "Auditor",
            "audit_type": "Stage 1",
            "audit_date": "2026-08-01"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        order_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/job-orders/{order_id}", headers=self.headers)
        assert get_response.status_code == 404
        print(f"Deleted job order: {order_id}")
    
    # ========== EDGE CASES ==========
    def test_get_nonexistent_job_order(self):
        """GET /api/job-orders/{id} - returns 404 for non-existent order"""
        response = requests.get(f"{BASE_URL}/api/job-orders/nonexistent-id-12345", headers=self.headers)
        assert response.status_code == 404
        print("Non-existent job order correctly returns 404")
    
    def test_create_job_order_invalid_auditor(self):
        """POST /api/job-orders - fails with invalid auditor ID"""
        programs_response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        programs = programs_response.json()
        approved_programs = [p for p in programs if p["status"] == "approved"]
        
        if not approved_programs:
            pytest.skip("No approved audit programs available")
        
        payload = {
            "audit_program_id": approved_programs[0]["id"],
            "auditor_id": "invalid-auditor-id-12345",
            "position": "Auditor",
            "audit_type": "Stage 1",
            "audit_date": "2026-09-01"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        assert response.status_code == 404
        print("Invalid auditor ID correctly returns 404")
    
    def test_create_job_order_invalid_program(self):
        """POST /api/job-orders - fails with invalid audit program ID"""
        auditors_response = requests.get(f"{BASE_URL}/api/auditors", headers=self.headers)
        auditors = auditors_response.json()
        active_auditors = [a for a in auditors if a["status"] == "active"]
        
        if not active_auditors:
            pytest.skip("No active auditors available")
        
        payload = {
            "audit_program_id": "invalid-program-id-12345",
            "auditor_id": active_auditors[0]["id"],
            "position": "Auditor",
            "audit_type": "Stage 1",
            "audit_date": "2026-09-15"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-orders", json=payload, headers=self.headers)
        assert response.status_code == 404
        print("Invalid program ID correctly returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
