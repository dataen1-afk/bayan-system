"""
Test Customer Portal APIs: RFQ and Contact Form submissions
These are public endpoints that don't require authentication
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRFQEndpoint:
    """Test RFQ (Request for Quotation) submission endpoint"""
    
    def test_rfq_submission_success(self):
        """Test successful RFQ submission"""
        rfq_data = {
            "company_name": f"TEST_Company_{uuid.uuid4().hex[:8]}",
            "contact_name": "Test Contact Person",
            "email": "test@testcompany.com",
            "phone": "+966 50 123 4567",
            "employees": "50",
            "sites": "2",
            "standards": ["ISO 9001:2015", "ISO 14001:2015"],
            "message": "We need ISO certification for our operations"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        
        assert response.status_code == 200, f"RFQ submission failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "id" in data
        assert data["message"] == "RFQ submitted successfully"
        print(f"✓ RFQ submitted successfully with ID: {data['id']}")
    
    def test_rfq_submission_minimal_data(self):
        """Test RFQ submission with minimal required data"""
        rfq_data = {
            "company_name": f"TEST_Minimal_{uuid.uuid4().hex[:8]}",
            "contact_name": "Minimal Contact",
            "email": "minimal@test.com",
            "phone": "+966 50 000 0000",
            "standards": ["ISO 9001:2015"]
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        
        assert response.status_code == 200, f"Minimal RFQ failed: {response.text}"
        print("✓ RFQ with minimal data submitted successfully")
    
    def test_rfq_submission_missing_required_field(self):
        """Test RFQ submission fails without required fields"""
        rfq_data = {
            "company_name": "Test Company",
            # Missing contact_name, email, phone
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 but got {response.status_code}"
        print("✓ RFQ correctly rejects incomplete data")
    
    def test_rfq_with_all_five_standards(self):
        """Test RFQ with all 5 ISO standards"""
        rfq_data = {
            "company_name": f"TEST_AllStandards_{uuid.uuid4().hex[:8]}",
            "contact_name": "Full Service Contact",
            "email": "fullservice@test.com",
            "phone": "+966 50 999 9999",
            "employees": "200",
            "sites": "5",
            "standards": [
                "ISO 9001:2015", 
                "ISO 14001:2015", 
                "ISO 45001:2018",
                "ISO 22000:2018",
                "ISO 27001:2022"
            ],
            "message": "We need comprehensive certification for all standards"
        }
        
        response = requests.post(f"{BASE_URL}/api/public/rfq", json=rfq_data)
        
        assert response.status_code == 200, f"Full standards RFQ failed: {response.text}"
        print("✓ RFQ with all 5 standards submitted successfully")


class TestContactEndpoint:
    """Test Contact Form submission endpoint"""
    
    def test_contact_form_success(self):
        """Test successful contact form submission"""
        contact_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "subject": "Inquiry about ISO Certification",
            "message": "I would like more information about your certification services."
        }
        
        response = requests.post(f"{BASE_URL}/api/public/contact", json=contact_data)
        
        assert response.status_code == 200, f"Contact form failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert data["message"] == "Message sent successfully"
        print("✓ Contact form submitted successfully")
    
    def test_contact_form_arabic_content(self):
        """Test contact form with Arabic content"""
        contact_data = {
            "name": "محمد أحمد",
            "email": "mohammed@example.com",
            "subject": "استفسار عن شهادة الجودة",
            "message": "أرغب في الحصول على معلومات إضافية حول خدمات الاعتماد الخاصة بكم."
        }
        
        response = requests.post(f"{BASE_URL}/api/public/contact", json=contact_data)
        
        assert response.status_code == 200, f"Arabic contact form failed: {response.text}"
        print("✓ Contact form with Arabic content submitted successfully")
    
    def test_contact_form_missing_required_field(self):
        """Test contact form fails without required fields"""
        contact_data = {
            "name": "Test User",
            # Missing email, subject, message
        }
        
        response = requests.post(f"{BASE_URL}/api/public/contact", json=contact_data)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422 but got {response.status_code}"
        print("✓ Contact form correctly rejects incomplete data")


class TestTrackingEndpoint:
    """Test order tracking endpoint"""
    
    def test_track_nonexistent_order(self):
        """Test tracking with a non-existent tracking ID"""
        response = requests.get(f"{BASE_URL}/api/public/track/TRK-INVALID123")
        
        assert response.status_code == 404, f"Expected 404 but got {response.status_code}"
        print("✓ Tracking correctly returns 404 for invalid ID")


class TestHealthCheck:
    """Test that the API is reachable"""
    
    def test_api_health(self):
        """Verify the API is responding"""
        response = requests.get(f"{BASE_URL}/api/")
        
        # Can be 200 or 404 for root, but should connect
        assert response.status_code in [200, 404], f"API unreachable: {response.status_code}"
        print(f"✓ API is reachable (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
