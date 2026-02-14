"""
Test file for new features in the Service Contract Management System:
- Customer Portal (Public Tracking)
- Reports Export (Excel/PDF)
- Audit Scheduling
- Contact History
- Document Management
- Sites Management
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "admin123"

class TestAuthentication:
    """Test authentication - needed for other tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Auth failed: {response.text}"
        data = response.json()
        assert "token" in data
        return data["token"]

class TestCustomerPortalTracking:
    """Test public tracking endpoint for Customer Portal"""
    
    def test_track_with_invalid_id(self):
        """Test tracking with non-existent ID returns 404"""
        response = requests.get(f"{BASE_URL}/api/public/track/invalid-tracking-id")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"[PASS] Invalid tracking ID returns 404: {data['detail']}")
    
    def test_track_with_valid_form_id(self):
        """Get a valid form ID and test tracking"""
        # First login and get forms
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        forms_response = requests.get(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if forms_response.status_code == 200:
            forms = forms_response.json()
            if forms:
                form_id = forms[0]["id"]
                # Now test public tracking
                track_response = requests.get(f"{BASE_URL}/api/public/track/{form_id}")
                assert track_response.status_code == 200
                data = track_response.json()
                assert "tracking_id" in data
                assert "company_name" in data
                assert "current_status" in data
                assert "timeline_dates" in data
                print(f"[PASS] Tracking works - Company: {data['company_name']}, Status: {data['current_status']}")
            else:
                pytest.skip("No application forms found for tracking test")
        else:
            pytest.skip("Could not fetch application forms")


class TestReportsExport:
    """Test reports export functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_export_excel(self, auth_token):
        """Test Excel export endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/export?format=excel",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Excel export failed: {response.text}"
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
        assert len(response.content) > 0
        print(f"[PASS] Excel export successful - Size: {len(response.content)} bytes")
    
    def test_export_pdf(self, auth_token):
        """Test PDF export endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/export?format=pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"PDF export failed: {response.text}"
        assert "application/pdf" in response.headers.get("content-type", "")
        assert len(response.content) > 0
        print(f"[PASS] PDF export successful - Size: {len(response.content)} bytes")
    
    def test_export_with_filters(self, auth_token):
        """Test export with date filters"""
        response = requests.get(
            f"{BASE_URL}/api/reports/export?format=excel&start_date=2024-01-01&end_date=2026-12-31",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print("[PASS] Excel export with date filters successful")
    
    def test_export_without_auth_fails(self):
        """Test export requires authentication"""
        response = requests.get(f"{BASE_URL}/api/reports/export?format=excel")
        assert response.status_code in [401, 403]
        print("[PASS] Export without auth correctly rejected")


class TestSitesManagement:
    """Test sites CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_sites(self, auth_token):
        """Test get sites endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/sites",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        sites = response.json()
        assert isinstance(sites, list)
        print(f"[PASS] Get sites successful - Found {len(sites)} sites")
    
    def test_create_site(self, auth_token):
        """Test create site"""
        site_data = {
            "contract_id": "TEST_contract_001",
            "name": "TEST Site Location",
            "address": "123 Test Street",
            "city": "Riyadh",
            "country": "Saudi Arabia",
            "contact_name": "Test Contact",
            "contact_email": "test@site.com",
            "contact_phone": "+966 555 1234",
            "is_main_site": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sites",
            json=site_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"[PASS] Site created with ID: {data['id']}")
        return data["id"]
    
    def test_delete_site(self, auth_token):
        """Test delete site"""
        # First create a site
        site_data = {
            "contract_id": "TEST_delete_contract",
            "name": "TEST Site to Delete",
            "address": "Delete Street",
            "city": "Jeddah"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/sites",
            json=site_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        site_id = create_response.json()["id"]
        
        # Then delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/sites/{site_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code == 200
        print(f"[PASS] Site {site_id} deleted successfully")


class TestAuditScheduling:
    """Test audit scheduling CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_audit_schedules(self, auth_token):
        """Test get audit schedules"""
        response = requests.get(
            f"{BASE_URL}/api/audit-schedules",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        audits = response.json()
        assert isinstance(audits, list)
        print(f"[PASS] Get audit schedules successful - Found {len(audits)} audits")
    
    def test_create_audit_schedule(self, auth_token):
        """Test create audit schedule"""
        # First need to get a contract/proposal id
        proposals_response = requests.get(
            f"{BASE_URL}/api/proposals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if proposals_response.status_code == 200 and proposals_response.json():
            proposal = proposals_response.json()[0]
            proposal_id = proposal["id"]
            
            audit_data = {
                "contract_id": proposal_id,
                "site_id": "",
                "audit_type": "initial",
                "scheduled_date": "2026-03-15",
                "scheduled_time": "09:00",
                "duration_days": 2,
                "auditors": "John Doe, Jane Smith",
                "notes": "TEST audit schedule"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/audit-schedules",
                json=audit_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            print(f"[PASS] Audit schedule created with ID: {data['id']}")
            return data["id"]
        else:
            pytest.skip("No proposals found to create audit schedule")
    
    def test_delete_audit_schedule(self, auth_token):
        """Test delete audit schedule"""
        # Get proposals first
        proposals_response = requests.get(
            f"{BASE_URL}/api/proposals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if proposals_response.status_code == 200 and proposals_response.json():
            proposal_id = proposals_response.json()[0]["id"]
            
            # Create an audit
            audit_data = {
                "contract_id": proposal_id,
                "audit_type": "surveillance",
                "scheduled_date": "2026-04-20",
                "notes": "TEST audit to delete"
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/audit-schedules",
                json=audit_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if create_response.status_code == 200:
                audit_id = create_response.json()["id"]
                
                delete_response = requests.delete(
                    f"{BASE_URL}/api/audit-schedules/{audit_id}",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                assert delete_response.status_code == 200
                print(f"[PASS] Audit schedule {audit_id} deleted successfully")
        else:
            pytest.skip("No proposals found")


class TestContactHistory:
    """Test contact history CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_contacts(self, auth_token):
        """Test get contacts endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/contacts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        contacts = response.json()
        assert isinstance(contacts, list)
        print(f"[PASS] Get contacts successful - Found {len(contacts)} contact records")
    
    def test_create_contact(self, auth_token):
        """Test create contact record"""
        # Get a customer ID from forms
        forms_response = requests.get(
            f"{BASE_URL}/api/application-forms",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        customer_id = "TEST_customer_001"
        customer_name = "Test Company"
        
        if forms_response.status_code == 200 and forms_response.json():
            customer_id = forms_response.json()[0]["id"]
            customer_name = forms_response.json()[0].get("client_info", {}).get("company_name", "Test Company")
        
        contact_data = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "contact_type": "call",
            "subject": "TEST Follow-up call regarding certification",
            "notes": "Discussed ISO 9001 requirements. Customer interested in proceeding.",
            "contact_date": "2026-01-15",
            "follow_up_date": "2026-01-22"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/contacts",
            json=contact_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"[PASS] Contact record created with ID: {data['id']}")
        return data["id"]
    
    def test_contact_follow_up(self, auth_token):
        """Test marking follow-up as complete"""
        # Create a contact with follow-up
        contact_data = {
            "customer_id": "TEST_followup_customer",
            "customer_name": "Followup Test Company",
            "contact_type": "email",
            "subject": "TEST Email follow-up",
            "notes": "Testing follow-up completion",
            "contact_date": "2026-01-10",
            "follow_up_date": "2026-01-17"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/contacts",
            json=contact_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if create_response.status_code == 200:
            contact_id = create_response.json()["id"]
            
            # Mark as complete
            complete_response = requests.put(
                f"{BASE_URL}/api/contacts/{contact_id}/follow-up",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert complete_response.status_code == 200
            print(f"[PASS] Follow-up marked as complete for contact {contact_id}")
    
    def test_delete_contact(self, auth_token):
        """Test delete contact"""
        # Create a contact
        contact_data = {
            "customer_id": "TEST_delete_customer",
            "customer_name": "Delete Test Company",
            "contact_type": "meeting",
            "subject": "TEST Meeting to delete",
            "contact_date": "2026-01-05"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/contacts",
            json=contact_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if create_response.status_code == 200:
            contact_id = create_response.json()["id"]
            
            delete_response = requests.delete(
                f"{BASE_URL}/api/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert delete_response.status_code == 200
            print(f"[PASS] Contact {contact_id} deleted successfully")


class TestDocumentManagement:
    """Test document upload/download/delete operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_documents(self, auth_token):
        """Test get documents endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)
        print(f"[PASS] Get documents successful - Found {len(documents)} documents")
    
    def test_upload_document(self, auth_token):
        """Test upload document"""
        # Create a simple text file as base64
        import base64
        test_content = "This is a test document for the Service Contract Management System."
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": "TEST_general",
            "related_type": "general",
            "name": "TEST_document.txt",
            "file_type": "text/plain",
            "file_data": file_data
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents",
            json=doc_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"[PASS] Document uploaded with ID: {data['id']}")
        return data["id"]
    
    def test_get_document_by_id(self, auth_token):
        """Test get specific document"""
        import base64
        
        # First upload a document
        test_content = "Document to retrieve"
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": "TEST_retrieve",
            "related_type": "general",
            "name": "TEST_retrieve_doc.txt",
            "file_type": "text/plain",
            "file_data": file_data
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/documents",
            json=doc_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if create_response.status_code == 200:
            doc_id = create_response.json()["id"]
            
            # Get the document
            get_response = requests.get(
                f"{BASE_URL}/api/documents/{doc_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert get_response.status_code == 200
            doc = get_response.json()
            assert doc["name"] == "TEST_retrieve_doc.txt"
            assert "file_data" in doc
            print(f"[PASS] Document retrieved successfully: {doc['name']}")
    
    def test_delete_document(self, auth_token):
        """Test delete document"""
        import base64
        
        # Upload a document
        test_content = "Document to delete"
        file_data = base64.b64encode(test_content.encode()).decode()
        
        doc_data = {
            "related_id": "TEST_delete",
            "related_type": "general",
            "name": "TEST_delete_doc.txt",
            "file_type": "text/plain",
            "file_data": file_data
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/documents",
            json=doc_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if create_response.status_code == 200:
            doc_id = create_response.json()["id"]
            
            # Delete the document
            delete_response = requests.delete(
                f"{BASE_URL}/api/documents/{doc_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert delete_response.status_code == 200
            print(f"[PASS] Document {doc_id} deleted successfully")


class TestReportsAPI:
    """Test reports statistics endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_get_submission_statistics(self, auth_token):
        """Test submission statistics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/submissions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_forms" in data
        assert "submitted_forms" in data
        assert "pending_forms" in data
        assert "conversion_rate" in data
        print(f"[PASS] Submission stats - Total: {data['total_forms']}, Submitted: {data['submitted_forms']}, Rate: {data['conversion_rate']}%")
    
    def test_get_revenue_statistics(self, auth_token):
        """Test revenue statistics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/reports/revenue",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_quoted" in data
        assert "accepted_revenue" in data
        print(f"[PASS] Revenue stats - Quoted: {data['total_quoted']} SAR, Accepted: {data['accepted_revenue']} SAR")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
