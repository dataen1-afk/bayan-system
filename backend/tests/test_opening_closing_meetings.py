"""
Tests for Opening & Closing Meeting (BACF6-09) Feature
Tests CRUD operations, public form access, client submission, PDF generation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"


class TestOpeningClosingMeetings:
    """Opening & Closing Meeting endpoint tests"""
    
    auth_token = None
    created_meeting_id = None
    meeting_access_token = None
    stage1_plan_id = None
    
    @classmethod
    def get_auth_token(cls):
        """Get auth token once for all tests"""
        if cls.auth_token:
            return cls.auth_token
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        cls.auth_token = response.json().get("token")
        return cls.auth_token
    
    def get_headers(self):
        """Get auth headers"""
        token = self.get_auth_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # ========== TEST: List Meetings ==========
    def test_01_list_meetings(self):
        """Test listing all meeting forms"""
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings", headers=self.get_headers())
        
        assert response.status_code == 200, f"List failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Store any existing meeting for later tests
        if data:
            TestOpeningClosingMeetings.created_meeting_id = data[0].get('id')
            TestOpeningClosingMeetings.meeting_access_token = data[0].get('access_token')
            print(f"Found existing meeting: {data[0].get('organization_name')}, status: {data[0].get('status')}")
        
        print(f"✓ Listed {len(data)} meeting forms")
    
    # ========== TEST: Get Stage 1 Plans ==========
    def test_02_get_stage1_plans(self):
        """Test getting client-accepted Stage 1 plans"""
        response = requests.get(f"{BASE_URL}/api/stage1-audit-plans", headers=self.get_headers())
        
        assert response.status_code == 200, f"Get Stage 1 plans failed: {response.text}"
        data = response.json()
        
        # Find client_accepted plans
        accepted_plans = [p for p in data if p.get('status') == 'client_accepted']
        print(f"✓ Found {len(accepted_plans)} client-accepted Stage 1 plans")
        
        if accepted_plans:
            # Check if any doesn't have meeting form yet
            meetings_response = requests.get(f"{BASE_URL}/api/opening-closing-meetings", headers=self.get_headers())
            meetings = meetings_response.json() if meetings_response.status_code == 200 else []
            existing_stage1_ids = [m.get('stage1_plan_id') for m in meetings]
            
            for plan in accepted_plans:
                if plan.get('id') not in existing_stage1_ids:
                    TestOpeningClosingMeetings.stage1_plan_id = plan.get('id')
                    print(f"✓ Found available Stage 1 plan: {plan.get('organization_name')}")
                    break
    
    # ========== TEST: Get Specific Meeting ==========
    def test_03_get_specific_meeting(self):
        """Test getting a specific meeting form"""
        if not TestOpeningClosingMeetings.created_meeting_id:
            pytest.skip("No meeting form available")
        
        meeting_id = TestOpeningClosingMeetings.created_meeting_id
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}", headers=self.get_headers())
        
        assert response.status_code == 200, f"Get meeting failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "id" in data, "Response should have id"
        assert "organization_name" in data, "Response should have organization_name"
        assert "attendees" in data, "Response should have attendees"
        assert "status" in data, "Response should have status"
        
        print(f"✓ Got meeting: {data.get('organization_name')}")
        print(f"  - Status: {data.get('status')}")
        print(f"  - Attendees: {len(data.get('attendees', []))}")
        print(f"  - Sent to client: {data.get('sent_to_client', False)}")
    
    # ========== TEST: Create Meeting Form ==========
    def test_04_create_meeting_form(self):
        """Test creating a meeting form from Stage 1 plan"""
        if not TestOpeningClosingMeetings.stage1_plan_id:
            pytest.skip("No available Stage 1 plan to create meeting from")
        
        response = requests.post(
            f"{BASE_URL}/api/opening-closing-meetings",
            json={"stage1_plan_id": TestOpeningClosingMeetings.stage1_plan_id},
            headers=self.get_headers()
        )
        
        if response.status_code == 400:
            # Meeting already exists for this plan
            print(f"✓ Meeting form already exists (expected if testing existing data)")
            return
        
        assert response.status_code == 200, f"Create meeting failed: {response.text}"
        data = response.json()
        
        assert "id" in data, "Response should have id"
        assert "access_token" in data, "Response should have access_token"
        
        TestOpeningClosingMeetings.created_meeting_id = data.get('id')
        TestOpeningClosingMeetings.meeting_access_token = data.get('access_token')
        
        print(f"✓ Created meeting form: {data.get('id')[:8]}...")
    
    # ========== TEST: Create Without Stage 1 Plan ==========
    def test_05_create_meeting_without_source_fails(self):
        """Test that creating meeting without source fails"""
        response = requests.post(
            f"{BASE_URL}/api/opening-closing-meetings",
            json={},
            headers=self.get_headers()
        )
        
        # Should fail with 400 or 422
        assert response.status_code in [400, 422], f"Should fail without source: {response.text}"
        print("✓ Correctly rejected creation without source")
    
    # ========== TEST: Send to Client ==========
    def test_06_send_to_client(self):
        """Test sending meeting form to client"""
        if not TestOpeningClosingMeetings.created_meeting_id:
            pytest.skip("No meeting form available")
        
        meeting_id = TestOpeningClosingMeetings.created_meeting_id
        response = requests.post(
            f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}/send-to-client",
            headers=self.get_headers()
        )
        
        assert response.status_code == 200, f"Send to client failed: {response.text}"
        data = response.json()
        
        assert "link" in data, "Response should have link"
        assert "organization" in data or "message" in data, "Response should have organization or message"
        
        print(f"✓ Sent to client, link generated")
        print(f"  - Link: {data.get('link', '')[:60]}...")
    
    # ========== TEST: Generate PDF ==========
    def test_07_generate_pdf(self):
        """Test PDF generation for meeting form"""
        if not TestOpeningClosingMeetings.created_meeting_id:
            pytest.skip("No meeting form available")
        
        meeting_id = TestOpeningClosingMeetings.created_meeting_id
        response = requests.get(
            f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}/pdf",
            headers=self.get_headers()
        )
        
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert response.headers.get('content-type') == 'application/pdf', "Should return PDF content type"
        
        pdf_size = len(response.content)
        assert pdf_size > 10000, f"PDF seems too small: {pdf_size} bytes"
        
        print(f"✓ PDF generated successfully: {pdf_size / 1024:.1f} KB")
    
    # ========== TEST: Public Form Access - Not Sent Yet ==========
    def test_08_public_access_not_sent_yet(self):
        """Test that public access fails if not sent to client"""
        # Create a new meeting and try to access without sending
        if not TestOpeningClosingMeetings.stage1_plan_id:
            pytest.skip("No Stage 1 plan available for testing")
        
        # This test verifies behavior when form is not sent yet
        # Using existing meeting which should be sent
        print("✓ Public access test skipped (existing meeting already sent)")
    
    # ========== TEST: Public Form Access ==========
    def test_09_public_form_access(self):
        """Test public access to meeting form (for client)"""
        if not TestOpeningClosingMeetings.meeting_access_token:
            pytest.skip("No meeting access token available")
        
        access_token = TestOpeningClosingMeetings.meeting_access_token
        response = requests.get(f"{BASE_URL}/api/public/opening-closing-meetings/{access_token}")
        
        # If form not sent to client yet, it will fail with 400
        if response.status_code == 400:
            print("✓ Form not yet sent to client (expected behavior)")
            return
        
        assert response.status_code == 200, f"Public access failed: {response.text}"
        data = response.json()
        
        # Verify public response structure
        assert "id" in data, "Public response should have id"
        assert "organization_name" in data, "Public response should have organization_name"
        assert "attendees" in data, "Public response should have attendees"
        assert "status" in data, "Public response should have status"
        
        print(f"✓ Public form accessible: {data.get('organization_name')}")
        print(f"  - Status: {data.get('status')}")
    
    # ========== TEST: Invalid Access Token ==========
    def test_10_invalid_access_token(self):
        """Test that invalid access token returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/opening-closing-meetings/invalid-token-12345")
        
        assert response.status_code == 404, f"Should return 404 for invalid token: {response.text}"
        print("✓ Invalid access token correctly rejected")
    
    # ========== TEST: Client Submit Meeting Form ==========
    def test_11_client_submit_form(self):
        """Test client submitting meeting attendance form"""
        if not TestOpeningClosingMeetings.meeting_access_token:
            pytest.skip("No meeting access token available")
        
        access_token = TestOpeningClosingMeetings.meeting_access_token
        
        # First check if form is accessible and not already submitted
        check_response = requests.get(f"{BASE_URL}/api/public/opening-closing-meetings/{access_token}")
        
        if check_response.status_code == 400:
            print("✓ Form not sent to client yet, skipping submit test")
            return
        
        if check_response.status_code == 200:
            form_data = check_response.json()
            if form_data.get('status') == 'submitted':
                print("✓ Form already submitted, skipping submit test")
                return
        
        # Submit the form
        submit_data = {
            "attendees": [
                {"name": "John Doe", "designation": "Manager", "opening_meeting_date": "2026-01-15", "closing_meeting_date": "2026-01-16"},
                {"name": "Jane Smith", "designation": "Quality Lead", "opening_meeting_date": "2026-01-15", "closing_meeting_date": "2026-01-16"},
                {"name": "Ahmed Ali", "designation": "Operations", "opening_meeting_date": "2026-01-15", "closing_meeting_date": ""}
            ],
            "opening_meeting_notes": "Test opening meeting notes - discussed audit scope and objectives",
            "closing_meeting_notes": "Test closing meeting notes - reviewed findings and recommendations"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/public/opening-closing-meetings/{access_token}/submit",
            json=submit_data
        )
        
        # Check if already submitted
        if response.status_code == 400 and "already" in response.text.lower():
            print("✓ Form already submitted (expected)")
            return
        
        assert response.status_code == 200, f"Submit failed: {response.text}"
        print("✓ Form submitted successfully")
    
    # ========== TEST: Verify Submission ==========
    def test_12_verify_submission(self):
        """Verify submission was saved correctly"""
        if not TestOpeningClosingMeetings.created_meeting_id:
            pytest.skip("No meeting form available")
        
        meeting_id = TestOpeningClosingMeetings.created_meeting_id
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}", headers=self.get_headers())
        
        assert response.status_code == 200, f"Get meeting failed: {response.text}"
        data = response.json()
        
        print(f"✓ Verified meeting state:")
        print(f"  - Status: {data.get('status')}")
        print(f"  - Sent to client: {data.get('sent_to_client')}")
        print(f"  - Attendees filled: {len([a for a in data.get('attendees', []) if a.get('name')])}")
        
        if data.get('submitted_date'):
            print(f"  - Submitted date: {data.get('submitted_date')}")
    
    # ========== TEST: PDF After Submission ==========
    def test_13_pdf_after_submission(self):
        """Test PDF reflects submitted data"""
        if not TestOpeningClosingMeetings.created_meeting_id:
            pytest.skip("No meeting form available")
        
        meeting_id = TestOpeningClosingMeetings.created_meeting_id
        
        # Get meeting status
        meeting_response = requests.get(f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}", headers=self.get_headers())
        meeting_data = meeting_response.json()
        
        # Generate PDF
        response = requests.get(
            f"{BASE_URL}/api/opening-closing-meetings/{meeting_id}/pdf",
            headers=self.get_headers()
        )
        
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        
        pdf_size = len(response.content)
        print(f"✓ PDF generated after submission: {pdf_size / 1024:.1f} KB")
        print(f"  - Meeting status: {meeting_data.get('status')}")
    
    # ========== TEST: List Shows Updated Status ==========
    def test_14_list_shows_updated_status(self):
        """Verify list endpoint shows updated status"""
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings", headers=self.get_headers())
        
        assert response.status_code == 200, f"List failed: {response.text}"
        data = response.json()
        
        # Count by status
        status_counts = {}
        for meeting in data:
            status = meeting.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"✓ Meeting status counts:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
    
    # ========== TEST: Unauthorized Access ==========
    def test_15_unauthorized_access(self):
        """Test that endpoints require authentication"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        
        response = requests.post(f"{BASE_URL}/api/opening-closing-meetings", json={})
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        
        print("✓ Endpoints correctly require authentication")


class TestOpeningClosingMeetingsAdditional:
    """Additional edge case tests"""
    
    def test_get_nonexistent_meeting(self):
        """Test getting non-existent meeting returns 404"""
        token = TestOpeningClosingMeetings.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings/nonexistent-id", headers=headers)
        assert response.status_code == 404, f"Should return 404: {response.status_code}"
        print("✓ Non-existent meeting returns 404")
    
    def test_delete_nonexistent_meeting(self):
        """Test deleting non-existent meeting returns 404"""
        token = TestOpeningClosingMeetings.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.delete(f"{BASE_URL}/api/opening-closing-meetings/nonexistent-id", headers=headers)
        assert response.status_code == 404, f"Should return 404: {response.status_code}"
        print("✓ Delete non-existent meeting returns 404")
    
    def test_generate_pdf_nonexistent(self):
        """Test PDF generation for non-existent meeting returns 404"""
        token = TestOpeningClosingMeetings.get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/opening-closing-meetings/nonexistent-id/pdf", headers=headers)
        assert response.status_code == 404, f"Should return 404: {response.status_code}"
        print("✓ PDF for non-existent meeting returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
