#!/usr/bin/env python3
"""
Backend Testing for Couples Massage Booking Review Request
Tests the specific endpoints mentioned in the review request:
1. Health Check: GET /api/health
2. Services Endpoint: GET /api/services (looking for "Kartica Masaza za parove" category)
3. Couples Massage Booking: POST /api/book-couple-appointment
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from backend
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Use frontend URL for testing (as specified in review request)
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://wavy-parallax-hero.preview.emergentagent.com')
BOOKING_API_URL = os.getenv('BOOKING_API_URL', 'https://spabooking.emergent.host')

class ReviewRequestTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.api_base = f"{self.backend_url}/api"
        self.booking_api_url = BOOKING_API_URL
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2, default=str)}")
        print()

    async def test_health_check(self):
        """Test 1: Health Check - GET /api/health should return 200 OK"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Health Check",
                        True,
                        "GET /api/health returns 200 OK - Backend is running correctly",
                        {
                            "status_code": response.status_code,
                            "response": data,
                            "backend_url": self.backend_url
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Health Check",
                        False,
                        f"GET /api/health returned status {response.status_code} (expected 200)",
                        {
                            "status_code": response.status_code,
                            "response": response.text,
                            "backend_url": self.backend_url
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Health Check",
                False,
                f"Cannot connect to /api/health: {str(e)}",
                {
                    "error": str(e),
                    "endpoint": f"{self.api_base}/health",
                    "backend_url": self.backend_url
                }
            )
            return False

    async def test_services_endpoint(self):
        """Test 2: Services Endpoint - GET /api/services should return services from "Kartica Masaza za parove" category with discount_percentage field"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.api_base}/services")
                
                if response.status_code == 200:
                    services = response.json()
                    
                    # Check if it's a list of services
                    if not isinstance(services, list):
                        self.log_result(
                            "Services Endpoint",
                            False,
                            f"Services endpoint returned non-list: {type(services)}",
                            {
                                "response_type": type(services).__name__,
                                "response": str(services)[:200]
                            }
                        )
                        return False
                    
                    # Look for "Kartica Masaza za parove" category services
                    kartica_services = []
                    services_with_discount = []
                    
                    for service in services:
                        service_name = service.get('name', '')
                        service_category = service.get('category', '')
                        
                        # Check for couples massage services (various ways they might be named)
                        if any(keyword in service_name.lower() for keyword in ['parovi', 'couple', 'masaža za parove']):
                            kartica_services.append(service)
                        
                        # Check for discount_percentage field
                        if 'discount_percentage' in service:
                            services_with_discount.append(service)
                    
                    # Check if we found the expected services
                    found_kartica_services = len(kartica_services) > 0
                    found_discount_field = len(services_with_discount) > 0
                    
                    self.log_result(
                        "Services Endpoint",
                        found_kartica_services and found_discount_field,
                        f"GET /api/services returns {len(services)} services. Found {len(kartica_services)} couples massage services and {len(services_with_discount)} services with discount_percentage field",
                        {
                            "total_services": len(services),
                            "kartica_services_count": len(kartica_services),
                            "kartica_services": [s.get('name', 'Unknown') for s in kartica_services[:5]],
                            "services_with_discount_count": len(services_with_discount),
                            "sample_service": services[0] if services else None,
                            "booking_system_url": self.booking_api_url,
                            "found_kartica_services": found_kartica_services,
                            "found_discount_field": found_discount_field
                        }
                    )
                    return found_kartica_services and found_discount_field
                else:
                    self.log_result(
                        "Services Endpoint",
                        False,
                        f"GET /api/services returned status {response.status_code} (expected 200)",
                        {
                            "status_code": response.status_code,
                            "response": response.text[:200],
                            "backend_url": self.backend_url
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Services Endpoint",
                False,
                f"Cannot connect to /api/services: {str(e)}",
                {
                    "error": str(e),
                    "endpoint": f"{self.api_base}/services",
                    "backend_url": self.backend_url
                }
            )
            return False

    async def test_couples_massage_booking(self):
        """Test 3: Couples Massage Booking - POST /api/book-couple-appointment with realistic data"""
        
        # First get services to find a couples massage service
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                services_response = await client.get(f"{self.api_base}/services")
                
                if services_response.status_code != 200:
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        f"Cannot get services list: {services_response.status_code}",
                        {"status_code": services_response.status_code}
                    )
                    return False
                
                services = services_response.json()
                
                # Find couples massage services
                couples_services = []
                for service in services:
                    service_name = service.get('name', '')
                    if any(keyword in service_name.lower() for keyword in ['parovi', 'couple', 'masaža za parove']):
                        couples_services.append(service)
                
                if not couples_services:
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        "No couples massage services found for booking test",
                        {
                            "total_services": len(services),
                            "couples_services": 0,
                            "searched_keywords": ['parovi', 'couple', 'masaža za parove']
                        }
                    )
                    return False
                
                # Use first couples service found
                test_service = couples_services[0]
                
                # Calculate tomorrow's date at 14:00 (as specified in review request)
                tomorrow = datetime.now() + timedelta(days=1)
                appointment_date = tomorrow.strftime('%Y-%m-%d')
                start_time = f"{appointment_date}T14:00:00"
                
                # Prepare realistic couples booking data (as specified in review request)
                couple_booking_data = {
                    "client_first_name": "Test",
                    "client_last_name": "User",
                    "client_phone": "+381601234567",
                    "client_email": "test@example.com",
                    "start_time": start_time,
                    "duration_type": 120,  # 120 minutes per person (as mentioned in review)
                    "person1_services": [test_service.get('id')],
                    "person2_services": [test_service.get('id')],
                    "discount_couples_massage": 15.0,  # 15% discount
                    "language": "sr"  # Serbian language as specified
                }
                
                response = await client.post(
                    f"{self.api_base}/book-couple-appointment",
                    json=couple_booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    
                    # Verify booking was created successfully
                    self.log_result(
                        "Couples Massage Booking",
                        True,
                        f"POST /api/book-couple-appointment successful - Appointment ID: {appointment_id}",
                        {
                            "service_name": test_service.get('name'),
                            "service_id": test_service.get('id'),
                            "appointment_id": appointment_id,
                            "client": "Test User (+381601234567, test@example.com)",
                            "date_time": start_time,
                            "duration_per_person": "120 minutes",
                            "language": "Serbian (sr)",
                            "status_code": response.status_code,
                            "response": response_data,
                            "booking_api_url": self.booking_api_url
                        }
                    )
                    return True
                else:
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', error_detail)
                    except:
                        pass
                    
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        f"POST /api/book-couple-appointment failed - {response.status_code}: {error_detail}",
                        {
                            "service_name": test_service.get('name'),
                            "service_id": test_service.get('id'),
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": "Test User (+381601234567, test@example.com)",
                            "date_time": start_time,
                            "duration_per_person": "120 minutes",
                            "language": "Serbian (sr)"
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Couples Massage Booking",
                False,
                f"Exception during couples massage booking test: {str(e)}",
                {
                    "error": str(e),
                    "endpoint": f"{self.api_base}/book-couple-appointment"
                }
            )
            return False

    async def run_review_tests(self):
        """Run all tests specified in the review request"""
        print("=" * 80)
        print("COUPLES MASSAGE BOOKING REVIEW REQUEST TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print(f"Booking System: {self.booking_api_url}")
        print()
        print("Testing the following endpoints as specified in review request:")
        print("1. Health Check: GET /api/health - should return 200 OK")
        print("2. Services Endpoint: GET /api/services - should return services from 'Kartica Masaza za parove' category with discount_percentage field")
        print("3. Couples Massage Booking: POST /api/book-couple-appointment - with realistic data (Test User, +381601234567, test@example.com, tomorrow at 14:00, Serbian language)")
        print()
        
        # Test 1: Health Check
        print("🔍 TEST 1: Health Check")
        health_working = await self.test_health_check()
        
        # Test 2: Services Endpoint
        print("🔍 TEST 2: Services Endpoint")
        services_working = False
        if health_working:
            services_working = await self.test_services_endpoint()
        else:
            self.log_result(
                "Services Endpoint",
                False,
                "Skipped - Health check failed",
                {"reason": "Backend health check failed"}
            )
        
        # Test 3: Couples Massage Booking
        print("🔍 TEST 3: Couples Massage Booking")
        couples_booking_working = False
        if health_working and services_working:
            couples_booking_working = await self.test_couples_massage_booking()
        else:
            self.log_result(
                "Couples Massage Booking",
                False,
                "Skipped - Prerequisites failed",
                {
                    "health_working": health_working,
                    "services_working": services_working
                }
            )
        
        # Summary
        print("\n" + "=" * 80)
        print("REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            print(f"   {result['message']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Review Request Assessment
        if health_working and services_working and couples_booking_working:
            print("🎉 ALL REVIEW REQUEST OBJECTIVES ACHIEVED!")
            print("✅ Health Check: GET /api/health returns 200 OK")
            print("✅ Services Endpoint: Returns services from 'Kartica Masaza za parove' category with discount_percentage field")
            print("✅ Couples Massage Booking: POST /api/book-couple-appointment works with realistic data")
            print()
            print("🏆 CONCLUSION: Backend is solid and ready for frontend testing")
        elif health_working and services_working:
            print("⚠️ PARTIAL SUCCESS - Basic endpoints working but couples booking failed")
            print("✅ Health Check: Working")
            print("✅ Services Endpoint: Working")
            print("❌ Couples Massage Booking: Failed")
            print()
            print("🔧 ISSUE: Couples massage booking endpoint needs investigation")
        elif health_working:
            print("🚨 CRITICAL ISSUES FOUND")
            print("✅ Health Check: Backend accessible")
            print("❌ Services Endpoint: Cannot fetch services or missing required data")
            print("❌ Couples Booking: Skipped due to services endpoint failure")
            print()
            print("🔧 ISSUE: Services endpoint integration broken")
        else:
            print("🚨 BACKEND SERVICE NOT ACCESSIBLE")
            print("❌ Health Check: Backend not responding")
            print("❌ All other tests: Skipped")
            print()
            print("🔧 ISSUE: Backend service needs to be started/fixed")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ReviewRequestTester()
    results = await tester.run_review_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())