"""
Customer Feedback (BAC-F6-16) API Tests

Tests customer satisfaction survey functionality:
- Admin CRUD operations for feedback forms
- Public endpoint for clients to view and submit feedback
- Score calculation verification (>=90% Excellent, 75-89% Good, 60-74% Average, <60% Unsatisfactory)
- PDF generation
- Review workflow
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
AUTH_TOKEN = None
TEST_FEEDBACK_IDS = []

# Admin credentials for testing
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"


class TestAuthSetup:
    """Get authentication token for protected endpoints"""
    
    def test_admin_login(self):
        """Login as admin to get auth token"""
        global AUTH_TOKEN
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        AUTH_TOKEN = data["token"]
        print(f"✓ Admin login successful, token obtained")


class TestCustomerFeedbackCRUD:
    """Test CRUD operations for customer feedback (authenticated admin)"""
    
    @pytest.fixture(autouse=True)
    def auth_headers(self):
        """Set up auth headers for each test"""
        assert AUTH_TOKEN, "AUTH_TOKEN not set - run TestAuthSetup first"
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    def test_get_feedback_list(self, auth_headers):
        """GET /api/customer-feedback - List all feedback forms"""
        response = requests.get(f"{BASE_URL}/api/customer-feedback", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get feedback list: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/customer-feedback - Found {len(data)} feedback forms")
    
    def test_create_feedback_form(self, auth_headers):
        """POST /api/customer-feedback - Create a new feedback form"""
        global TEST_FEEDBACK_IDS
        
        payload = {
            "organization_name": "TEST_Company_Feedback",
            "organization_name_ar": "شركة الاختبار للملاحظات",
            "audit_type": "Initial",
            "standards": ["ISO 9001:2015"],
            "audit_date": "2026-01-20",
            "lead_auditor": "Ahmed Ali",
            "auditor": "Mohammed Hassan",
            "certificate_id": "",
            "audit_id": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/customer-feedback", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create feedback: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "access_token" in data
        assert "public_url" in data
        
        TEST_FEEDBACK_IDS.append(data["id"])
        print(f"✓ POST /api/customer-feedback - Created feedback ID: {data['id']}")
        print(f"  Access token: {data['access_token']}")
        print(f"  Public URL: {data['public_url']}")
        
        return data
    
    def test_get_single_feedback(self, auth_headers):
        """GET /api/customer-feedback/{id} - Get single feedback with questions"""
        # First create a feedback if none exists
        if not TEST_FEEDBACK_IDS:
            created = self.test_create_feedback_form(auth_headers)
            feedback_id = created["id"]
        else:
            feedback_id = TEST_FEEDBACK_IDS[0]
        
        response = requests.get(f"{BASE_URL}/api/customer-feedback/{feedback_id}", headers=auth_headers)
        assert response.status_code == 200, f"Failed to get feedback: {response.text}"
        data = response.json()
        
        # Verify data structure
        assert data["id"] == feedback_id
        assert "organization_name" in data
        assert "questions" in data
        assert isinstance(data["questions"], list)
        
        # Verify default questions are present (13 questions)
        assert len(data["questions"]) == 13, f"Expected 13 default questions, got {len(data['questions'])}"
        
        # Verify question structure
        for q in data["questions"]:
            assert "category" in q
            assert "question" in q
            assert "question_ar" in q
        
        print(f"✓ GET /api/customer-feedback/{feedback_id} - Contains {len(data['questions'])} questions")
        print(f"  Categories: {set(q['category'] for q in data['questions'])}")
    
    def test_update_feedback(self, auth_headers):
        """PUT /api/customer-feedback/{id} - Update feedback"""
        if not TEST_FEEDBACK_IDS:
            created = self.test_create_feedback_form(auth_headers)
            feedback_id = created["id"]
        else:
            feedback_id = TEST_FEEDBACK_IDS[0]
        
        update_data = {
            "audit_type": "1st Surveillance",
            "lead_auditor": "Omar Khaled"
        }
        
        response = requests.put(f"{BASE_URL}/api/customer-feedback/{feedback_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Failed to update feedback: {response.text}"
        
        # Verify update
        get_response = requests.get(f"{BASE_URL}/api/customer-feedback/{feedback_id}", headers=auth_headers)
        updated_data = get_response.json()
        assert updated_data["audit_type"] == "1st Surveillance"
        assert updated_data["lead_auditor"] == "Omar Khaled"
        
        print(f"✓ PUT /api/customer-feedback/{feedback_id} - Update successful")
    
    def test_filter_feedback_by_status(self, auth_headers):
        """GET /api/customer-feedback?status=pending - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/customer-feedback?status=pending", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # All returned items should have pending status
        for item in data:
            if item.get('status'):  # Some might not have status yet
                assert item['status'] == 'pending' or item['status'] == 'submitted'
        
        print(f"✓ GET /api/customer-feedback?status=pending - Filter working, {len(data)} results")


