"""
Test file for Customer Portal, Audit Scheduling, Document Management, and Contact History features.
Created for iteration 14 testing.
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://stage2-audit-plan.preview.emergentagent.com').rstrip('/')

# Test data constants
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Known data from database
EXISTING_FORM_ID = "ab9a8ab2-2f59-4cd3-89d0-23a8be32882a"
SIGNED_CONTRACT_ID = "1c121c59-100f-49a9-b348-5e0694d1bd84"  # agreement_signed status

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]

@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestCustomerPortalTracking:
    """Test public tracking endpoint for Customer Portal"""
    
    def test_track_order_by_form_id(self):
        """Test tracking order using form ID - should return order status and timeline"""
        response = requests.get(f"{BASE_URL}/api/public/track/{EXISTING_FORM_ID}")
        
        assert response.status_code == 200, f"Failed to track order: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "tracking_id" in data, "Response missing tracking_id"
        assert "company_name" in data, "Response missing company_name"
        assert "current_status" in data, "Response missing current_status"
        assert "timeline_dates" in data, "Response missing timeline_dates"
        
        # Verify data values
        assert data["tracking_id"] == EXISTING_FORM_ID
        assert data["company_name"] == "شركة التقنية المتقدمة"
        assert data["current_status"] in ["pending", "submitted", "under_review", "accepted", "agreement_signed", "contract_generated"]
        
        # Verify timeline has at least pending date
        assert "pending" in data["timeline_dates"], "Timeline missing pending date"
        print(f"Track order SUCCESS: Company={data['company_name']}, Status={data['current_status']}")
    
    def test_track_order_not_found(self):
        """Test tracking with non-existent ID returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/public/track/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404 for non-existent order, got {response.status_code}"
        print("Track order NOT FOUND test passed")
    
    def test_track_order_response_includes_standards(self):
        """Test that tracking response includes certification standards"""
        response = requests.get(f"{BASE_URL}/api/public/track/{EXISTING_FORM_ID}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify standards field exists (may be empty for pending forms)
        assert "standards" in data, "Response missing standards field"
        
        # For this form, we know it has ISO certifications
        if data["standards"]:
            print(f"Standards found: {data['standards']}")
        else:
            print("No standards found (expected for some forms)")


class TestAuditScheduling:
    """Test Audit Scheduling CRUD operations"""
    
    def test_get_audit_schedules(self, auth_headers):
        """Test getting all audit schedules"""
        response = requests.get(f"{BASE_URL}/api/audit-schedules", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get audit schedules: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Get audit schedules SUCCESS: Found {len(data)} audits")
    
    def test_create_audit_schedule(self, auth_headers):
        """Test creating a new audit schedule"""
        # Create audit with signed contract
        audit_data = {
            "contract_id": SIGNED_CONTRACT_ID,
            "site_id": "",
            "audit_type": "initial",
            "scheduled_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "scheduled_time": "09:00",
            "duration_days": 2,
            "auditors": "TEST_Auditor_John Smith",
            "notes": "TEST_Initial certification audit"
        }
        
        response = requests.post(f"{BASE_URL}/api/audit-schedules", json=audit_data, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to create audit schedule: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response missing audit ID"
        assert "message" in data, "Response missing message"
        
        print(f"Create audit schedule SUCCESS: ID={data['id']}")
        return data["id"]
    
    def test_create_and_verify_audit_persistence(self, auth_headers):
        """Test creating audit and verifying it persists in database"""
        # Create audit
        audit_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        audit_data = {
            "contract_id": SIGNED_CONTRACT_ID,
            "site_id": "",
            "audit_type": "surveillance",
            "scheduled_date": audit_date,
            "scheduled_time": "10:00",
            "duration_days": 1,
            "auditors": "TEST_Auditor_Jane Doe",
            "notes": "TEST_Surveillance audit - verify persistence"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/audit-schedules", json=audit_data, headers=auth_headers)
        assert create_response.status_code == 200, f"Failed to create audit: {create_response.text}"
        
        audit_id = create_response.json()["id"]
        
        # Get all audits and verify our audit is there
        get_response = requests.get(f"{BASE_URL}/api/audit-schedules", headers=auth_headers)
        assert get_response.status_code == 200
        
        audits = get_response.json()
        audit_found = next((a for a in audits if a.get("id") == audit_id), None)
        
        assert audit_found is not None, f"Created audit {audit_id} not found in list"
        assert audit_found["audit_type"] == "surveillance"
        assert audit_found["scheduled_date"] == audit_date or audit_found["scheduled_date"].startswith(audit_date)
        
        print(f"Audit persistence verified: ID={audit_id}, Type={audit_found['audit_type']}")
        return audit_id
    
    def test_delete_audit_schedule(self, auth_headers):
        """Test deleting an audit schedule"""
        # First create an audit to delete
        audit_data = {
            "contract_id": SIGNED_CONTRACT_ID,
            "site_id": "",
            "audit_type": "recertification",
            "scheduled_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "scheduled_time": "14:00",
            "duration_days": 3,
            "auditors": "TEST_Auditor_Delete",
            "notes": "TEST_Audit to be deleted"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/audit-schedules", json=audit_data, headers=auth_headers)
        assert create_response.status_code == 200
        audit_id = create_response.json()["id"]
        
        # Delete the audit
        delete_response = requests.delete(f"{BASE_URL}/api/audit-schedules/{audit_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Failed to delete audit: {delete_response.text}"
        
        # Verify audit no longer exists
        get_response = requests.get(f"{BASE_URL}/api/audit-schedules", headers=auth_headers)
        audits = get_response.json()
        audit_found = next((a for a in audits if a.get("id") == audit_id), None)
        
        assert audit_found is None, f"Deleted audit {audit_id} still found in list"
        print(f"Delete audit SUCCESS: ID={audit_id}")


class TestContactHistory:
    """Test Contact History CRUD operations"""
    
    def test_get_contacts(self, auth_headers):
        """Test getting all contact records"""
        response = requests.get(f"{BASE_URL}/api/contacts", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get contacts: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Get contacts SUCCESS: Found {len(data)} contacts")
    
    def test_create_contact_record(self, auth_headers):
        """Test creating a new contact record"""
        contact_data = {
            "customer_id": EXISTING_FORM_ID,
            "contact_type": "call",
            "subject": "TEST_Follow-up on certification application",
            "notes": "TEST_Discussed documentation requirements and timeline",
            "contact_date": datetime.now().strftime("%Y-%m-%d"),
            "follow_up_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
        
        response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to create contact: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response missing contact ID"
        
        print(f"Create contact SUCCESS: ID={data['id']}")
        return data["id"]
    
    def test_create_and_verify_contact_persistence(self, auth_headers):
        """Test creating contact and verifying it persists"""
        contact_data = {
            "customer_id": EXISTING_FORM_ID,
            "contact_type": "email",
            "subject": "TEST_Email correspondence - persistence test",
            "notes": "TEST_Sent proposal documentation via email",
            "contact_date": datetime.now().strftime("%Y-%m-%d"),
            "follow_up_date": ""
        }
        
        create_response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=auth_headers)
        assert create_response.status_code == 200
        
        contact_id = create_response.json()["id"]
        
        # Get all contacts and verify our contact is there
        get_response = requests.get(f"{BASE_URL}/api/contacts", headers=auth_headers)
        assert get_response.status_code == 200
        
        contacts = get_response.json()
        contact_found = next((c for c in contacts if c.get("id") == contact_id), None)
        
        assert contact_found is not None, f"Created contact {contact_id} not found in list"
        assert contact_found["contact_type"] == "email"
        assert "persistence test" in contact_found["subject"]
        
        print(f"Contact persistence verified: ID={contact_id}, Type={contact_found['contact_type']}")
        return contact_id
    
    def test_create_contact_meeting_type(self, auth_headers):
        """Test creating a meeting type contact"""
        contact_data = {
            "customer_id": EXISTING_FORM_ID,
            "contact_type": "meeting",
            "subject": "TEST_Kickoff meeting for certification process",
            "notes": "TEST_Met with client team to discuss audit schedule",
            "contact_date": datetime.now().strftime("%Y-%m-%d"),
            "follow_up_date": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=auth_headers)
        assert response.status_code == 200
        
        contact_id = response.json()["id"]
        print(f"Create meeting contact SUCCESS: ID={contact_id}")
    
    def test_mark_follow_up_complete(self, auth_headers):
        """Test marking a follow-up as complete"""
        # Create contact with follow-up date
        contact_data = {
            "customer_id": EXISTING_FORM_ID,
            "contact_type": "call",
            "subject": "TEST_Follow-up test contact",
            "notes": "TEST_Testing follow-up completion",
            "contact_date": datetime.now().strftime("%Y-%m-%d"),
            "follow_up_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        }
        
        create_response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=auth_headers)
        assert create_response.status_code == 200
        contact_id = create_response.json()["id"]
        
        # Mark follow-up as complete
        follow_up_response = requests.put(f"{BASE_URL}/api/contacts/{contact_id}/follow-up", headers=auth_headers)
        assert follow_up_response.status_code == 200, f"Failed to mark follow-up complete: {follow_up_response.text}"
        
        # Verify the update
        get_response = requests.get(f"{BASE_URL}/api/contacts", headers=auth_headers)
        contacts = get_response.json()
        contact_found = next((c for c in contacts if c.get("id") == contact_id), None)
        
        assert contact_found is not None
        assert contact_found["follow_up_completed"] == True, "Follow-up should be marked as completed"
        
        print(f"Mark follow-up complete SUCCESS: ID={contact_id}")
    
    def test_delete_contact(self, auth_headers):
        """Test deleting a contact record"""
        # Create contact to delete
        contact_data = {
            "customer_id": EXISTING_FORM_ID,
            "contact_type": "other",
            "subject": "TEST_Contact to be deleted",
            "notes": "TEST_This contact will be deleted",
            "contact_date": datetime.now().strftime("%Y-%m-%d"),
            "follow_up_date": ""
        }
        
        create_response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=auth_headers)
        assert create_response.status_code == 200
        contact_id = create_response.json()["id"]
        
        # Delete the contact
        delete_response = requests.delete(f"{BASE_URL}/api/contacts/{contact_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Failed to delete contact: {delete_response.text}"
        
        # Verify contact no longer exists
        get_response = requests.get(f"{BASE_URL}/api/contacts", headers=auth_headers)
        contacts = get_response.json()
        contact_found = next((c for c in contacts if c.get("id") == contact_id), None)
        
        assert contact_found is None, f"Deleted contact {contact_id} still found in list"
        print(f"Delete contact SUCCESS: ID={contact_id}")


class TestDocumentManagement:
    """Test Document Management CRUD operations"""
    
    def test_get_documents(self, auth_headers):
        """Test getting all documents"""
        response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Get documents SUCCESS: Found {len(data)} documents")
    
    def test_upload_document(self, auth_headers):
        """Test uploading a new document"""
        # Create a simple text file as base64
        test_content = "This is a test document for certification."
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": EXISTING_FORM_ID,
            "related_type": "form",
            "name": "TEST_Certification_Document.txt",
            "file_type": "text/plain",
            "file_data": f"data:text/plain;base64,{file_data}"
        }
        
        response = requests.post(f"{BASE_URL}/api/documents", json=doc_data, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to upload document: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response missing document ID"
        
        print(f"Upload document SUCCESS: ID={data['id']}")
        return data["id"]
    
    def test_upload_and_verify_document_persistence(self, auth_headers):
        """Test uploading document and verifying it persists"""
        test_content = "Verification test document content - checking persistence"
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": EXISTING_FORM_ID,
            "related_type": "form",
            "name": "TEST_Persistence_Doc.txt",
            "file_type": "text/plain",
            "file_data": f"data:text/plain;base64,{file_data}"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/documents", json=doc_data, headers=auth_headers)
        assert create_response.status_code == 200
        
        doc_id = create_response.json()["id"]
        
        # Get all documents and verify our document is there
        get_response = requests.get(f"{BASE_URL}/api/documents", headers=auth_headers)
        assert get_response.status_code == 200
        
        documents = get_response.json()
        doc_found = next((d for d in documents if d.get("id") == doc_id), None)
        
        assert doc_found is not None, f"Created document {doc_id} not found in list"
        assert doc_found["name"] == "TEST_Persistence_Doc.txt"
        
        print(f"Document persistence verified: ID={doc_id}, Name={doc_found['name']}")
        return doc_id
    
    def test_download_document(self, auth_headers):
        """Test downloading a specific document"""
        # First upload a document
        test_content = "Download test content"
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": "general",
            "related_type": "general",
            "name": "TEST_Download_Doc.txt",
            "file_type": "text/plain",
            "file_data": f"data:text/plain;base64,{file_data}"
        }
        
        upload_response = requests.post(f"{BASE_URL}/api/documents", json=doc_data, headers=auth_headers)
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Download the document
        download_response = requests.get(f"{BASE_URL}/api/documents/{doc_id}", headers=auth_headers)
        assert download_response.status_code == 200, f"Failed to download document: {download_response.text}"
        
        data = download_response.json()
        assert "file_data" in data, "Response missing file_data"
        assert data["name"] == "TEST_Download_Doc.txt"
        
        print(f"Download document SUCCESS: ID={doc_id}")
        return doc_id
    
    def test_delete_document(self, auth_headers):
        """Test deleting a document"""
        # First upload a document to delete
        test_content = "Document to be deleted"
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": "general",
            "related_type": "general",
            "name": "TEST_Delete_Doc.txt",
            "file_type": "text/plain",
            "file_data": f"data:text/plain;base64,{file_data}"
        }
        
        upload_response = requests.post(f"{BASE_URL}/api/documents", json=doc_data, headers=auth_headers)
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # Delete the document
        delete_response = requests.delete(f"{BASE_URL}/api/documents/{doc_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Failed to delete document: {delete_response.text}"
        
        # Verify document no longer exists
        get_response = requests.get(f"{BASE_URL}/api/documents/{doc_id}", headers=auth_headers)
        assert get_response.status_code == 404, f"Deleted document {doc_id} still exists"
        
        print(f"Delete document SUCCESS: ID={doc_id}")


class TestRequiredAuth:
    """Test that authenticated endpoints require valid token"""
    
    def test_audit_schedules_requires_auth(self):
        """Test that audit-schedules endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/audit-schedules")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Auth required for audit-schedules: PASS")
    
    def test_contacts_requires_auth(self):
        """Test that contacts endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/contacts")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Auth required for contacts: PASS")
    
    def test_documents_requires_auth(self):
        """Test that documents endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Auth required for documents: PASS")
    
    def test_public_track_no_auth_required(self):
        """Test that public track endpoint does NOT require auth"""
        response = requests.get(f"{BASE_URL}/api/public/track/{EXISTING_FORM_ID}")
        assert response.status_code == 200, f"Public track should work without auth, got {response.status_code}"
        print("Public track NO auth required: PASS")
