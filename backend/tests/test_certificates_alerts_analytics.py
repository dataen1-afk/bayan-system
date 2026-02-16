"""
Test suite for Certificates, Expiration Alerts, and Analytics Dashboard APIs
Phase 4, 5, 6 features testing - iteration 21
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSetup:
    """Setup tests - authentication and prerequisites"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping tests")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Return headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestCertificatesAPI(TestSetup):
    """Test Certificate Management API endpoints"""
    
    def test_get_certificates_list(self, headers):
        """GET /api/certificates - List all certificates"""
        response = requests.get(f"{BASE_URL}/api/certificates", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of certificates"
        print(f"✓ GET /api/certificates - Found {len(data)} certificates")
    
    def test_get_certificates_stats(self, headers):
        """GET /api/certificates/stats - Get certificate statistics"""
        response = requests.get(f"{BASE_URL}/api/certificates/stats", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "total_certificates" in data, "Missing total_certificates"
        assert "active_count" in data, "Missing active_count"
        assert "expired_count" in data, "Missing expired_count"
        assert "suspended_count" in data, "Missing suspended_count"
        assert "expiring_soon_count" in data, "Missing expiring_soon_count"
        
        # Validate data types
        assert isinstance(data["total_certificates"], int)
        assert isinstance(data["active_count"], int)
        
        print(f"✓ GET /api/certificates/stats - Stats: total={data['total_certificates']}, active={data['active_count']}, expiring_soon={data['expiring_soon_count']}")
    
    def test_get_certificates_filtered_by_status(self, headers):
        """GET /api/certificates?status=active - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/certificates?status=active", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify all returned certs are active (if any returned)
        for cert in data:
            assert cert.get('status') == 'active', f"Expected active status, got {cert.get('status')}"
        
        print(f"✓ GET /api/certificates?status=active - Found {len(data)} active certificates")
    
    def test_certificates_requires_auth(self):
        """GET /api/certificates - Should require authentication"""
        response = requests.get(f"{BASE_URL}/api/certificates")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {response.status_code}"
        print("✓ GET /api/certificates requires authentication")
    
    def test_certificates_stats_requires_auth(self):
        """GET /api/certificates/stats - Should require authentication"""
        response = requests.get(f"{BASE_URL}/api/certificates/stats")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {response.status_code}"
        print("✓ GET /api/certificates/stats requires authentication")


class TestCertificateCreateAndManage(TestSetup):
    """Test Certificate Creation and Management"""
    
    def test_create_certificate_requires_valid_contract(self, headers):
        """POST /api/certificates - Should require valid contract_id"""
        response = requests.post(f"{BASE_URL}/api/certificates", headers=headers, json={
            "contract_id": "nonexistent-contract-id",
            "standards": ["ISO 9001"],
            "scope": "Test scope"
        })
        assert response.status_code == 404, f"Expected 404 for nonexistent contract, got {response.status_code}"
        print("✓ POST /api/certificates - Validates contract_id exists")
    
    def test_create_certificate_requires_auth(self):
        """POST /api/certificates - Should require authentication"""
        response = requests.post(f"{BASE_URL}/api/certificates", json={
            "contract_id": "test",
            "standards": ["ISO 9001"]
        })
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {response.status_code}"
        print("✓ POST /api/certificates requires authentication")
    
    def test_get_nonexistent_certificate(self, headers):
        """GET /api/certificates/{id} - Should return 404 for nonexistent"""
        response = requests.get(f"{BASE_URL}/api/certificates/nonexistent-cert-id", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/certificates/{id} - Returns 404 for nonexistent")
    
    def test_update_status_nonexistent_certificate(self, headers):
        """PUT /api/certificates/{id}/status - Should return 404 for nonexistent"""
        response = requests.put(
            f"{BASE_URL}/api/certificates/nonexistent-cert-id/status",
            headers=headers,
            json={"status": "suspended"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ PUT /api/certificates/{id}/status - Returns 404 for nonexistent")
    
    def test_update_status_invalid_status(self, headers):
        """PUT /api/certificates/{id}/status - Should reject invalid status"""
        # First get a certificate if any exists
        certs_response = requests.get(f"{BASE_URL}/api/certificates", headers=headers)
        certs = certs_response.json()
        
        if len(certs) == 0:
            pytest.skip("No certificates available to test status update")
        
        cert_id = certs[0]['id']
        response = requests.put(
            f"{BASE_URL}/api/certificates/{cert_id}/status",
            headers=headers,
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
        print("✓ PUT /api/certificates/{id}/status - Rejects invalid status")


class TestPublicCertificateVerification(TestSetup):
    """Test Public Certificate Verification API"""
    
    def test_verify_certificate_nonexistent(self):
        """GET /api/public/verify/{cert_number} - Should return 404 for nonexistent"""
        response = requests.get(f"{BASE_URL}/api/public/verify/CERT-XXXX-XXXX")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/public/verify/{cert_number} - Returns 404 for nonexistent")
    
    def test_verify_certificate_no_auth_required(self, headers):
        """GET /api/public/verify/{cert_number} - Should NOT require authentication"""
        # First check if we have any certificates
        certs_response = requests.get(f"{BASE_URL}/api/certificates", headers=headers)
        certs = certs_response.json()
        
        if len(certs) == 0:
            # Even without certificates, the 404 response without auth proves no auth required
            response = requests.get(f"{BASE_URL}/api/public/verify/CERT-0000-0001")
            assert response.status_code == 404, "Expected 404 without needing auth"
            print("✓ GET /api/public/verify - No auth required (404 without auth)")
            return
        
        cert_number = certs[0].get('certificate_number')
        # Request without auth header
        response = requests.get(f"{BASE_URL}/api/public/verify/{cert_number}")
        # Should get 200 (valid cert) or proper response, not 401/403
        assert response.status_code not in [401, 403], f"Public verify should not require auth, got {response.status_code}"
        
        data = response.json()
        assert "valid" in data, "Response should include 'valid' field"
        assert "certificate_number" in data, "Response should include certificate_number"
        assert "organization_name" in data, "Response should include organization_name"
        
        print(f"✓ GET /api/public/verify/{cert_number} - Public access works, valid={data.get('valid')}")


class TestExpirationAlertsAPI(TestSetup):
    """Test Expiration Alerts API endpoints"""
    
    def test_get_expiring_alerts_default(self, headers):
        """GET /api/alerts/expiring - Get expiring items (default 90 days)"""
        response = requests.get(f"{BASE_URL}/api/alerts/expiring", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "summary" in data, "Missing summary"
        assert "alerts" in data, "Missing alerts"
        
        summary = data["summary"]
        assert "total_alerts" in summary, "Missing total_alerts in summary"
        assert "critical_count" in summary, "Missing critical_count in summary"
        assert "warning_count" in summary, "Missing warning_count in summary"
        assert "info_count" in summary, "Missing info_count in summary"
        
        alerts = data["alerts"]
        assert "critical" in alerts, "Missing critical alerts"
        assert "warning" in alerts, "Missing warning alerts"
        assert "info" in alerts, "Missing info alerts"
        
        print(f"✓ GET /api/alerts/expiring - Total: {summary['total_alerts']}, Critical: {summary['critical_count']}, Warning: {summary['warning_count']}, Info: {summary['info_count']}")
    
    def test_get_expiring_alerts_30_days(self, headers):
        """GET /api/alerts/expiring?days=30 - Get items expiring in 30 days"""
        response = requests.get(f"{BASE_URL}/api/alerts/expiring?days=30", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "summary" in data
        assert "alerts" in data
        
        print(f"✓ GET /api/alerts/expiring?days=30 - Total: {data['summary']['total_alerts']}")
    
    def test_get_expiring_alerts_180_days(self, headers):
        """GET /api/alerts/expiring?days=180 - Get items expiring in 180 days"""
        response = requests.get(f"{BASE_URL}/api/alerts/expiring?days=180", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "summary" in data
        assert "alerts" in data
        
        print(f"✓ GET /api/alerts/expiring?days=180 - Total: {data['summary']['total_alerts']}")
    
    def test_alerts_requires_auth(self):
        """GET /api/alerts/expiring - Should require authentication"""
        response = requests.get(f"{BASE_URL}/api/alerts/expiring")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {response.status_code}"
        print("✓ GET /api/alerts/expiring requires authentication")
    
    def test_alerts_data_structure(self, headers):
        """Validate alert item structure"""
        response = requests.get(f"{BASE_URL}/api/alerts/expiring?days=180", headers=headers)
        data = response.json()
        
        all_alerts = data["alerts"]["critical"] + data["alerts"]["warning"] + data["alerts"]["info"]
        
        if len(all_alerts) > 0:
            alert = all_alerts[0]
            assert "type" in alert, "Alert missing 'type' field"
            assert "id" in alert, "Alert missing 'id' field"
            assert "reference" in alert, "Alert missing 'reference' field"
            assert "expiry_date" in alert, "Alert missing 'expiry_date' field"
            assert "days_until_expiry" in alert, "Alert missing 'days_until_expiry' field"
            print(f"✓ Alert structure validated: type={alert['type']}, days_until={alert['days_until_expiry']}")
        else:
            print("✓ Alert structure test - No alerts to validate (empty result)")


class TestAnalyticsDashboardAPI(TestSetup):
    """Test Analytics Dashboard API endpoints"""
    
    def test_get_dashboard_analytics(self, headers):
        """GET /api/dashboard/analytics - Get comprehensive analytics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "overview" in data, "Missing overview"
        assert "conversion_rates" in data, "Missing conversion_rates"
        assert "revenue" in data, "Missing revenue"
        assert "monthly_trends" in data, "Missing monthly_trends"
        assert "standards_breakdown" in data, "Missing standards_breakdown"
        assert "audits" in data, "Missing audits"
        
        print(f"✓ GET /api/dashboard/analytics - Data structure validated")
    
    def test_analytics_overview_fields(self, headers):
        """Validate overview section of analytics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        data = response.json()
        
        overview = data["overview"]
        assert "total_forms" in overview, "Missing total_forms"
        assert "total_proposals" in overview, "Missing total_proposals"
        assert "total_contracts" in overview, "Missing total_contracts"
        assert "total_certificates" in overview, "Missing total_certificates"
        assert "active_certificates" in overview, "Missing active_certificates"
        
        # Validate data types
        assert isinstance(overview["total_forms"], int)
        assert isinstance(overview["total_proposals"], int)
        assert isinstance(overview["total_contracts"], int)
        
        print(f"✓ Analytics Overview: forms={overview['total_forms']}, proposals={overview['total_proposals']}, contracts={overview['total_contracts']}, certificates={overview['total_certificates']}")
    
    def test_analytics_conversion_rates(self, headers):
        """Validate conversion rates in analytics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        data = response.json()
        
        rates = data["conversion_rates"]
        assert "form_to_proposal" in rates, "Missing form_to_proposal rate"
        assert "proposal_to_contract" in rates, "Missing proposal_to_contract rate"
        assert "overall" in rates, "Missing overall rate"
        
        # Validate rates are numbers
        assert isinstance(rates["form_to_proposal"], (int, float))
        assert isinstance(rates["proposal_to_contract"], (int, float))
        assert isinstance(rates["overall"], (int, float))
        
        print(f"✓ Conversion Rates: form_to_proposal={rates['form_to_proposal']}%, proposal_to_contract={rates['proposal_to_contract']}%, overall={rates['overall']}%")
    
    def test_analytics_revenue(self, headers):
        """Validate revenue section in analytics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        data = response.json()
        
        revenue = data["revenue"]
        assert "total_quoted" in revenue, "Missing total_quoted"
        assert "total_accepted" in revenue, "Missing total_accepted"
        assert "total_invoiced" in revenue, "Missing total_invoiced"
        assert "total_collected" in revenue, "Missing total_collected"
        assert "collection_rate" in revenue, "Missing collection_rate"
        
        print(f"✓ Revenue: quoted={revenue['total_quoted']}, accepted={revenue['total_accepted']}, collected={revenue['total_collected']}, collection_rate={revenue['collection_rate']}%")
    
    def test_analytics_monthly_trends(self, headers):
        """Validate monthly trends data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        data = response.json()
        
        monthly = data["monthly_trends"]
        assert isinstance(monthly, list), "monthly_trends should be a list"
        
        if len(monthly) > 0:
            month_data = monthly[0]
            assert "month" in month_data, "Missing month field"
            assert "forms" in month_data, "Missing forms field"
            assert "proposals" in month_data, "Missing proposals field"
            assert "contracts" in month_data, "Missing contracts field"
        
        print(f"✓ Monthly Trends: {len(monthly)} months of data")
    
    def test_analytics_audits(self, headers):
        """Validate audit statistics in analytics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics", headers=headers)
        data = response.json()
        
        audits = data["audits"]
        assert "total" in audits, "Missing total audits"
        assert "completed" in audits, "Missing completed audits"
        assert "scheduled" in audits, "Missing scheduled audits"
        assert "pending" in audits, "Missing pending audits"
        
        print(f"✓ Audit Stats: total={audits['total']}, completed={audits['completed']}, scheduled={audits['scheduled']}, pending={audits['pending']}")
    
    def test_analytics_requires_auth(self):
        """GET /api/dashboard/analytics - Should require authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/analytics")
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {response.status_code}"
        print("✓ GET /api/dashboard/analytics requires authentication")


class TestCertificationAgreements(TestSetup):
    """Test Certification Agreements endpoint for certificate creation"""
    
    def test_get_certification_agreements(self, headers):
        """GET /api/certification-agreements - List agreements for certificate creation"""
        response = requests.get(f"{BASE_URL}/api/certification-agreements", headers=headers)
        # This endpoint may not exist - check status
        if response.status_code == 404:
            pytest.skip("Certification agreements endpoint not available")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of agreements"
        
        signed_count = len([a for a in data if a.get('status') == 'signed'])
        print(f"✓ GET /api/certification-agreements - Found {len(data)} agreements, {signed_count} signed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
