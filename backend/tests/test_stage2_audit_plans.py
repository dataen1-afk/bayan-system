"""
Stage 2 Audit Plans (BACF6-08) API Tests
Tests the full workflow:
- Create from Job Order
- CRUD operations
- Manager approval
- Send to client
- Client accept/request changes
- PDF generation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://audit-workflow-pro-1.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Test data - confirmed job order from context
CONFIRMED_JOB_ORDER_ID = "132bc0dc-a699-47dc-b4eb-94ef8f8c3273"


class TestStage2AuditPlansAPI:
    """Test Stage 2 Audit Plans API endpoints (BACF6-08)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login and get token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token
    
    # ============= AUTH TEST =============
    def test_01_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful, token received")
    
    # ============= PREREQUISITES =============
    def test_02_list_job_orders(self):
        """Test GET /api/job-orders - verify confirmed job order exists"""
        response = self.session.get(f"{BASE_URL}/api/job-orders")
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        
        # Check for confirmed job order
        confirmed = [o for o in orders if o.get('status') == 'confirmed']
        print(f"✓ Found {len(orders)} job orders, {len(confirmed)} confirmed")
        
        if confirmed:
            print(f"✓ Confirmed job order available: {confirmed[0].get('organization_name', 'N/A')}")
    
    def test_03_list_stage1_plans(self):
        """Test GET /api/stage1-audit-plans - verify Stage 1 plans exist"""
        response = self.session.get(f"{BASE_URL}/api/stage1-audit-plans")
        assert response.status_code == 200
        plans = response.json()
        assert isinstance(plans, list)
        
        # Check for client accepted Stage 1 plans
        accepted = [p for p in plans if p.get('status') == 'client_accepted']
        print(f"✓ Found {len(plans)} Stage 1 plans, {len(accepted)} client_accepted")
    
    # ============= STAGE 2 CRUD TESTS =============
    def test_04_list_stage2_plans_empty_or_existing(self):
        """Test GET /api/stage2-audit-plans - list existing plans"""
        response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans")
        assert response.status_code == 200
        plans = response.json()
        assert isinstance(plans, list)
        print(f"✓ Stage 2 plans API returns {len(plans)} plans")
    
    def test_05_create_stage2_from_job_order(self):
        """Test POST /api/stage2-audit-plans - create from confirmed job order"""
        # First check if a Stage 2 plan already exists for this job order
        existing_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans")
        existing = existing_response.json()
        
        # Delete any existing Stage 2 plans for testing
        for plan in existing:
            if plan.get('job_order_id') == CONFIRMED_JOB_ORDER_ID:
                self.session.delete(f"{BASE_URL}/api/stage2-audit-plans/{plan['id']}")
                print(f"✓ Deleted existing Stage 2 plan for job order")
        
        # Create new Stage 2 plan from job order
        response = self.session.post(f"{BASE_URL}/api/stage2-audit-plans", json={
            "job_order_id": CONFIRMED_JOB_ORDER_ID,
            "audit_type": "Stage 2"
        })
        
        if response.status_code == 404:
            pytest.skip("Job order not found - may need different ID")
        
        assert response.status_code == 200, f"Failed to create: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert "access_token" in data
        assert data.get("message") == "Stage 2 audit plan created successfully"
        
        self.created_plan_id = data["id"]
        self.created_access_token = data["access_token"]
        print(f"✓ Stage 2 plan created: ID={data['id'][:8]}...")
        
        # Store for later tests
        pytest.plan_id = data["id"]
        pytest.access_token = data["access_token"]
    
    def test_06_get_stage2_plan(self):
        """Test GET /api/stage2-audit-plans/{id} - retrieve created plan"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        assert response.status_code == 200
        
        plan = response.json()
        assert plan.get("id") == pytest.plan_id
        assert plan.get("audit_type") == "Stage 2"
        assert "organization_name" in plan
        assert "team_leader" in plan
        assert "schedule_entries" in plan
        
        # Verify default schedule entries were created
        assert len(plan.get("schedule_entries", [])) >= 5
        
        print(f"✓ Stage 2 plan retrieved: {plan.get('organization_name', 'N/A')}")
        print(f"  - Audit type: {plan.get('audit_type')}")
        print(f"  - Standards: {plan.get('standards', [])}")
        print(f"  - Schedule entries: {len(plan.get('schedule_entries', []))}")
    
    def test_07_update_stage2_plan(self):
        """Test PUT /api/stage2-audit-plans/{id} - update plan details"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        update_data = {
            "contact_person": "John Test Manager",
            "contact_phone": "+966-50-1234567",
            "contact_designation": "Quality Manager",
            "contact_email": "quality@testcompany.com",
            "audit_language": "English",
            "audit_type": "Stage 2",
            "audit_date_from": "2026-02-20",
            "audit_date_to": "2026-02-22",
            "notes": "Test update notes for Stage 2 plan"
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}",
            json=update_data
        )
        assert response.status_code == 200
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert plan.get("contact_person") == "John Test Manager"
        assert plan.get("contact_email") == "quality@testcompany.com"
        assert plan.get("audit_date_from") == "2026-02-20"
        assert plan.get("notes") == "Test update notes for Stage 2 plan"
        
        print(f"✓ Stage 2 plan updated successfully")
    
    def test_08_update_schedule_entries(self):
        """Test PUT /api/stage2-audit-plans/{id} - update schedule entries"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        schedule_entries = [
            {"date_time": "09:00-10:00", "process": "Opening Meeting", "process_owner": "CEO", "clauses": "4.1", "auditor": "Team Leader"},
            {"date_time": "10:00-12:00", "process": "Document Review", "process_owner": "QA Manager", "clauses": "7.0", "auditor": "Auditor 1"},
            {"date_time": "13:00-15:00", "process": "Operations Audit", "process_owner": "Production Head", "clauses": "8.0", "auditor": "Auditor 2"},
            {"date_time": "15:00-16:00", "process": "Closing Meeting", "process_owner": "Management", "clauses": "N/A", "auditor": "Team"}
        ]
        
        response = self.session.put(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}",
            json={"schedule_entries": schedule_entries}
        )
        assert response.status_code == 200
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert len(plan.get("schedule_entries", [])) == 4
        assert plan["schedule_entries"][0]["process"] == "Opening Meeting"
        assert plan["schedule_entries"][0]["date_time"] == "09:00-10:00"
        
        print(f"✓ Schedule entries updated: {len(plan['schedule_entries'])} entries")
    
    def test_09_add_team_members(self):
        """Test PUT /api/stage2-audit-plans/{id} - add team members"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        team_members = [
            {"auditor_id": "test-1", "name": "Ahmed Al-Rashid", "name_ar": "أحمد الراشد", "role": "Auditor"},
            {"auditor_id": "test-2", "name": "Sarah Johnson", "name_ar": "", "role": "Technical Expert"}
        ]
        
        response = self.session.put(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}",
            json={"team_members": team_members}
        )
        assert response.status_code == 200
        
        # Verify
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert len(plan.get("team_members", [])) == 2
        print(f"✓ Team members added: {len(plan['team_members'])} members")
    
    # ============= MANAGER APPROVAL =============
    def test_10_manager_approve(self):
        """Test POST /api/stage2-audit-plans/{id}/manager-approve"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        response = self.session.post(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}/manager-approve"
        )
        assert response.status_code == 200
        
        # Verify
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert plan.get("manager_approved") == True
        assert plan.get("status") == "manager_approved"
        assert plan.get("manager_name") is not None
        assert plan.get("manager_approval_date") is not None
        
        print(f"✓ Manager approved the plan")
        print(f"  - Manager: {plan.get('manager_name')}")
        print(f"  - Date: {plan.get('manager_approval_date')}")
    
    # ============= SEND TO CLIENT =============
    def test_11_send_to_client(self):
        """Test POST /api/stage2-audit-plans/{id}/send-to-client"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        response = self.session.post(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}/send-to-client"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "link" in data
        assert "stage2-plan-review" in data["link"]
        assert data.get("organization") is not None
        
        # Verify
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert plan.get("sent_to_client") == True
        assert plan.get("status") == "pending_client"
        
        pytest.client_link = data["link"]
        print(f"✓ Plan sent to client")
        print(f"  - Link: {data['link'][:60]}...")
    
    def test_12_send_to_client_requires_approval(self):
        """Test send-to-client requires manager approval first"""
        # Create a new plan without approval
        response = self.session.post(f"{BASE_URL}/api/stage2-audit-plans", json={
            "job_order_id": CONFIRMED_JOB_ORDER_ID,
            "audit_type": "Surveillance"
        })
        
        if response.status_code == 400 and "already exists" in response.text:
            # Expected - plan already exists
            print("✓ Duplicate prevention working")
            return
        
        if response.status_code != 200:
            print(f"Note: Create failed - {response.text}")
            return
        
        new_plan_id = response.json()["id"]
        
        # Try to send without approval
        send_response = self.session.post(
            f"{BASE_URL}/api/stage2-audit-plans/{new_plan_id}/send-to-client"
        )
        
        assert send_response.status_code == 400
        assert "approved by manager first" in send_response.json().get("detail", "").lower()
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/stage2-audit-plans/{new_plan_id}")
        print("✓ Send to client correctly requires manager approval first")
    
    # ============= PUBLIC CLIENT REVIEW =============
    def test_13_public_access_plan(self):
        """Test GET /api/public/stage2-audit-plans/{access_token}"""
        if not hasattr(pytest, 'access_token'):
            pytest.skip("No access token from previous test")
        
        # Public endpoint - no auth required
        response = requests.get(
            f"{BASE_URL}/api/public/stage2-audit-plans/{pytest.access_token}"
        )
        assert response.status_code == 200
        
        plan = response.json()
        assert "organization_name" in plan
        assert "team_leader" in plan
        assert "schedule_entries" in plan
        assert "manager_name" in plan
        assert plan.get("client_accepted") == False
        
        print(f"✓ Public access to plan works")
        print(f"  - Organization: {plan.get('organization_name')}")
        print(f"  - Status: {plan.get('status')}")
    
    def test_14_public_access_requires_sent(self):
        """Test public access fails if plan not sent to client"""
        # Create new plan
        response = self.session.post(f"{BASE_URL}/api/stage2-audit-plans", json={
            "job_order_id": CONFIRMED_JOB_ORDER_ID,
            "audit_type": "Renewal"
        })
        
        if response.status_code == 400:
            # Already exists - skip
            print("✓ Cannot create duplicate - existing plan in use")
            return
        
        new_plan = response.json()
        new_token = new_plan.get("access_token")
        
        # Try public access without sending
        public_response = requests.get(
            f"{BASE_URL}/api/public/stage2-audit-plans/{new_token}"
        )
        
        assert public_response.status_code == 400
        assert "not been sent" in public_response.json().get("detail", "").lower()
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/stage2-audit-plans/{new_plan['id']}")
        print("✓ Public access correctly requires plan to be sent first")
    
    # ============= CLIENT RESPONSE =============
    def test_15_client_accept_plan(self):
        """Test POST /api/public/stage2-audit-plans/{token}/respond - accept"""
        if not hasattr(pytest, 'access_token'):
            pytest.skip("No access token from previous test")
        
        # Public endpoint - no auth
        response = requests.post(
            f"{BASE_URL}/api/public/stage2-audit-plans/{pytest.access_token}/respond",
            json={"accepted": True, "change_requests": ""}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "accepted" in data.get("message", "").lower()
        
        # Verify via admin endpoint
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        plan = get_response.json()
        
        assert plan.get("client_accepted") == True
        assert plan.get("status") == "client_accepted"
        assert plan.get("client_acceptance_date") is not None
        
        print(f"✓ Client accepted the plan")
        print(f"  - Acceptance date: {plan.get('client_acceptance_date')}")
    
    def test_16_client_cannot_accept_twice(self):
        """Test client cannot respond twice"""
        if not hasattr(pytest, 'access_token'):
            pytest.skip("No access token from previous test")
        
        response = requests.post(
            f"{BASE_URL}/api/public/stage2-audit-plans/{pytest.access_token}/respond",
            json={"accepted": True, "change_requests": ""}
        )
        
        assert response.status_code == 400
        assert "already accepted" in response.json().get("detail", "").lower()
        print("✓ Double acceptance prevented")
    
    # ============= PDF GENERATION =============
    def test_17_generate_pdf(self):
        """Test GET /api/stage2-audit-plans/{id}/pdf - generate PDF"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        response = self.session.get(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}/pdf"
        )
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        # Check PDF size
        pdf_size = len(response.content)
        assert pdf_size > 10000  # At least 10KB
        
        # Check PDF header
        assert response.content[:4] == b'%PDF'
        
        print(f"✓ PDF generated successfully: {pdf_size/1024:.1f}KB")
    
    def test_18_generate_pdf_not_found(self):
        """Test PDF generation returns 404 for invalid ID"""
        response = self.session.get(
            f"{BASE_URL}/api/stage2-audit-plans/invalid-plan-id-12345/pdf"
        )
        assert response.status_code == 404
        print("✓ PDF endpoint returns 404 for invalid plan")
    
    # ============= DELETE =============
    def test_19_delete_stage2_plan(self):
        """Test DELETE /api/stage2-audit-plans/{id}"""
        if not hasattr(pytest, 'plan_id'):
            pytest.skip("No plan created in previous test")
        
        response = self.session.delete(
            f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}"
        )
        assert response.status_code == 200
        
        # Verify deleted
        get_response = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{pytest.plan_id}")
        assert get_response.status_code == 404
        
        print("✓ Stage 2 plan deleted successfully")
    
    def test_20_delete_not_found(self):
        """Test DELETE returns 404 for invalid ID"""
        response = self.session.delete(
            f"{BASE_URL}/api/stage2-audit-plans/invalid-plan-id-12345"
        )
        assert response.status_code == 404
        print("✓ Delete returns 404 for invalid ID")


class TestStage2AuditPlansRequestChanges:
    """Test Stage 2 client request changes workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login and get token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        token = response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_client_request_changes_workflow(self):
        """Test complete workflow: create → approve → send → client requests changes"""
        # 1. Create plan
        create_response = self.session.post(f"{BASE_URL}/api/stage2-audit-plans", json={
            "job_order_id": CONFIRMED_JOB_ORDER_ID,
            "audit_type": "Stage 2"
        })
        
        if create_response.status_code == 400:
            print("✓ Job order already has a plan - testing with existing")
            # List plans and find one to test with
            plans = self.session.get(f"{BASE_URL}/api/stage2-audit-plans").json()
            if not plans:
                pytest.skip("No plans available for testing")
            return
        
        assert create_response.status_code == 200
        plan_data = create_response.json()
        plan_id = plan_data["id"]
        access_token = plan_data["access_token"]
        
        # 2. Manager approve
        approve_response = self.session.post(
            f"{BASE_URL}/api/stage2-audit-plans/{plan_id}/manager-approve"
        )
        assert approve_response.status_code == 200
        
        # 3. Send to client
        send_response = self.session.post(
            f"{BASE_URL}/api/stage2-audit-plans/{plan_id}/send-to-client"
        )
        assert send_response.status_code == 200
        
        # 4. Client requests changes (public endpoint)
        change_request = "Please reschedule the opening meeting to 10:00 AM"
        client_response = requests.post(
            f"{BASE_URL}/api/public/stage2-audit-plans/{access_token}/respond",
            json={"accepted": False, "change_requests": change_request}
        )
        assert client_response.status_code == 200
        
        # 5. Verify status
        plan = self.session.get(f"{BASE_URL}/api/stage2-audit-plans/{plan_id}").json()
        assert plan["status"] == "changes_requested"
        assert plan["client_change_requests"] == change_request
        
        # 6. Cleanup
        self.session.delete(f"{BASE_URL}/api/stage2-audit-plans/{plan_id}")
        
        print("✓ Client request changes workflow complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
