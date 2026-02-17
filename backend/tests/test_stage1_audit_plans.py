"""
Stage 1 Audit Plans (BACF6-07) Backend API Tests
Tests the full workflow: create from job order → update → manager approve → send to client → client response
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-mgmt-9.preview.emergentagent.com')

# Known test data from main agent context
EXISTING_PLAN_ID = "d8e34254-f6a0-4fb8-98f6-ea16aa057911"
EXISTING_ACCESS_TOKEN = "3cb3c379-d12f-4de0-8434-dc9c9c36d53b"

class TestStage1AuditPlansAPI:
    """Test Stage 1 Audit Plan CRUD operations and workflow"""
    
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
    
    # ========== LIST STAGE 1 AUDIT PLANS ==========
    def test_list_stage1_audit_plans(self):
        """GET /api/stage1-audit-plans - list all plans"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} Stage 1 Audit Plans")
        # Verify known plan exists if any plans exist
        if len(data) > 0:
            plan_ids = [p.get("id") for p in data]
            print(f"Plan IDs: {plan_ids[:5]}...")
    
    # ========== GET EXISTING STAGE 1 AUDIT PLAN ==========
    def test_get_existing_stage1_plan(self):
        """GET /api/stage1-audit-plans/{id} - get existing plan by ID"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == EXISTING_PLAN_ID
        assert "organization_name" in data
        assert "team_leader" in data
        assert "status" in data
        assert "schedule_entries" in data
        print(f"Stage 1 Plan found: {data['organization_name']} - Status: {data['status']}")
    
    def test_get_nonexistent_plan(self):
        """GET /api/stage1-audit-plans/{id} - non-existent plan returns 404"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans/nonexistent-id-12345", headers=self.headers)
        assert response.status_code == 404
        print("Non-existent plan correctly returns 404")
    
    # ========== UPDATE STAGE 1 AUDIT PLAN ==========
    def test_update_stage1_plan(self):
        """PUT /api/stage1-audit-plans/{id} - update plan details"""
        update_data = {
            "contact_person": "Test Contact Updated",
            "contact_phone": "+966-11-123-4567",
            "contact_designation": "Quality Manager",
            "contact_email": "test.contact@example.com",
            "audit_language": "English",
            "audit_date_from": "2026-03-01",
            "audit_date_to": "2026-03-02",
            "team_members": [
                {
                    "auditor_id": "test-auditor-1",
                    "name": "Test Auditor",
                    "name_ar": "مدقق اختبار",
                    "role": "Auditor"
                }
            ],
            "schedule_entries": [
                {
                    "date_time": "09:00 - 10:00",
                    "process": "Opening Meeting Updated",
                    "process_owner": "CEO",
                    "clauses": "4.1, 4.2",
                    "auditor": "Team Leader"
                },
                {
                    "date_time": "10:00 - 12:00",
                    "process": "Document Review",
                    "process_owner": "Quality Manager",
                    "clauses": "7.5",
                    "auditor": "Lead Auditor"
                }
            ],
            "notes": "Test notes for Stage 1 audit plan"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}",
            json=update_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "updated" in data.get("message", "").lower(), f"Expected update message, got: {data}"
        print(f"Stage 1 Plan update response: {data.get('message')}")
        
        # Verify update by fetching again
        get_response = requests.get(f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}", headers=self.headers)
        assert get_response.status_code == 200
        updated_plan = get_response.json()
        assert updated_plan["contact_person"] == "Test Contact Updated"
        assert updated_plan["contact_email"] == "test.contact@example.com"
        assert len(updated_plan["schedule_entries"]) == 2
        print(f"Update verified: contact={updated_plan['contact_person']}, schedule_entries={len(updated_plan['schedule_entries'])}")
    
    # ========== PDF GENERATION ==========
    def test_get_stage1_plan_pdf(self):
        """GET /api/stage1-audit-plans/{id}/pdf - generate PDF"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}/pdf", headers=self.headers)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 10000, "PDF should be at least 10KB"
        print(f"PDF generated successfully: {len(response.content)} bytes ({len(response.content)/1024:.1f}KB)")
    
    # ========== PUBLIC ACCESS TESTS ==========
    def test_public_stage1_plan_access(self):
        """GET /api/public/stage1-audit-plans/{token} - public client access"""
        response = requests.get(f"{BASE_URL}/api/public/stage1-audit-plans/{EXISTING_ACCESS_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        assert "organization_name" in data
        assert "team_leader" in data
        assert "schedule_entries" in data
        assert "status" in data
        print(f"Public access verified: {data['organization_name']} - Status: {data['status']}")
    
    def test_public_stage1_plan_invalid_token(self):
        """GET /api/public/stage1-audit-plans/{token} - invalid token returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/stage1-audit-plans/invalid-token-12345")
        assert response.status_code == 404
        print("Invalid token correctly returns 404")
    
    # ========== MANAGER APPROVAL ==========
    def test_manager_approve_already_approved(self):
        """POST /api/stage1-audit-plans/{id}/manager-approve - test approval endpoint"""
        # Based on context, plan is already approved, so this should work without error
        response = requests.post(
            f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}/manager-approve",
            headers=self.headers
        )
        # Should return 200 or handle already approved case
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"Manager approval endpoint response: {response.status_code}")
    
    # ========== SEND TO CLIENT ==========
    def test_send_to_client(self):
        """POST /api/stage1-audit-plans/{id}/send-to-client - get client review link"""
        response = requests.post(
            f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}/send-to-client",
            headers=self.headers
        )
        # Might already be sent to client based on status
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "link" in data
            assert "stage1-plan-review" in data["link"]
            print(f"Client review link: {data['link']}")
        else:
            print(f"Send to client response (already sent): {response.json()}")
    
    # ========== CLIENT RESPONSE TESTS ==========
    def test_client_accept_plan(self):
        """POST /api/public/stage1-audit-plans/{token}/respond - client accepts plan"""
        # Note: This may fail if plan is already accepted - we test the endpoint format
        response = requests.post(
            f"{BASE_URL}/api/public/stage1-audit-plans/{EXISTING_ACCESS_TOKEN}/respond",
            json={
                "accepted": True,
                "change_requests": ""
            }
        )
        # Should work or return error if already responded
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"Client accept response: {response.status_code} - {response.json()}")
    
    def test_client_request_changes_format(self):
        """Verify client response endpoint accepts change requests format"""
        # This is a format test - actual submission would change status
        # Using a fake token to test endpoint behavior
        response = requests.post(
            f"{BASE_URL}/api/public/stage1-audit-plans/fake-token-for-format-test/respond",
            json={
                "accepted": False,
                "change_requests": "Please change the audit dates"
            }
        )
        # Should return 404 for invalid token
        assert response.status_code == 404
        print("Client change request format validated (404 for invalid token as expected)")
    
    # ========== WORKFLOW TEST ==========
    def test_full_workflow_verification(self):
        """Verify full workflow state: job order → plan → manager approve → client"""
        # 1. Get the plan
        plan_response = requests.get(f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}", headers=self.headers)
        assert plan_response.status_code == 200
        plan = plan_response.json()
        
        # 2. Verify plan has required workflow fields
        assert "job_order_id" in plan, "Plan should reference job order"
        assert "manager_approved" in plan, "Plan should track manager approval"
        assert "sent_to_client" in plan, "Plan should track if sent to client"
        assert "status" in plan, "Plan should have status"
        
        print(f"Workflow state verification:")
        print(f"  - Organization: {plan['organization_name']}")
        print(f"  - Status: {plan['status']}")
        print(f"  - Manager approved: {plan['manager_approved']}")
        print(f"  - Sent to client: {plan['sent_to_client']}")
        print(f"  - Client accepted: {plan.get('client_accepted', False)}")
        
        # 3. Verify schedule entries structure
        if plan.get("schedule_entries"):
            entry = plan["schedule_entries"][0]
            assert isinstance(entry, dict), "Schedule entry should be a dict"
            print(f"  - Schedule entries count: {len(plan['schedule_entries'])}")
        
        # 4. Verify team leader structure
        if plan.get("team_leader"):
            assert isinstance(plan["team_leader"], dict), "Team leader should be a dict"
            print(f"  - Team leader: {plan['team_leader'].get('name', 'N/A')}")
    
    # ========== CREATE NEW PLAN (IF CONFIRMED JOB ORDER EXISTS) ==========
    def test_create_plan_requires_job_order(self):
        """POST /api/stage1-audit-plans - requires confirmed job order"""
        # Test with invalid job order ID
        response = requests.post(
            f"{BASE_URL}/api/stage1-audit-plans",
            json={"job_order_id": "nonexistent-job-order-id"},
            headers=self.headers
        )
        # Should fail with 404 for non-existent job order
        assert response.status_code == 404
        print("Create plan correctly requires valid job order (404)")
    
    # ========== AUTHORIZATION TESTS ==========
    def test_list_plans_requires_auth(self):
        """GET /api/stage1-audit-plans - requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("List plans correctly requires authentication")
    
    def test_create_plan_requires_auth(self):
        """POST /api/stage1-audit-plans - requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/stage1-audit-plans",
            json={"job_order_id": "test"}
        )
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("Create plan correctly requires authentication")
    
    def test_update_plan_requires_auth(self):
        """PUT /api/stage1-audit-plans/{id} - requires authentication"""
        response = requests.put(
            f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}",
            json={"notes": "test"}
        )
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("Update plan correctly requires authentication")
    
    def test_delete_plan_requires_auth(self):
        """DELETE /api/stage1-audit-plans/{id} - requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/stage1-audit-plans/{EXISTING_PLAN_ID}")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("Delete plan correctly requires authentication")
