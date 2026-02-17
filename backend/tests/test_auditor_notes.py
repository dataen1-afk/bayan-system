"""
Auditor Notes (BACF6-12) API Tests
Tests for creating, reading, updating, deleting auditor notes and PDF generation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuditorNotesAPI:
    """Test Auditor Notes (BACF6-12) CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    # ============= MANUAL CREATION TESTS =============
    
    def test_create_auditor_notes_manually(self, headers):
        """Test creating auditor notes manually without Stage 2 report"""
        payload = {
            "client_name": "TEST_Manual Client LLC",
            "location": "Riyadh, Saudi Arabia",
            "standards": ["ISO 9001:2015", "ISO 14001:2015"],
            "auditor_name": "Ahmed Al-Auditor",
            "audit_type": "Stage 2",
            "audit_date": "2026-01-20",
            "department": "Quality Management"
        }
        
        response = requests.post(f"{BASE_URL}/api/auditor-notes", json=payload, headers=headers)
        
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "Response should have id"
        assert data["client_name"] == payload["client_name"], "Client name should match"
        assert data["location"] == payload["location"], "Location should match"
        assert data["standards"] == payload["standards"], "Standards should match"
        assert data["auditor_name"] == payload["auditor_name"], "Auditor name should match"
        assert data["audit_type"] == payload["audit_type"], "Audit type should match"
        assert data["audit_date"] == payload["audit_date"], "Audit date should match"
        assert data["department"] == payload["department"], "Department should match"
        assert data["status"] == "draft", "Initial status should be draft"
        
        # Store for later tests
        self.__class__.manual_notes_id = data["id"]
        
        return data
    
    def test_get_auditor_notes_list(self, headers):
        """Test getting list of all auditor notes"""
        response = requests.get(f"{BASE_URL}/api/auditor-notes", headers=headers)
        
        assert response.status_code == 200, f"Get list failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        # Should have at least one note from our create test
        assert len(data) >= 1, "Should have at least one auditor note"
        
        # Verify structure of first item
        if data:
            note = data[0]
            assert "id" in note, "Note should have id"
            assert "client_name" in note, "Note should have client_name"
            assert "status" in note, "Note should have status"
    
    def test_get_auditor_notes_by_id(self, headers):
        """Test getting specific auditor notes by ID"""
        notes_id = getattr(self.__class__, 'manual_notes_id', None)
        if not notes_id:
            pytest.skip("No manual notes ID from previous test")
        
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        
        assert response.status_code == 200, f"Get by ID failed: {response.text}"
        data = response.json()
        
        assert data["id"] == notes_id, "ID should match requested ID"
        assert data["client_name"] == "TEST_Manual Client LLC", "Client name should match"
    
    def test_update_auditor_notes_content(self, headers):
        """Test updating auditor notes - specifically the notes content"""
        notes_id = getattr(self.__class__, 'manual_notes_id', None)
        if not notes_id:
            pytest.skip("No manual notes ID from previous test")
        
        update_payload = {
            "notes": "This is the audit finding note content.\n\n- Finding 1: Documentation is complete\n- Finding 2: Process controls are adequate\n- Finding 3: Training records updated",
            "notes_ar": "هذه ملاحظات التدقيق",
            "department": "Updated QA Department"
        }
        
        response = requests.put(f"{BASE_URL}/api/auditor-notes/{notes_id}", json=update_payload, headers=headers)
        
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        
        assert data["notes"] == update_payload["notes"], "Notes should be updated"
        assert data["notes_ar"] == update_payload["notes_ar"], "Arabic notes should be updated"
        assert data["department"] == update_payload["department"], "Department should be updated"
        assert "updated_at" in data, "Should have updated_at timestamp"
        
        # Verify with GET
        verify_response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["notes"] == update_payload["notes"], "Notes should persist after update"
    
    def test_mark_auditor_notes_completed(self, headers):
        """Test marking auditor notes as completed"""
        notes_id = getattr(self.__class__, 'manual_notes_id', None)
        if not notes_id:
            pytest.skip("No manual notes ID from previous test")
        
        response = requests.post(f"{BASE_URL}/api/auditor-notes/{notes_id}/complete", headers=headers)
        
        assert response.status_code == 200, f"Complete failed: {response.text}"
        data = response.json()
        assert "message" in data, "Response should have message"
        
        # Verify status changed
        verify_response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["status"] == "completed", "Status should be completed"
        assert "completed_at" in verify_data, "Should have completed_at timestamp"
    
    def test_download_auditor_notes_pdf(self, headers):
        """Test downloading PDF for auditor notes"""
        notes_id = getattr(self.__class__, 'manual_notes_id', None)
        if not notes_id:
            pytest.skip("No manual notes ID from previous test")
        
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}/pdf", headers=headers)
        
        assert response.status_code == 200, f"PDF download failed: {response.text}"
        assert "application/pdf" in response.headers.get("content-type", ""), "Should return PDF content type"
        
        # Verify PDF content
        pdf_content = response.content
        assert len(pdf_content) > 1000, f"PDF should have substantial content, got {len(pdf_content)} bytes"
        assert pdf_content[:4] == b'%PDF', "Should start with PDF magic bytes"
    
    def test_delete_auditor_notes(self, headers):
        """Test deleting auditor notes"""
        notes_id = getattr(self.__class__, 'manual_notes_id', None)
        if not notes_id:
            pytest.skip("No manual notes ID from previous test")
        
        response = requests.delete(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        
        assert response.status_code == 200, f"Delete failed: {response.text}"
        data = response.json()
        assert "message" in data, "Response should have message"
        
        # Verify deletion with GET - should return 404
        verify_response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        assert verify_response.status_code == 404, "Should return 404 after deletion"
    
    # ============= ERROR HANDLING TESTS =============
    
    def test_get_nonexistent_auditor_notes(self, headers):
        """Test getting non-existent auditor notes returns 404"""
        fake_id = "nonexistent-id-12345"
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{fake_id}", headers=headers)
        
        assert response.status_code == 404, "Should return 404 for non-existent notes"
    
    def test_update_nonexistent_auditor_notes(self, headers):
        """Test updating non-existent auditor notes returns 404"""
        fake_id = "nonexistent-id-12345"
        response = requests.put(f"{BASE_URL}/api/auditor-notes/{fake_id}", json={"notes": "test"}, headers=headers)
        
        assert response.status_code == 404, "Should return 404 for non-existent notes"
    
    def test_complete_nonexistent_auditor_notes(self, headers):
        """Test completing non-existent auditor notes returns 404"""
        fake_id = "nonexistent-id-12345"
        response = requests.post(f"{BASE_URL}/api/auditor-notes/{fake_id}/complete", headers=headers)
        
        assert response.status_code == 404, "Should return 404 for non-existent notes"
    
    def test_pdf_nonexistent_auditor_notes(self, headers):
        """Test PDF generation for non-existent auditor notes returns 404"""
        fake_id = "nonexistent-id-12345"
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{fake_id}/pdf", headers=headers)
        
        assert response.status_code == 404, "Should return 404 for non-existent notes"
    
    def test_delete_nonexistent_auditor_notes(self, headers):
        """Test deleting non-existent auditor notes returns 404"""
        fake_id = "nonexistent-id-12345"
        response = requests.delete(f"{BASE_URL}/api/auditor-notes/{fake_id}", headers=headers)
        
        assert response.status_code == 404, "Should return 404 for non-existent notes"
    
    def test_unauthorized_access(self):
        """Test accessing auditor notes without auth returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/auditor-notes")
        
        assert response.status_code in [401, 403], "Should return 401 or 403 without auth"


class TestAuditorNotesFromStage2Report:
    """Test creating Auditor Notes from Stage 2 Report"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_stage2_reports_for_selection(self, headers):
        """Test fetching Stage 2 reports - used to select for creating auditor notes"""
        response = requests.get(f"{BASE_URL}/api/stage2-audit-reports", headers=headers)
        
        assert response.status_code == 200, f"Get Stage 2 reports failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        # Store any approved report for next test
        approved_reports = [r for r in data if r.get("status") == "approved"]
        if approved_reports:
            self.__class__.stage2_report_id = approved_reports[0]["id"]
            self.__class__.stage2_report = approved_reports[0]
        else:
            # Store any report for testing
            if data:
                self.__class__.stage2_report_id = data[0]["id"]
                self.__class__.stage2_report = data[0]
    
    def test_create_auditor_notes_from_stage2_report(self, headers):
        """Test creating auditor notes from a Stage 2 report"""
        report_id = getattr(self.__class__, 'stage2_report_id', None)
        if not report_id:
            pytest.skip("No Stage 2 report available to create auditor notes from")
        
        payload = {
            "stage2_report_id": report_id
        }
        
        response = requests.post(f"{BASE_URL}/api/auditor-notes", json=payload, headers=headers)
        
        assert response.status_code == 200, f"Create from report failed: {response.text}"
        data = response.json()
        
        # Verify data was pulled from Stage 2 report
        assert "id" in data, "Response should have id"
        assert data["stage2_report_id"] == report_id, "Should have stage2_report_id"
        
        # Store for cleanup
        self.__class__.notes_from_report_id = data["id"]
        
        return data
    
    def test_cleanup_created_notes(self, headers):
        """Cleanup test data created from Stage 2 report"""
        notes_id = getattr(self.__class__, 'notes_from_report_id', None)
        if notes_id:
            response = requests.delete(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
            # Don't fail if already deleted
            assert response.status_code in [200, 404]


class TestAuditorNotesFullWorkflow:
    """Test complete workflow: create -> update -> complete -> pdf -> delete"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_01_create_notes(self, headers):
        """Step 1: Create auditor notes"""
        payload = {
            "client_name": "TEST_Workflow Client Corp",
            "location": "Jeddah, Saudi Arabia",
            "standards": ["ISO 45001:2018"],
            "auditor_name": "Mohammed Al-Workflow",
            "audit_type": "Surveillance 1",
            "audit_date": "2026-01-25",
            "department": "Operations"
        }
        
        response = requests.post(f"{BASE_URL}/api/auditor-notes", json=payload, headers=headers)
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        self.__class__.workflow_notes_id = data["id"]
        
        assert data["status"] == "draft", "Initial status should be draft"
    
    def test_02_update_notes_content(self, headers):
        """Step 2: Add notes content"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if not notes_id:
            pytest.skip("No notes ID from step 1")
        
        update_payload = {
            "notes": "Surveillance audit completed.\n\nObservations:\n- Safety procedures well documented\n- Emergency drills conducted regularly\n- PPE usage compliance at 95%\n\nRecommendations:\n- Continue monitoring incident reports\n- Update risk assessment annually"
        }
        
        response = requests.put(f"{BASE_URL}/api/auditor-notes/{notes_id}", json=update_payload, headers=headers)
        assert response.status_code == 200, f"Update failed: {response.text}"
    
    def test_03_verify_before_complete(self, headers):
        """Step 3: Verify data before marking complete"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if not notes_id:
            pytest.skip("No notes ID from step 1")
        
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "draft", "Status should still be draft"
        assert "Surveillance audit completed" in data["notes"], "Notes content should be saved"
    
    def test_04_generate_pdf_draft(self, headers):
        """Step 4: Generate PDF while still in draft"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if not notes_id:
            pytest.skip("No notes ID from step 1")
        
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}/pdf", headers=headers)
        assert response.status_code == 200, "PDF should be generated even for draft notes"
        assert "application/pdf" in response.headers.get("content-type", "")
    
    def test_05_mark_complete(self, headers):
        """Step 5: Mark notes as completed"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if not notes_id:
            pytest.skip("No notes ID from step 1")
        
        response = requests.post(f"{BASE_URL}/api/auditor-notes/{notes_id}/complete", headers=headers)
        assert response.status_code == 200, f"Complete failed: {response.text}"
        
        # Verify status
        verify_response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
        assert verify_response.json()["status"] == "completed"
    
    def test_06_generate_pdf_completed(self, headers):
        """Step 6: Generate PDF for completed notes"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if not notes_id:
            pytest.skip("No notes ID from step 1")
        
        response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}/pdf", headers=headers)
        assert response.status_code == 200
        
        pdf_content = response.content
        assert len(pdf_content) > 5000, f"Completed notes PDF should be substantial, got {len(pdf_content)} bytes"
    
    def test_07_cleanup(self, headers):
        """Step 7: Cleanup test data"""
        notes_id = getattr(self.__class__, 'workflow_notes_id', None)
        if notes_id:
            response = requests.delete(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
            assert response.status_code == 200, f"Cleanup delete failed: {response.text}"
            
            # Verify deletion
            verify_response = requests.get(f"{BASE_URL}/api/auditor-notes/{notes_id}", headers=headers)
            assert verify_response.status_code == 404, "Notes should be deleted"
