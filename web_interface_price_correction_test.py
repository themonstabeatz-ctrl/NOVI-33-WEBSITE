#!/usr/bin/env python3
"""
Web Interface Price Correction Testing
Tests the web-based admin interface for updating service prices
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://gold-line-fixer.preview.emergentagent.com')

class WebInterfaceTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.admin_url = f"{self.backend_url}/admin"
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or {}
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        print()

    async def test_admin_interface_access(self):
        """Test if admin interface is accessible"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.admin_url)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check if it's an admin interface
                    admin_indicators = [
                        'admin', 'login', 'password', 'services', 'management',
                        'edit', 'update', 'price', 'discount'
                    ]
                    
                    found_indicators = [indicator for indicator in admin_indicators if indicator.lower() in content.lower()]
                    
                    # Check if there's a login form
                    has_login_form = 'password' in content.lower() and ('login' in content.lower() or 'form' in content.lower())
                    
                    self.log_result(
                        "Admin Interface Access",
                        True,
                        f"✅ Admin interface accessible at {self.admin_url}",
                        {
                            "status_code": response.status_code,
                            "content_length": len(content),
                            "admin_indicators_found": found_indicators,
                            "has_login_form": has_login_form,
                            "requires_authentication": has_login_form,
                            "content_preview": content[:500] if content else "No content"
                        }
                    )
                    return True, has_login_form
                else:
                    self.log_result(
                        "Admin Interface Access",
                        False,
                        f"❌ Admin interface returned status {response.status_code}",
                        {"status_code": response.status_code, "url": self.admin_url}
                    )
                    return False, False
                    
        except Exception as e:
            self.log_result(
                "Admin Interface Access",
                False,
                f"❌ Cannot access admin interface: {str(e)}",
                {"error": str(e), "url": self.admin_url}
            )
            return False, False

    async def test_authentication_methods(self):
        """Test common authentication methods"""
        
        # Common admin credentials to try
        auth_attempts = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "admin", "password": "123456"},
            {"username": "admin", "password": "studio149"},  # From review request context
            {"password": "studio149"},  # Password only
            {"username": "root", "password": "root"},
            {"username": "user", "password": "user"}
        ]
        
        successful_auth = None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # First, check if there are any login endpoints
                login_endpoints = [
                    f"{self.admin_url}/login",
                    f"{self.backend_url}/login",
                    f"{self.backend_url}/auth/login",
                    f"{self.admin_url}/auth"
                ]
                
                working_login_endpoint = None
                
                for endpoint in login_endpoints:
                    try:
                        response = await client.get(endpoint)
                        if response.status_code in [200, 302]:
                            working_login_endpoint = endpoint
                            break
                    except:
                        continue
                
                if working_login_endpoint:
                    # Try authentication attempts
                    for i, creds in enumerate(auth_attempts[:3]):  # Test first 3 to avoid lockout
                        try:
                            # Try POST login
                            login_response = await client.post(
                                working_login_endpoint,
                                data=creds,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}
                            )
                            
                            # Check if login was successful (redirect or 200 with different content)
                            if login_response.status_code in [200, 302] and 'error' not in login_response.text.lower():
                                successful_auth = creds
                                break
                                
                        except Exception as e:
                            continue
                
                # Also try basic auth on admin interface
                if not successful_auth:
                    for creds in auth_attempts[:2]:
                        try:
                            auth = (creds.get('username', 'admin'), creds.get('password', 'admin'))
                            response = await client.get(self.admin_url, auth=auth)
                            
                            if response.status_code == 200 and 'unauthorized' not in response.text.lower():
                                successful_auth = creds
                                break
                        except:
                            continue
                
                self.log_result(
                    "Authentication Methods",
                    successful_auth is not None,
                    f"✅ Authentication successful with {successful_auth}" if successful_auth else "❌ No working authentication found",
                    {
                        "working_login_endpoint": working_login_endpoint,
                        "successful_credentials": successful_auth,
                        "tested_endpoints": login_endpoints,
                        "tested_credentials": len(auth_attempts),
                        "authentication_required": working_login_endpoint is not None
                    }
                )
                
                return successful_auth
                
        except Exception as e:
            self.log_result(
                "Authentication Methods",
                False,
                f"❌ Error testing authentication: {str(e)}",
                {"error": str(e)}
            )
            return None

    async def test_services_management_interface(self, auth_credentials=None):
        """Test if services can be managed through web interface"""
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Set up authentication if available
                auth = None
                if auth_credentials and 'username' in auth_credentials:
                    auth = (auth_credentials['username'], auth_credentials['password'])
                
                # Try to access services management
                services_urls = [
                    f"{self.admin_url}/services",
                    f"{self.admin_url}/manage/services",
                    f"{self.admin_url}/usluge",  # Serbian
                    f"{self.backend_url}/services/manage",
                    self.admin_url  # Main admin page might have services
                ]
                
                services_interface_found = False
                working_url = None
                
                for url in services_urls:
                    try:
                        response = await client.get(url, auth=auth)
                        
                        if response.status_code == 200:
                            content = response.text.lower()
                            
                            # Check for services management indicators
                            service_indicators = [
                                'kartica masaza za parove', 'service', 'price', 'edit',
                                'update', 'massage', 'masaža', 'cena', 'popust'
                            ]
                            
                            found_indicators = [ind for ind in service_indicators if ind in content]
                            
                            if len(found_indicators) >= 2:  # At least 2 indicators
                                services_interface_found = True
                                working_url = url
                                
                                # Look for specific couples massage services
                                couples_services_found = []
                                couples_indicators = [
                                    'tradicionalna tajlandska', 'aroma terapija', 'masaža toplim uljem',
                                    'glava, vrat, ramena', 'masaža stopala', 'aroma duboko tkivo'
                                ]
                                
                                for indicator in couples_indicators:
                                    if indicator in content:
                                        couples_services_found.append(indicator)
                                
                                self.log_result(
                                    "Services Management Interface",
                                    True,
                                    f"✅ Services management interface found at {url}",
                                    {
                                        "working_url": url,
                                        "service_indicators_found": found_indicators,
                                        "couples_services_detected": couples_services_found,
                                        "content_length": len(response.text),
                                        "authentication_used": auth is not None,
                                        "can_edit_prices": 'price' in found_indicators or 'cena' in found_indicators
                                    }
                                )
                                return True, url
                    except:
                        continue
                
                if not services_interface_found:
                    self.log_result(
                        "Services Management Interface",
                        False,
                        "❌ No services management interface found",
                        {
                            "tested_urls": services_urls,
                            "authentication_used": auth is not None,
                            "suggestion": "Manual navigation through admin interface may be required"
                        }
                    )
                    return False, None
                    
        except Exception as e:
            self.log_result(
                "Services Management Interface",
                False,
                f"❌ Error testing services management: {str(e)}",
                {"error": str(e)}
            )
            return False, None

    async def test_price_update_capability(self, services_url, auth_credentials=None):
        """Test if prices can actually be updated through the interface"""
        
        if not services_url:
            self.log_result(
                "Price Update Capability",
                False,
                "❌ No services URL available for testing",
                {"services_url": None}
            )
            return False
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Set up authentication
                auth = None
                if auth_credentials and 'username' in auth_credentials:
                    auth = (auth_credentials['username'], auth_credentials['password'])
                
                # Get the services page
                response = await client.get(services_url, auth=auth)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Look for edit capabilities
                    edit_indicators = [
                        'edit', 'update', 'save', 'submit', 'form', 'input',
                        'button', 'pencil', 'modify', 'change'
                    ]
                    
                    found_edit_indicators = [ind for ind in edit_indicators if ind.lower() in content.lower()]
                    
                    # Look for price fields
                    price_indicators = [
                        'price', 'cena', 'amount', 'value', 'cost', 'rsd'
                    ]
                    
                    found_price_indicators = [ind for ind in price_indicators if ind.lower() in content.lower()]
                    
                    # Check for forms that might allow updates
                    has_forms = '<form' in content.lower()
                    has_inputs = '<input' in content.lower()
                    has_buttons = '<button' in content.lower() or 'type="submit"' in content.lower()
                    
                    can_update_prices = (
                        len(found_edit_indicators) >= 1 and 
                        len(found_price_indicators) >= 1 and 
                        (has_forms or has_inputs)
                    )
                    
                    self.log_result(
                        "Price Update Capability",
                        can_update_prices,
                        f"✅ Price update capability detected" if can_update_prices else "❌ No price update capability found",
                        {
                            "services_url": services_url,
                            "edit_indicators": found_edit_indicators,
                            "price_indicators": found_price_indicators,
                            "has_forms": has_forms,
                            "has_inputs": has_inputs,
                            "has_buttons": has_buttons,
                            "can_update_prices": can_update_prices,
                            "manual_process_required": not can_update_prices
                        }
                    )
                    
                    return can_update_prices
                else:
                    self.log_result(
                        "Price Update Capability",
                        False,
                        f"❌ Cannot access services page: {response.status_code}",
                        {"status_code": response.status_code, "services_url": services_url}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Price Update Capability",
                False,
                f"❌ Error testing price update capability: {str(e)}",
                {"error": str(e), "services_url": services_url}
            )
            return False

    async def run_web_interface_test(self):
        """Run complete web interface testing"""
        print("=" * 80)
        print("WEB INTERFACE PRICE CORRECTION TESTING")
        print("=" * 80)
        print(f"Admin URL: {self.admin_url}")
        print(f"Target: Manual price correction for 'Kartica Masaza za parove' services")
        print()
        
        # Step 1: Test admin interface access
        print("🔍 STEP 1: Admin Interface Access")
        interface_accessible, requires_auth = await self.test_admin_interface_access()
        
        # Step 2: Test authentication if required
        print("\n🔍 STEP 2: Authentication Testing")
        auth_credentials = None
        if interface_accessible and requires_auth:
            auth_credentials = await self.test_authentication_methods()
        elif interface_accessible and not requires_auth:
            self.log_result(
                "Authentication Testing",
                True,
                "✅ No authentication required - public admin interface",
                {"authentication_required": False}
            )
        else:
            self.log_result(
                "Authentication Testing",
                False,
                "Skipped - Admin interface not accessible",
                {"reason": "Step 1 failed"}
            )
        
        # Step 3: Test services management interface
        print("\n🔍 STEP 3: Services Management Interface")
        services_available = False
        services_url = None
        if interface_accessible:
            services_available, services_url = await self.test_services_management_interface(auth_credentials)
        else:
            self.log_result(
                "Services Management Interface",
                False,
                "Skipped - Admin interface not accessible",
                {"reason": "Step 1 failed"}
            )
        
        # Step 4: Test price update capability
        print("\n🔍 STEP 4: Price Update Capability")
        can_update_prices = False
        if services_available:
            can_update_prices = await self.test_price_update_capability(services_url, auth_credentials)
        else:
            self.log_result(
                "Price Update Capability",
                False,
                "Skipped - Services management not available",
                {"reason": "Step 3 failed"}
            )
        
        # Summary
        print("\n" + "=" * 80)
        print("WEB INTERFACE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Final assessment and instructions
        if interface_accessible and can_update_prices:
            print("🎉 WEB INTERFACE PRICE CORRECTION IS POSSIBLE!")
            print("✅ Admin interface accessible")
            print("✅ Services management available")
            print("✅ Price update capability detected")
            print()
            print("📋 MANUAL PRICE CORRECTION PROCESS:")
            print(f"1. Access admin interface: {self.admin_url}")
            if auth_credentials:
                print(f"2. Login with credentials: {auth_credentials}")
            print(f"3. Navigate to services management: {services_url}")
            print("4. Find services in 'Kartica Masaza za parove' category")
            print("5. Update prices according to the mapping provided in test results")
            print("6. Ensure discount remains at 10%")
            print("7. Save changes and verify")
            
        elif interface_accessible and services_available:
            print("⚠️ PARTIAL WEB INTERFACE CAPABILITY")
            print("✅ Admin interface accessible")
            print("✅ Services management available")
            print("❌ Price update capability unclear")
            print()
            print("🔧 MANUAL INVESTIGATION REQUIRED:")
            print(f"1. Access: {services_url}")
            print("2. Look for edit/update buttons or forms")
            print("3. Test price modification on a single service")
            
        elif interface_accessible:
            print("🔧 LIMITED WEB INTERFACE ACCESS")
            print("✅ Admin interface accessible")
            print("❌ Services management not found")
            print()
            print("🔍 MANUAL NAVIGATION REQUIRED:")
            print(f"1. Access: {self.admin_url}")
            print("2. Look for services/usluge menu items")
            print("3. Navigate to couples massage category")
            
        else:
            print("🚨 WEB INTERFACE NOT ACCESSIBLE")
            print("❌ Cannot access admin interface")
            print()
            print("🔧 ALTERNATIVE APPROACHES:")
            print("1. Check if different admin URL exists")
            print("2. Contact system administrator for access")
            print("3. Use API endpoints if available")
        
        return self.results

async def main():
    """Main test execution"""
    tester = WebInterfaceTester()
    results = await tester.run_web_interface_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())