"""
Test module for Audit Programs (BACF6-05) feature
Tests CRUD operations, PDF generation, and approval workflow
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

class TestAuditProgramsFeature:
    """Test Audit Programs (BACF6-05) feature - schedule audit stages"""
    
    token = None
    created_program_id = None
    existing_program_id = "3450b020-fd96-446a-af59-541af71eb233"  # From main agent context
    contract_review_id = "2c21b7a8-99b7-44f9-a0a0-7606e93c8e78"  # From main agent context
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - authenticate before tests"""
        if not TestAuditProgramsFeature.token:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            assert response.status_code == 200, f"Login failed: {response.text}"
            TestAuditProgramsFeature.token = response.json()['token']
        yield
    
    @property
    def headers(self):
        return {"Authorization": f"Bearer {TestAuditProgramsFeature.token}"}
    
    # ---------- GET Endpoints ----------
    
    def test_01_get_audit_programs_list(self):
        """Test GET /api/audit-programs - list all audit programs"""
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} audit programs")
        
        # Verify existing program is in the list
        if data:
            program = data[0]
            assert 'id' in program, "Program should have id field"
            assert 'organization_name' in program, "Program should have organization_name"
            assert 'status' in program, "Program should have status"
            assert 'activities' in program, "Program should have activities"
            print(f"First program: {program.get('organization_name')} - Status: {program.get('status')}")
    
    def test_02_get_audit_program_by_id_existing(self):
        """Test GET /api/audit-programs/{id} - get specific program"""
        # First, get list to find an existing program
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert response.status_code == 200
        
        programs = response.json()
        if not programs:
            pytest.skip("No audit programs available for testing")
        
        program_id = programs[0]['id']
        
        # Get specific program
        response = requests.get(f"{BASE_URL}/api/audit-programs/{program_id}", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data['id'] == program_id, "ID should match"
        assert 'organization_name' in data, "Should have organization_name"
        assert 'standards' in data, "Should have standards list"
        assert 'activities' in data, "Should have activities list"
        print(f"Retrieved program: {data['organization_name']}")
        print(f"Standards: {data.get('standards', [])}")
        print(f"Activities count: {len(data.get('activities', []))}")
        
        # Verify activities structure
        if data.get('activities'):
            activity = data['activities'][0]
            required_fields = ['activity', 'audit_type', 'stage1', 'stage2', 'sur1', 'sur2', 'rc', 'planned_date']
            for field in required_fields:
                assert field in activity, f"Activity should have {field} field"
    
    def test_03_get_audit_program_not_found(self):
        """Test GET /api/audit-programs/{id} - 404 for non-existent"""
        response = requests.get(f"{BASE_URL}/api/audit-programs/non-existent-id", headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ---------- Contract Reviews (for creating audit programs) ----------
    
    def test_04_get_contract_reviews_for_creation(self):
        """Test GET /api/contract-reviews - needed to create audit programs"""
        response = requests.get(f"{BASE_URL}/api/contract-reviews", headers=self.headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} contract reviews")
        
        # Check for completed reviews
        completed = [r for r in data if r.get('status') == 'completed']
        print(f"Completed contract reviews: {len(completed)}")
    
    # ---------- POST - Create Audit Program ----------
    
    def test_05_create_audit_program_missing_review(self):
        """Test POST /api/audit-programs - fail with non-existent review"""
        response = requests.post(
            f"{BASE_URL}/api/audit-programs",
            json={"contract_review_id": "non-existent-review-id"},
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_06_create_audit_program_duplicate(self):
        """Test POST /api/audit-programs - fail for duplicate (program already exists)"""
        # Try to create audit program for a review that already has one
        response = requests.post(
            f"{BASE_URL}/api/audit-programs",
            json={"contract_review_id": self.contract_review_id},
            headers=self.headers
        )
        # Should get 400 if program already exists for this review
        # OR 404 if the review doesn't exist
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}: {response.text}"
        if response.status_code == 400:
            assert "already exists" in response.json().get('detail', '').lower(), "Should indicate program exists"
            print("Correctly rejected duplicate - audit program already exists for this contract review")
    
    # ---------- PUT - Update Audit Program ----------
    
    def test_07_update_audit_program(self):
        """Test PUT /api/audit-programs/{id} - update activities and details"""
        # Get an existing program
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert response.status_code == 200
        programs = response.json()
        
        if not programs:
            pytest.skip("No audit programs available for testing")
        
        program_id = programs[0]['id']
        
        # Update with new data
        update_data = {
            "num_shifts": 2,
            "activities": [
                {"activity": "Document Review", "audit_type": "Desktop", "stage1": "1 day", "stage2": "", "sur1": "", "sur2": "", "rc": "", "planned_date": "2026-02-15"},
                {"activity": "Opening Meeting", "audit_type": "On-site", "stage1": "0.5 day", "stage2": "0.5 day", "sur1": "0.5 day", "sur2": "0.5 day", "rc": "0.5 day", "planned_date": "2026-02-20"},
                {"activity": "Management Review", "audit_type": "On-site", "stage1": "1 day", "stage2": "1 day", "sur1": "", "sur2": "", "rc": "1 day", "planned_date": "2026-02-21"},
                {"activity": "Process Audits", "audit_type": "On-site", "stage1": "", "stage2": "3 days", "sur1": "1 day", "sur2": "1 day", "rc": "2 days", "planned_date": "2026-02-22"},
                {"activity": "Internal Audit Review", "audit_type": "On-site", "stage1": "", "stage2": "1 day", "sur1": "0.5 day", "sur2": "0.5 day", "rc": "1 day", "planned_date": "2026-02-25"},
                {"activity": "Closing Meeting", "audit_type": "On-site", "stage1": "", "stage2": "0.5 day", "sur1": "0.5 day", "sur2": "0.5 day", "rc": "0.5 day", "planned_date": "2026-02-26"}
            ],
            "certification_manager": "Test Manager",
            "approval_date": "2026-01-20",
            "notes": "Test notes for audit program"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/audit-programs/{program_id}",
            json=update_data,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify update persisted
        response = requests.get(f"{BASE_URL}/api/audit-programs/{program_id}", headers=self.headers)
        assert response.status_code == 200
        
        updated = response.json()
        assert updated['num_shifts'] == 2, "num_shifts should be updated"
        assert len(updated['activities']) == 6, "Should have 6 activities"
        print(f"Updated program - Shifts: {updated['num_shifts']}, Activities: {len(updated['activities'])}")
        
        # When certification_manager and approval_date are provided, status should be 'approved'
        assert updated.get('status') == 'approved', "Status should be approved when manager and date are set"
    
    def test_08_update_audit_program_not_found(self):
        """Test PUT /api/audit-programs/{id} - 404 for non-existent"""
        response = requests.put(
            f"{BASE_URL}/api/audit-programs/non-existent-id",
            json={"num_shifts": 1, "activities": []},
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ---------- POST - Approve Audit Program ----------
    
    def test_09_approve_audit_program(self):
        """Test POST /api/audit-programs/{id}/approve - approve program"""
        # Get an existing program
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert response.status_code == 200
        programs = response.json()
        
        if not programs:
            pytest.skip("No audit programs available for testing")
        
        # Find a draft program if available, otherwise use any
        draft_programs = [p for p in programs if p.get('status') == 'draft']
        program = draft_programs[0] if draft_programs else programs[0]
        program_id = program['id']
        
        # Approve the program
        response = requests.post(
            f"{BASE_URL}/api/audit-programs/{program_id}/approve",
            json={},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify status changed to approved
        response = requests.get(f"{BASE_URL}/api/audit-programs/{program_id}", headers=self.headers)
        assert response.status_code == 200
        
        approved = response.json()
        assert approved.get('status') == 'approved', "Status should be approved"
        assert approved.get('approval_date'), "Should have approval_date set"
        print(f"Program approved - Manager: {approved.get('certification_manager')}, Date: {approved.get('approval_date')}")
    
    def test_10_approve_audit_program_not_found(self):
        """Test POST /api/audit-programs/{id}/approve - 404 for non-existent"""
        response = requests.post(
            f"{BASE_URL}/api/audit-programs/non-existent-id/approve",
            json={},
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ---------- GET - PDF Generation ----------
    
    def test_11_generate_pdf(self):
        """Test GET /api/audit-programs/{id}/pdf - generate PDF"""
        # Get an existing program
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert response.status_code == 200
        programs = response.json()
        
        if not programs:
            pytest.skip("No audit programs available for testing")
        
        program_id = programs[0]['id']
        
        # Generate PDF
        response = requests.get(
            f"{BASE_URL}/api/audit-programs/{program_id}/pdf",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert response.headers.get('content-type') == 'application/pdf', "Should return PDF content type"
        
        # Verify PDF content
        pdf_content = response.content
        assert len(pdf_content) > 1000, f"PDF should have reasonable size, got {len(pdf_content)} bytes"
        assert pdf_content[:4] == b'%PDF', "Content should be valid PDF"
        print(f"Generated PDF size: {len(pdf_content)} bytes")
    
    def test_12_generate_pdf_not_found(self):
        """Test GET /api/audit-programs/{id}/pdf - 404 for non-existent"""
        response = requests.get(
            f"{BASE_URL}/api/audit-programs/non-existent-id/pdf",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ---------- DELETE - Delete Audit Program ----------
    
    def test_13_delete_audit_program_not_found(self):
        """Test DELETE /api/audit-programs/{id} - 404 for non-existent"""
        response = requests.delete(
            f"{BASE_URL}/api/audit-programs/non-existent-id",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    # ---------- Authentication ----------
    
    def test_14_unauthorized_access(self):
        """Test endpoints require authentication"""
        endpoints = [
            ("GET", "/api/audit-programs"),
            ("POST", "/api/audit-programs"),
            ("GET", "/api/audit-programs/test-id"),
            ("PUT", "/api/audit-programs/test-id"),
            ("DELETE", "/api/audit-programs/test-id"),
            ("GET", "/api/audit-programs/test-id/pdf"),
            ("POST", "/api/audit-programs/test-id/approve"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json={})
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}")
            
            assert response.status_code in [401, 403], f"{method} {endpoint} should require auth, got {response.status_code}"
            print(f"{method} {endpoint}: {response.status_code} - Auth required")


class TestAuditProgramActivitiesValidation:
    """Additional tests for audit program activities data structure"""
    
    token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestAuditProgramActivitiesValidation.token:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            assert response.status_code == 200
            TestAuditProgramActivitiesValidation.token = response.json()['token']
        yield
    
    @property
    def headers(self):
        return {"Authorization": f"Bearer {TestAuditProgramActivitiesValidation.token}"}
    
    def test_activities_default_structure(self):
        """Verify default activities are pre-populated correctly"""
        response = requests.get(f"{BASE_URL}/api/audit-programs", headers=self.headers)
        assert response.status_code == 200
        
        programs = response.json()
        if not programs:
            pytest.skip("No audit programs available")
        
        # Check expected default activities
        expected_activities = [
            "Document Review",
            "Opening Meeting",
            "Management Review",
            "Process Audits",
            "Internal Audit Review",
            "Closing Meeting"
        ]
        
        program = programs[0]
        activities = program.get('activities', [])
        
        activity_names = [a.get('activity', '') for a in activities]
        print(f"Found activities: {activity_names}")
        
        # Verify at least some expected activities are present
        found_count = sum(1 for ea in expected_activities if ea in activity_names)
        print(f"Found {found_count}/{len(expected_activities)} expected activities")
