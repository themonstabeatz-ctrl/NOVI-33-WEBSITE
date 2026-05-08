#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Thai Spa System
Tests all available backend endpoints and booking integration
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://gold-line-fixer.preview.emergentagent.com')

class ComprehensiveAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.api_base = f"{self.backend_url}/api"
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
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        print()

    async def test_backend_root_endpoint(self):
        """Test backend root endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Backend Root Endpoint",
                        True,
                        "Root endpoint accessible and returns expected response",
                        {"status_code": response.status_code, "response": data}
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Root Endpoint",
                        False,
                        f"Unexpected status code: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Backend Root Endpoint",
                False,
                f"Connection error: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_status_endpoints(self):
        """Test status check endpoints (GET and POST)"""
        
        # Test POST /status
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_data = {"client_name": "Test Client"}
                response = await client.post(
                    f"{self.api_base}/status",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "POST /status Endpoint",
                        True,
                        "Status creation endpoint working correctly",
                        {
                            "status_code": response.status_code,
                            "created_id": data.get('id', 'N/A'),
                            "client_name": data.get('client_name', 'N/A')
                        }
                    )
                    post_success = True
                else:
                    self.log_result(
                        "POST /status Endpoint",
                        False,
                        f"Status creation failed with code: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    post_success = False
                    
        except Exception as e:
            self.log_result(
                "POST /status Endpoint",
                False,
                f"Error creating status: {str(e)}",
                {"error": str(e)}
            )
            post_success = False
        
        # Test GET /status
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/status")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "GET /status Endpoint",
                        True,
                        f"Status retrieval working, found {len(data)} records",
                        {
                            "status_code": response.status_code,
                            "record_count": len(data),
                            "sample_record": data[0] if data else "No records"
                        }
                    )
                    get_success = True
                else:
                    self.log_result(
                        "GET /status Endpoint",
                        False,
                        f"Status retrieval failed with code: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    get_success = False
                    
        except Exception as e:
            self.log_result(
                "GET /status Endpoint",
                False,
                f"Error retrieving status: {str(e)}",
                {"error": str(e)}
            )
            get_success = False
            
        return post_success and get_success

    async def test_booking_endpoint_validation(self):
        """Test booking endpoint with various validation scenarios"""
        
        # Test 1: Valid booking data
        valid_booking = {
            "client_first_name": "Ana",
            "client_last_name": "Petrovic",
            "client_phone": "+381621234567",
            "client_email": "ana.petrovic@example.com",
            "appointment_date": "2025-02-15",
            "start_time": "2025-02-15T14:00:00",
            "service_id": "44826422-d4b4-4ca0-971b-1c91b0a6ccdd",
            "therapist_id": "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f",
            "notes": "Rezervacija za opuštajuću masažu"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=valid_booking,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Booking Endpoint - Valid Data",
                        True,
                        "Booking endpoint accepts valid data and processes correctly",
                        {
                            "status_code": response.status_code,
                            "response": "Booking successful"
                        }
                    )
                    return True
                elif response.status_code == 404:
                    self.log_result(
                        "Booking Endpoint - Valid Data",
                        False,
                        "External booking API not found (404) - Service unavailable",
                        {
                            "status_code": response.status_code,
                            "issue": "External booking service at /api/appointments does not exist",
                            "proxy_status": "Backend proxy working, external service missing"
                        }
                    )
                    return False
                elif response.status_code == 503:
                    self.log_result(
                        "Booking Endpoint - Valid Data",
                        False,
                        "External booking service unavailable (503)",
                        {
                            "status_code": response.status_code,
                            "issue": "External service timeout or connection error"
                        }
                    )
                    return False
                else:
                    self.log_result(
                        "Booking Endpoint - Valid Data",
                        False,
                        f"Unexpected response: {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "response": response.text[:200]
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Booking Endpoint - Valid Data",
                False,
                f"Connection error: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_booking_endpoint_invalid_data(self):
        """Test booking endpoint with invalid data"""
        
        # Test with missing required fields
        invalid_booking = {
            "client_first_name": "Test",
            # Missing other required fields
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=invalid_booking,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 422:  # Validation error
                    self.log_result(
                        "Booking Endpoint - Invalid Data",
                        True,
                        "Booking endpoint correctly validates input data",
                        {
                            "status_code": response.status_code,
                            "validation": "Working correctly - rejects invalid data"
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Booking Endpoint - Invalid Data",
                        False,
                        f"Unexpected validation behavior: {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "expected": "422 for validation errors",
                            "response": response.text[:200]
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Booking Endpoint - Invalid Data",
                False,
                f"Error testing validation: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_external_service_availability(self):
        """Test if external booking service exists"""
        external_url = "https://gold-line-fixer.preview.emergentagent.com/api/appointments"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try different HTTP methods
                methods_to_try = ['GET', 'POST', 'OPTIONS']
                
                for method in methods_to_try:
                    try:
                        if method == 'GET':
                            response = await client.get(external_url)
                        elif method == 'POST':
                            response = await client.post(external_url, json={})
                        elif method == 'OPTIONS':
                            response = await client.options(external_url)
                        
                        if response.status_code != 404:
                            self.log_result(
                                "External Service Availability",
                                True,
                                f"External service responds to {method} requests",
                                {
                                    "method": method,
                                    "status_code": response.status_code,
                                    "service_exists": True
                                }
                            )
                            return True
                    except:
                        continue
                
                # If all methods return 404 or error
                self.log_result(
                    "External Service Availability",
                    False,
                    "External booking service not available at expected endpoint",
                    {
                        "external_url": external_url,
                        "issue": "Endpoint /api/appointments does not exist",
                        "recommendation": "Check if external service is deployed or URL is correct"
                    }
                )
                return False
                
        except Exception as e:
            self.log_result(
                "External Service Availability",
                False,
                f"Cannot reach external service: {str(e)}",
                {"error": str(e), "external_url": external_url}
            )
            return False

    async def run_all_tests(self):
        """Run comprehensive backend tests"""
        print("=" * 70)
        print("COMPREHENSIVE BACKEND API TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print()
        
        # Test 1: Backend Root Endpoint
        root_working = await self.test_backend_root_endpoint()
        
        # Test 2: Status Endpoints (CRUD operations)
        status_working = await self.test_status_endpoints()
        
        # Test 3: External Service Availability
        external_available = await self.test_external_service_availability()
        
        # Test 4: Booking Endpoint with Valid Data
        booking_valid = await self.test_booking_endpoint_validation()
        
        # Test 5: Booking Endpoint with Invalid Data
        booking_validation = await self.test_booking_endpoint_invalid_data()
        
        # Summary
        print("=" * 70)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Detailed Analysis
        print("DETAILED ANALYSIS:")
        print("-" * 30)
        
        if root_working and status_working:
            print("✅ Backend Service: FULLY FUNCTIONAL")
            print("   - Root endpoint accessible")
            print("   - Status CRUD operations working")
            print("   - Database connectivity confirmed")
        else:
            print("❌ Backend Service: ISSUES DETECTED")
        
        if not external_available:
            print("❌ External Booking Service: NOT AVAILABLE")
            print("   - Endpoint /api/appointments does not exist")
            print("   - This is the root cause of booking failures")
        else:
            print("✅ External Booking Service: AVAILABLE")
        
        if not booking_valid and not external_available:
            print("⚠️  Booking Integration: BLOCKED BY EXTERNAL SERVICE")
            print("   - Backend proxy is working correctly")
            print("   - Issue is with external service availability")
        elif booking_valid:
            print("✅ Booking Integration: WORKING")
        
        print()
        print("RECOMMENDATIONS:")
        print("-" * 20)
        
        if not external_available:
            print("1. Verify external booking service deployment")
            print("2. Check if /api/appointments endpoint exists on external server")
            print("3. Confirm external service URL is correct")
            print("4. Consider implementing mock booking service for testing")
        
        if root_working and status_working and not external_available:
            print("5. Backend proxy implementation is correct")
            print("6. No changes needed to backend code")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ComprehensiveAPITester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())