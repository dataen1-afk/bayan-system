"""
Test cases for iteration 7 new features:
1. Contract Statistics Summary Cards on Contracts page
2. Template edit functionality (PUT endpoints for packages and proposals)
3. ApplicationForm sticky footer (frontend validation via API)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agreement-hub-14.preview.emergentagent.com').rstrip('/')


class TestAuth:
    """Authentication helper tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()['token']
    
    def test_login_success(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user' in data
        print("Login successful")


class TestContractStatistics:
    """Test contract statistics data availability for frontend display"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        return response.json()['token']
    
    def test_proposals_endpoint_returns_data(self, auth_token):
        """Test that proposals endpoint returns data for statistics calculation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/proposals", headers=headers)
        
        assert response.status_code == 200
        proposals = response.json()
        assert isinstance(proposals, list)
        
        # Check if there are agreement_signed proposals (contracts)
        signed_contracts = [p for p in proposals if p.get('status') == 'agreement_signed']
        print(f"Total proposals: {len(proposals)}")
        print(f"Signed contracts: {len(signed_contracts)}")
        
        if signed_contracts:
            # Verify contract has required fields for statistics
            contract = signed_contracts[0]
            assert 'total_amount' in contract, "Contract should have total_amount"
            assert 'organization_name' in contract, "Contract should have organization_name"
            print(f"First contract: {contract.get('organization_name')} - {contract.get('total_amount')} SAR")
    
    def test_statistics_calculation(self, auth_token):
        """Test that statistics can be calculated from proposals"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/proposals", headers=headers)
        
        assert response.status_code == 200
        proposals = response.json()
        
        # Filter signed contracts
        signed_contracts = [p for p in proposals if p.get('status') == 'agreement_signed']
        
        # Calculate statistics
        total_contracts = len(signed_contracts)
        total_revenue = sum(c.get('total_amount', 0) for c in signed_contracts)
        most_recent = max(signed_contracts, key=lambda x: x.get('client_response_date', ''), default=None) if signed_contracts else None
        
        print(f"Total Contracts: {total_contracts}")
        print(f"Total Revenue: {total_revenue} SAR")
        if most_recent:
            print(f"Most Recent: {most_recent.get('organization_name')}")
        
        # Verify expected values based on test data
        assert total_contracts >= 1, "Should have at least 1 signed contract"
        assert total_revenue > 0, "Total revenue should be positive"


class TestTemplatePackagesUpdate:
    """Test PUT /api/templates/packages/{id} endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        return response.json()['token']
    
    @pytest.fixture
    def test_package(self, auth_token):
        """Create a test package and clean up after"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create test package
        create_data = {
            "name": "TEST_Package_Update",
            "name_ar": "حزمة اختبار التحديث",
            "description": "Test package for update testing",
            "description_ar": "حزمة اختبار للتحديث",
            "standards": ["ISO9001"],
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/templates/packages", json=create_data, headers=headers)
        assert response.status_code == 200
        package_id = response.json()['id']
        
        yield package_id
        
        # Cleanup: Delete the test package
        requests.delete(f"{BASE_URL}/api/templates/packages/{package_id}", headers=headers)
    
    def test_update_package_success(self, auth_token, test_package):
        """Test successful package update"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        package_id = test_package
        
        # Update package
        update_data = {
            "name": "TEST_Package_Updated",
            "name_ar": "حزمة اختبار محدثة",
            "description": "Updated description",
            "description_ar": "الوصف المحدث",
            "standards": ["ISO9001", "ISO14001"],
            "is_active": True
        }
        response = requests.put(f"{BASE_URL}/api/templates/packages/{package_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        assert data.get('message') == 'Package updated'
        print(f"Package updated successfully: {package_id}")
        
        # Verify update by fetching packages
        list_response = requests.get(f"{BASE_URL}/api/templates/packages", headers=headers)
        packages = list_response.json()
        updated_package = next((p for p in packages if p['id'] == package_id), None)
        
        if updated_package:
            assert updated_package['name'] == "TEST_Package_Updated"
            assert "ISO14001" in updated_package['standards']
            print(f"Verified: name={updated_package['name']}, standards={updated_package['standards']}")
    
    def test_update_package_unauthorized(self, test_package):
        """Test package update without authentication"""
        package_id = test_package
        
        update_data = {
            "name": "Unauthorized Update",
            "name_ar": "تحديث غير مصرح",
            "description": "",
            "description_ar": "",
            "standards": ["ISO9001"]
        }
        response = requests.put(f"{BASE_URL}/api/templates/packages/{package_id}", json=update_data)
        
        # Should fail without auth
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("Unauthorized update correctly rejected")


class TestProposalTemplatesUpdate:
    """Test PUT /api/templates/proposals/{id} endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        return response.json()['token']
    
    @pytest.fixture
    def test_template(self, auth_token):
        """Create a test proposal template and clean up after"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create test template
        create_data = {
            "name": "TEST_Template_Update",
            "name_ar": "قالب اختبار التحديث",
            "description": "Test template for update testing",
            "default_fees": {
                "initial_certification": 10000,
                "surveillance_1": 5000,
                "surveillance_2": 5000,
                "recertification": 8000
            },
            "default_notes": "Test notes",
            "default_validity_days": 30,
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/templates/proposals", json=create_data, headers=headers)
        assert response.status_code == 200
        template_id = response.json()['id']
        
        yield template_id
        
        # Cleanup: Delete the test template
        requests.delete(f"{BASE_URL}/api/templates/proposals/{template_id}", headers=headers)
    
    def test_update_template_success(self, auth_token, test_template):
        """Test successful proposal template update"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        template_id = test_template
        
        # Update template
        update_data = {
            "name": "TEST_Template_Updated",
            "name_ar": "قالب اختبار محدث",
            "description": "Updated template description",
            "default_fees": {
                "initial_certification": 15000,
                "surveillance_1": 7000,
                "surveillance_2": 7000,
                "recertification": 12000
            },
            "default_notes": "Updated notes",
            "default_validity_days": 45,
            "is_active": True
        }
        response = requests.put(f"{BASE_URL}/api/templates/proposals/{template_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        assert data.get('message') == 'Template updated'
        print(f"Template updated successfully: {template_id}")
        
        # Verify update by fetching templates
        list_response = requests.get(f"{BASE_URL}/api/templates/proposals", headers=headers)
        templates = list_response.json()
        updated_template = next((t for t in templates if t['id'] == template_id), None)
        
        if updated_template:
            assert updated_template['name'] == "TEST_Template_Updated"
            assert updated_template['default_fees']['initial_certification'] == 15000
            assert updated_template['default_validity_days'] == 45
            print(f"Verified: name={updated_template['name']}, fees={updated_template['default_fees']}")
    
    def test_update_template_unauthorized(self, test_template):
        """Test template update without authentication"""
        template_id = test_template
        
        update_data = {
            "name": "Unauthorized Update",
            "name_ar": "تحديث غير مصرح",
            "description": "",
            "default_fees": {},
            "default_notes": "",
            "default_validity_days": 30
        }
        response = requests.put(f"{BASE_URL}/api/templates/proposals/{template_id}", json=update_data)
        
        # Should fail without auth
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print("Unauthorized update correctly rejected")


class TestApplicationForms:
    """Test application forms for sticky footer context"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        return response.json()['token']
    
    def test_get_pending_forms(self, auth_token):
        """Test that pending forms exist for form testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/application-forms", headers=headers)
        
        assert response.status_code == 200
        forms = response.json()
        pending_forms = [f for f in forms if f.get('status') == 'pending']
        
        print(f"Total forms: {len(forms)}")
        print(f"Pending forms (for sticky footer test): {len(pending_forms)}")
        
        if pending_forms:
            form = pending_forms[0]
            assert 'access_token' in form
            print(f"Form access URL: /form/{form['access_token']}")
    
    def test_public_form_access(self, auth_token):
        """Test public form endpoint works for sticky footer form"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get a pending form
        response = requests.get(f"{BASE_URL}/api/application-forms", headers=headers)
        forms = response.json()
        pending_forms = [f for f in forms if f.get('status') == 'pending']
        
        if not pending_forms:
            pytest.skip("No pending forms available")
        
        access_token = pending_forms[0]['access_token']
        
        # Test public access
        public_response = requests.get(f"{BASE_URL}/api/public/form/{access_token}")
        assert public_response.status_code == 200
        
        form_data = public_response.json()
        assert 'id' in form_data
        assert 'client_info' in form_data
        assert 'status' in form_data
        print(f"Public form access works: {form_data['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
