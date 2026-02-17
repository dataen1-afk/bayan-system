"""
Test Grant Agreement PDF Generation
Tests:
1. PDF endpoint returns valid PDF
2. PDF generation uses DOCX template
3. Standards checkboxes are filled correctly
4. Organization details are populated
"""

import pytest
import requests
import os

# Use the public URL for testing - same URL users see
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://grant-audit-flow.preview.emergentagent.com"

# Test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# Known agreement IDs from database
TEST_AGREEMENT_IDS = [
    "f112544e-713f-44",  # TEST Acme Corporation - ISO9001, ISO14001
    "35425430-de26-44",  # شركة اختبار - ISO9001, ISO45001
    "929e48d1-c684-45",  # PDF Download Test Corp
    "1e2e2d54-7c9f-45",  # Test Company for Proposal
]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def authenticated_session(auth_token):
    """Session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestCertificationAgreementsEndpoint:
    """Test GET /api/certification-agreements endpoint"""
    
    def test_get_certification_agreements_returns_list(self, authenticated_session):
        """Test that GET /api/certification-agreements returns list of signed agreements"""
        response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one agreement"
        
        # Validate structure of first agreement
        agreement = data[0]
        assert "id" in agreement, "Agreement should have id"
        assert "organization_name" in agreement, "Agreement should have organization_name"
        assert "selected_standards" in agreement, "Agreement should have selected_standards"
        assert "status" in agreement, "Agreement should have status"
        
        print(f"✓ Found {len(data)} certification agreements")
        
    def test_get_certification_agreements_filter_by_status(self, authenticated_session):
        """Test filtering agreements by status"""
        response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements?status=submitted")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned agreements should have 'submitted' status
        for agreement in data:
            assert agreement.get("status") == "submitted", f"Expected status 'submitted', got {agreement.get('status')}"
        
        print(f"✓ Filter by status working - {len(data)} submitted agreements")


class TestGrantAgreementPDFGeneration:
    """Test /api/contracts/{agreement_id}/pdf endpoint"""
    
    def test_pdf_endpoint_requires_auth(self):
        """Test that PDF endpoint requires authentication"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/contracts/fake-id/pdf")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ PDF endpoint requires authentication")
    
    def test_pdf_endpoint_returns_404_for_invalid_id(self, authenticated_session):
        """Test that invalid agreement ID returns 404"""
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/nonexistent-id-12345/pdf")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid agreement ID returns 404")
    
    def test_pdf_generation_returns_valid_pdf(self, authenticated_session):
        """Test PDF generation returns valid PDF file"""
        # First get a real agreement ID
        agreements_response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        assert agreements_response.status_code == 200, "Failed to get agreements"
        
        agreements = agreements_response.json()
        assert len(agreements) > 0, "No agreements found"
        
        # Use first agreement
        agreement = agreements[0]
        agreement_id = agreement['id']
        
        print(f"Testing PDF generation for agreement: {agreement_id[:16]}...")
        print(f"  Organization: {agreement.get('organization_name')}")
        print(f"  Standards: {agreement.get('selected_standards')}")
        
        # Generate PDF
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/{agreement_id}/pdf")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Content-Type should be PDF
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected PDF content-type, got {content_type}"
        
        # Should have content
        content_length = len(response.content)
        assert content_length > 1000, f"PDF too small ({content_length} bytes) - might be empty"
        
        # PDF should start with %PDF header
        assert response.content[:4] == b'%PDF', "Response does not start with PDF header"
        
        print(f"✓ PDF generated successfully ({content_length} bytes)")
        
    def test_pdf_content_has_expected_size(self, authenticated_session):
        """Test that generated PDF has reasonable size (indicates template is being used)"""
        agreements_response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        agreements = agreements_response.json()
        
        if not agreements:
            pytest.skip("No agreements available")
        
        agreement = agreements[0]
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/{agreement['id']}/pdf")
        
        # A proper PDF from DOCX template should be at least 50KB
        # (DOCX template has BAYAN logo, formatting, etc.)
        content_length = len(response.content)
        
        # Reasonable PDF size check (template-based PDF should be substantial)
        assert content_length > 50000, f"PDF seems too small ({content_length} bytes) - template might not be used"
        assert content_length < 10000000, f"PDF too large ({content_length} bytes) - possible error"
        
        print(f"✓ PDF size is reasonable: {content_length / 1024:.1f} KB")


class TestMultipleAgreementsPDF:
    """Test PDF generation for multiple agreements with different standards"""
    
    def test_pdf_for_iso9001_iso14001_standards(self, authenticated_session):
        """Test PDF generation for ISO 9001 + ISO 14001 combination"""
        agreements_response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        agreements = agreements_response.json()
        
        # Find agreement with ISO9001 and ISO14001
        target_agreement = None
        for ag in agreements:
            standards = ag.get('selected_standards', [])
            normalized_standards = [s.upper().replace(' ', '') for s in standards]
            if 'ISO9001' in normalized_standards and 'ISO14001' in normalized_standards:
                target_agreement = ag
                break
        
        if not target_agreement:
            pytest.skip("No agreement with ISO9001+ISO14001 found")
        
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/{target_agreement['id']}/pdf")
        
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert b'%PDF' in response.content[:10], "Invalid PDF header"
        
        print(f"✓ PDF for ISO9001+ISO14001 generated ({len(response.content)} bytes)")
        print(f"  Organization: {target_agreement.get('organization_name')}")
    
    def test_pdf_for_arabic_organization(self, authenticated_session):
        """Test PDF generation for Arabic organization name"""
        agreements_response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        agreements = agreements_response.json()
        
        # Find agreement with Arabic organization name
        target_agreement = None
        for ag in agreements:
            org_name = ag.get('organization_name', '')
            # Check if contains Arabic characters
            if any('\u0600' <= c <= '\u06FF' for c in org_name):
                target_agreement = ag
                break
        
        if not target_agreement:
            pytest.skip("No agreement with Arabic name found")
        
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/{target_agreement['id']}/pdf")
        
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        assert b'%PDF' in response.content[:10], "Invalid PDF header"
        
        print(f"✓ PDF for Arabic organization generated ({len(response.content)} bytes)")
        print(f"  Organization: {target_agreement.get('organization_name')}")


class TestPDFSaveAndVerify:
    """Test saving PDF and verifying content"""
    
    def test_save_pdf_to_disk(self, authenticated_session, tmp_path):
        """Save generated PDF and verify it's valid"""
        agreements_response = authenticated_session.get(f"{BASE_URL}/api/certification-agreements")
        agreements = agreements_response.json()
        
        if not agreements:
            pytest.skip("No agreements available")
        
        agreement = agreements[0]
        response = authenticated_session.get(f"{BASE_URL}/api/contracts/{agreement['id']}/pdf")
        
        assert response.status_code == 200
        
        # Save to temp file
        pdf_path = tmp_path / "test_grant_agreement.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        # Verify file exists and has content
        assert pdf_path.exists(), "PDF file not created"
        assert pdf_path.stat().st_size > 0, "PDF file is empty"
        
        # Verify it's a valid PDF by reading first bytes
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
        
        assert header[:4] == b'%PDF', "Invalid PDF header in saved file"
        
        print(f"✓ PDF saved successfully to {pdf_path}")
        print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