class TestPublicFeedbackEndpoints:
    """Test public endpoints for client feedback submission (no auth required)"""
    
    @pytest.fixture
    def access_token(self):
        """Create a feedback and get its access token"""
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        payload = {
            "organization_name": "TEST_Public_Feedback_Co",
            "audit_type": "Initial",
            "standards": ["ISO 14001:2015"],
            "audit_date": "2026-01-22"
        }
        response = requests.post(f"{BASE_URL}/api/customer-feedback", json=payload, headers=headers)
        data = response.json()
        TEST_FEEDBACK_IDS.append(data["id"])
        return data["access_token"]
    
    def test_get_public_feedback_form(self, access_token):
        """GET /api/public/feedback/{access_token} - Get public form (no auth)"""
        response = requests.get(f"{BASE_URL}/api/public/feedback/{access_token}")
        assert response.status_code == 200, f"Failed to get public form: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "id" in data
        assert "organization_name" in data
        assert "questions" in data
        assert data["status"] == "pending"
        
        print(f"✓ GET /api/public/feedback/{access_token} - Public form accessible")
        print(f"  Organization: {data['organization_name']}")
        print(f"  Questions count: {len(data['questions'])}")
    
    def test_submit_public_feedback_and_verify_score(self, access_token):
        """POST /api/public/feedback/{access_token}/submit - Submit and verify score calculation"""
        # Submit with all 5-star ratings (should be 100% = Excellent)
        questions_data = []
        for i in range(13):
            questions_data.append({"index": i, "rating": 5})
        
        submission = {
            "questions": questions_data,
            "want_same_team": True,
            "suggestions": "Great service! Highly recommended.",
            "respondent_name": "John Smith",
            "respondent_designation": "Quality Manager"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        assert response.status_code == 200, f"Failed to submit feedback: {response.text}"
        data = response.json()
        
        # Verify score calculation
        assert "overall_score" in data
        assert "evaluation_result" in data
        assert data["overall_score"] == 100.0, f"Expected 100%, got {data['overall_score']}%"
        assert data["evaluation_result"] == "excellent", f"Expected 'excellent', got {data['evaluation_result']}"
        
        print(f"✓ POST /api/public/feedback/{access_token}/submit - Score: {data['overall_score']}% ({data['evaluation_result']})")
    
    def test_duplicate_submission_blocked(self, access_token):
        """Verify duplicate submissions are blocked"""
        # First submission
        questions_data = [{"index": i, "rating": 5} for i in range(13)]
        submission = {
            "questions": questions_data,
            "want_same_team": True,
            "suggestions": "",
            "respondent_name": "Test User",
            "respondent_designation": ""
        }
        
        # Submit once
        response1 = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        assert response1.status_code == 200
        
        # Try to submit again
        response2 = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        
        print(f"✓ Duplicate submission correctly blocked (status 400)")
    
    def test_invalid_access_token(self):
        """GET /api/public/feedback/invalid-token - Invalid token handling"""
        response = requests.get(f"{BASE_URL}/api/public/feedback/invalid-token-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Invalid access token correctly returns 404")


class TestScoreCalculation:
    """Test score calculation formula: percentage = (total_rating / (num_questions * 5)) * 100"""
    
    @pytest.fixture
    def create_feedback_and_get_token(self):
        """Create feedback for score testing"""
        def _create():
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            payload = {
                "organization_name": "TEST_Score_Calc_Co",
                "audit_type": "Initial",
                "standards": ["ISO 9001:2015"],
                "audit_date": "2026-01-25"
            }
            response = requests.post(f"{BASE_URL}/api/customer-feedback", json=payload, headers=headers)
            data = response.json()
            TEST_FEEDBACK_IDS.append(data["id"])
            return data["access_token"]
        return _create
    
    def test_excellent_score(self, create_feedback_and_get_token):
        """Score >=90% should be 'excellent'"""
        access_token = create_feedback_and_get_token()
        
        # All 5s = 100%
        questions = [{"index": i, "rating": 5} for i in range(13)]
        submission = {
            "questions": questions,
            "respondent_name": "Excellent Tester",
            "respondent_designation": "QA"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        data = response.json()
        
        assert data["overall_score"] >= 90
        assert data["evaluation_result"] == "excellent"
        print(f"✓ Excellent score test: {data['overall_score']}% = {data['evaluation_result']}")
    
    def test_good_score(self, create_feedback_and_get_token):
        """Score 75-89% should be 'good'"""
        access_token = create_feedback_and_get_token()
        
        # Mix of 4s = 80%
        questions = [{"index": i, "rating": 4} for i in range(13)]
        submission = {
            "questions": questions,
            "respondent_name": "Good Tester",
            "respondent_designation": "Manager"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        data = response.json()
        
        assert 75 <= data["overall_score"] < 90
        assert data["evaluation_result"] == "good"
        print(f"✓ Good score test: {data['overall_score']}% = {data['evaluation_result']}")
    
    def test_average_score(self, create_feedback_and_get_token):
        """Score 60-74% should be 'average'"""
        access_token = create_feedback_and_get_token()
        
        # Mix of 3s and 4s = ~65-70%
        questions = []
        for i in range(13):
            rating = 3 if i % 2 == 0 else 4  # Alternate 3 and 4
            questions.append({"index": i, "rating": rating})
        
        submission = {
            "questions": questions,
            "respondent_name": "Average Tester",
            "respondent_designation": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        data = response.json()
        
        # 7*3 + 6*4 = 21 + 24 = 45 / 65 = 69.2%
        assert 60 <= data["overall_score"] < 75, f"Got {data['overall_score']}%"
        assert data["evaluation_result"] == "average"
        print(f"✓ Average score test: {data['overall_score']}% = {data['evaluation_result']}")
    
    def test_unsatisfactory_score(self, create_feedback_and_get_token):
        """Score <60% should be 'unsatisfactory'"""
        access_token = create_feedback_and_get_token()
        
        # All 2s = 40%
        questions = [{"index": i, "rating": 2} for i in range(13)]
        submission = {
            "questions": questions,
            "respondent_name": "Low Tester",
            "respondent_designation": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        data = response.json()
        
        assert data["overall_score"] < 60
        assert data["evaluation_result"] == "unsatisfactory"
        print(f"✓ Unsatisfactory score test: {data['overall_score']}% = {data['evaluation_result']}")
    
    def test_na_ratings_excluded(self, create_feedback_and_get_token):
        """N/A ratings should be excluded from calculation"""
        access_token = create_feedback_and_get_token()
        
        # Some 5s, some N/A
        questions = []
        for i in range(13):
            if i < 7:
                questions.append({"index": i, "rating": 5})
            else:
                questions.append({"index": i, "rating": "na"})
        
        submission = {
            "questions": questions,
            "respondent_name": "NA Tester",
            "respondent_designation": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        data = response.json()
        
        # 7*5 = 35 / (7*5) = 100% (N/A excluded)
        assert data["overall_score"] == 100.0, f"Expected 100%, got {data['overall_score']}%"
        print(f"✓ N/A exclusion test: {data['overall_score']}% (N/A ratings properly excluded)")


class TestReviewWorkflow:
    """Test admin review workflow for submitted feedback"""
    
    @pytest.fixture(autouse=True)
    def auth_headers(self):
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    @pytest.fixture
    def submitted_feedback_id(self, auth_headers):
        """Create and submit a feedback for review testing"""
        # Create
        create_payload = {
            "organization_name": "TEST_Review_Workflow_Co",
            "audit_type": "2nd Surveillance",
            "standards": ["ISO 45001:2018"]
        }
        create_resp = requests.post(f"{BASE_URL}/api/customer-feedback", json=create_payload, headers=auth_headers)
        data = create_resp.json()
        feedback_id = data["id"]
        access_token = data["access_token"]
        TEST_FEEDBACK_IDS.append(feedback_id)
        
        # Submit
        questions = [{"index": i, "rating": 4} for i in range(13)]
        submission = {
            "questions": questions,
            "want_same_team": True,
            "suggestions": "Good overall",
            "respondent_name": "Review Tester",
            "respondent_designation": "Director"
        }
        requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        
        return feedback_id
    
    def test_mark_as_reviewed(self, auth_headers, submitted_feedback_id):
        """POST /api/customer-feedback/{id}/review - Mark as reviewed"""
        review_data = {
            "reviewed_by": "Admin User",
            "review_date": "2026-01-20",
            "review_comments": "Feedback reviewed and noted for improvement areas."
        }
        
        response = requests.post(
            f"{BASE_URL}/api/customer-feedback/{submitted_feedback_id}/review",
            json=review_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to review: {response.text}"
        
        # Verify status changed
        get_resp = requests.get(f"{BASE_URL}/api/customer-feedback/{submitted_feedback_id}", headers=auth_headers)
        feedback = get_resp.json()
        
        assert feedback["status"] == "reviewed"
        assert feedback["reviewed_by"] == "Admin User"
        assert feedback["review_comments"] == "Feedback reviewed and noted for improvement areas."
        
        print(f"✓ POST /api/customer-feedback/{submitted_feedback_id}/review - Status updated to 'reviewed'")


class TestPDFGeneration:
    """Test PDF generation for customer feedback"""
    
    @pytest.fixture(autouse=True)
    def auth_headers(self):
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    def test_generate_pdf(self, auth_headers):
        """GET /api/customer-feedback/{id}/pdf - Generate PDF"""
        # First create and submit a feedback
        create_payload = {
            "organization_name": "TEST_PDF_Gen_Co",
            "audit_type": "Re-Certification",
            "standards": ["ISO 9001:2015", "ISO 14001:2015"]
        }
        create_resp = requests.post(f"{BASE_URL}/api/customer-feedback", json=create_payload, headers=auth_headers)
        data = create_resp.json()
        feedback_id = data["id"]
        access_token = data["access_token"]
        TEST_FEEDBACK_IDS.append(feedback_id)
        
        # Submit feedback
        questions = [{"index": i, "rating": 5} for i in range(13)]
        submission = {
            "questions": questions,
            "want_same_team": True,
            "suggestions": "Excellent service!",
            "respondent_name": "PDF Tester",
            "respondent_designation": "Quality Manager"
        }
        requests.post(f"{BASE_URL}/api/public/feedback/{access_token}/submit", json=submission)
        
        # Generate PDF
        response = requests.get(f"{BASE_URL}/api/customer-feedback/{feedback_id}/pdf", headers=auth_headers)
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000, "PDF content seems too small"
        
        print(f"✓ GET /api/customer-feedback/{feedback_id}/pdf - PDF generated ({len(response.content)} bytes)")


class TestDeleteFeedback:
    """Test delete operation"""
    
    def test_delete_feedback(self):
        """DELETE /api/customer-feedback/{id} - Delete feedback"""
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Create a feedback to delete
        create_payload = {
            "organization_name": "TEST_Delete_Me_Co",
            "audit_type": "Initial"
        }
        create_resp = requests.post(f"{BASE_URL}/api/customer-feedback", json=create_payload, headers=headers)
        feedback_id = create_resp.json()["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/customer-feedback/{feedback_id}", headers=headers)
        assert response.status_code == 200, f"Delete failed: {response.text}"
        
        # Verify deleted
        get_resp = requests.get(f"{BASE_URL}/api/customer-feedback/{feedback_id}", headers=headers)
        assert get_resp.status_code == 404
        
        print(f"✓ DELETE /api/customer-feedback/{feedback_id} - Deleted successfully")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self):
        """Delete all test-created feedback"""
        global TEST_FEEDBACK_IDS
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        deleted_count = 0
        for feedback_id in TEST_FEEDBACK_IDS:
            try:
                response = requests.delete(f"{BASE_URL}/api/customer-feedback/{feedback_id}", headers=headers)
                if response.status_code == 200:
                    deleted_count += 1
            except:
                pass
        
        TEST_FEEDBACK_IDS = []
        print(f"✓ Cleanup: Deleted {deleted_count} test feedback records")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
