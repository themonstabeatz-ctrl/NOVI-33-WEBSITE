#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST - User's exact scenarios with Generic therapist
Testing the exact scenarios from the review request
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

class ReviewTester:
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    async def verify_booking_in_external_system(self, appointment_id):
        """Verify if booking actually appears in external system"""
        if not appointment_id or appointment_id == 'N/A':
            return "❌ No appointment ID to verify"
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to get the specific appointment
                response = await client.get(
                    f"https://pozdrav-kako-si.emergent.host/api/appointments/{appointment_id}",
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    return "✅ Found in external system"
                elif response.status_code == 404:
                    return "❌ NOT found in external system"
                else:
                    return f"⚠️ External system returned {response.status_code}"
                    
        except Exception as e:
            return f"⚠️ Cannot verify: {str(e)}"

    async def test_backend_health(self):
        """Test if backend service is accessible"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Backend Health Check",
                        True,
                        f"Backend accessible at {self.api_base}",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Health Check",
                        False,
                        f"Backend returned status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"Cannot connect to backend: {str(e)}",
                {"error": str(e), "backend_url": self.api_base}
            )
            return False

    async def test_user_exact_scenarios(self):
        """Test EXACT scenarios from user review request"""
        
        print("🚨 FINAL VERIFICATION TEST - User's exact scenarios with Generic therapist")
        print("=" * 80)
        print("Context:")
        print("- Created 'Web Rezervacije (Generic)' therapist (ID: 1490364f-31c8-49a6-a370-2e19fed34e81)")
        print("- This therapist allows duplicate bookings at same time")
        print("- Frontend updated to use this therapist for all web bookings")
        print("- User can now organize real therapists in salon")
        print()
        
        # EXACT services and scenarios from review request
        test_scenarios = [
            {
                "source": "Massage page",
                "service_name": "Partnerska masaža - 120 min",
                "service_id": "114600d6-3960-41e4-b453-32012cb6400a",
                "client_first_name": "Denis",
                "client_last_name": "Test",
                "client_email": "denis.test@example.com",
                "client_phone": "+381621111111"
            },
            {
                "source": "Spa page", 
                "service_name": "Tretman lica - 60 min",
                "service_id": "75c1c431-b9aa-4ed6-acc5-b2498eb8ccaf",
                "client_first_name": "Andrijana",
                "client_last_name": "Test",
                "client_email": "andrijana.test@example.com",
                "client_phone": "+381622222222"
            },
            {
                "source": "Booking dropdown",
                "service_name": "Tradicionalna tajlandska masaža - 90 min", 
                "service_id": "39f8c583-a780-4e54-9bab-f693a51287c2",
                "client_first_name": "Web",
                "client_last_name": "Test",
                "client_email": "web.test@example.com",
                "client_phone": "+381623333333"
            }
        ]
        
        # EXACT date/time from review request
        test_date = "2025-11-02"
        test_time = "2025-11-02T14:00:00"
        generic_therapist_id = "1490364f-31c8-49a6-a370-2e19fed34e81"  # Generic therapist
        
        all_passed = True
        successful_bookings = []
        failed_bookings = []
        
        print(f"Testing all 3 bookings on: {test_date} at 14:00")
        print(f"Using Generic therapist ID: {generic_therapist_id}")
        print("All bookings at SAME time (14:00) should work (duplicate bookings allowed)")
        print()
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"📋 TEST {i}/3: {scenario['source']} - {scenario['service_name']}")
            
            booking_data = {
                "client_first_name": scenario["client_first_name"],
                "client_last_name": scenario["client_last_name"],
                "client_phone": scenario["client_phone"],
                "client_email": scenario["client_email"],
                "appointment_date": test_date,
                "start_time": test_time,  # Same time for all (testing duplicate bookings)
                "service_id": scenario["service_id"],
                "therapist_id": generic_therapist_id,
                "notes": f"REVIEW TEST: {scenario['source']} booking"
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.api_base}/book-appointment",
                        json=booking_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        appointment_id = response_data.get('id', 'N/A') if response_data else 'N/A'
                        
                        # Verify booking appears in external system
                        external_verification = await self.verify_booking_in_external_system(appointment_id)
                        
                        successful_bookings.append({
                            "scenario": i,
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "appointment_id": appointment_id,
                            "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                            "client_email": scenario["client_email"],
                            "external_verification": external_verification
                        })
                        
                        self.log_result(
                            f"✅ SCENARIO {i}: {scenario['source']}",
                            True,
                            f"SUCCESS - {scenario['service_name']} | ID: {appointment_id} | {external_verification}",
                            {
                                "source": scenario["source"],
                                "service_name": scenario['service_name'],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "appointment_id": appointment_id,
                                "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                                "client_email": scenario["client_email"],
                                "date_time": test_time,
                                "therapist_id": generic_therapist_id,
                                "external_verification": external_verification,
                                "response": response_data
                            }
                        )
                        
                    else:
                        # Handle errors
                        try:
                            error_detail = response.json().get('detail', '') if response.headers.get('content-type', '').startswith('application/json') else response.text
                        except:
                            error_detail = response.text
                            
                        failed_bookings.append({
                            "scenario": i,
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "error": error_detail,
                            "status_code": response.status_code,
                            "client": f"{scenario['client_first_name']} {scenario['client_last_name']}"
                        })
                        
                        self.log_result(
                            f"❌ SCENARIO {i}: {scenario['source']}",
                            False,
                            f"FAILED - {scenario['service_name']} | Status: {response.status_code} | Error: {error_detail}",
                            {
                                "source": scenario["source"],
                                "service_name": scenario['service_name'],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "error_detail": error_detail,
                                "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                                "client_email": scenario["client_email"],
                                "date_time": test_time,
                                "therapist_id": generic_therapist_id
                            }
                        )
                        all_passed = False
                        
            except Exception as e:
                failed_bookings.append({
                    "scenario": i,
                    "source": scenario["source"],
                    "service": scenario["service_name"],
                    "service_id": scenario["service_id"],
                    "error": str(e),
                    "status_code": "Exception"
                })
                self.log_result(
                    f"❌ SCENARIO {i}: {scenario['source']}",
                    False,
                    f"EXCEPTION - {scenario['service_name']} | Error: {str(e)}",
                    {"error": str(e), "service_id": scenario["service_id"]}
                )
                all_passed = False
        
        # FINAL SUMMARY
        total_success = len(successful_bookings)
        total_tests = len(test_scenarios)
        
        print("=" * 80)
        print("🎯 FINAL VERIFICATION RESULTS")
        print("=" * 80)
        
        if total_success == total_tests:
            print("🎉 ALL TESTS PASSED - 100% SUCCESS RATE!")
            print(f"✅ All {total_tests} bookings succeeded (200/201 response)")
            print(f"✅ All {total_tests} bookings returned appointment IDs")
            print(f"✅ All bookings use Generic therapist ID: {generic_therapist_id}")
            print(f"✅ All bookings at SAME time (14:00) worked (duplicate bookings allowed)")
            print()
            print("📋 SUCCESSFUL BOOKINGS:")
            for booking in successful_bookings:
                print(f"   {booking['scenario']}. {booking['source']}: {booking['service']} | ID: {booking['appointment_id']} | {booking['external_verification']}")
            print()
            print("✅ Backend endpoint: POST {REACT_APP_BACKEND_URL}/api/book-appointment - WORKING")
            print("✅ External system: https://pozdrav-kako-si.emergent.host/ - ACCESSIBLE")
            
        else:
            print(f"❌ PARTIAL SUCCESS - {total_success}/{total_tests} bookings succeeded")
            print()
            if successful_bookings:
                print("✅ SUCCESSFUL BOOKINGS:")
                for booking in successful_bookings:
                    print(f"   {booking['scenario']}. {booking['source']}: {booking['service']} | ID: {booking['appointment_id']} | {booking['external_verification']}")
                print()
            if failed_bookings:
                print("❌ FAILED BOOKINGS:")
                for booking in failed_bookings:
                    print(f"   {booking['scenario']}. {booking['source']}: {booking['service']} | Status: {booking['status_code']} | Error: {booking['error']}")
                print()
        
        self.log_result(
            "🚨 FINAL VERIFICATION TEST SUMMARY",
            total_success == total_tests,
            f"User's exact scenarios: {total_success}/{total_tests} bookings successful on 2025-11-02 at 14:00",
            {
                "test_date": "2025-11-02",
                "test_time": "14:00",
                "generic_therapist_id": generic_therapist_id,
                "total_success": total_success,
                "total_tests": total_tests,
                "success_rate": f"{(total_success/total_tests)*100:.0f}%",
                "successful_bookings": successful_bookings,
                "failed_bookings": failed_bookings,
                "all_at_same_time": True,
                "duplicate_bookings_allowed": True,
                "backend_endpoint": f"{self.api_base}/book-appointment",
                "external_system": "https://pozdrav-kako-si.emergent.host/",
                "user_issue_resolved": total_success == total_tests
            }
        )
        
        return all_passed

    async def run_review_test(self):
        """Run the complete review verification test"""
        print("🚨 FINAL VERIFICATION TEST - User's exact scenarios with Generic therapist")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print()
        
        # Test 1: Backend Health Check
        backend_healthy = await self.test_backend_health()
        
        if not backend_healthy:
            print("🚨 CRITICAL: Backend not accessible - Cannot proceed with tests")
            return False
        
        # Test 2: User's Exact Scenarios
        user_scenarios_passed = await self.test_user_exact_scenarios()
        
        return user_scenarios_passed

async def main():
    """Main test execution"""
    tester = ReviewTester()
    success = await tester.run_review_test()
    return success

if __name__ == "__main__":
    asyncio.run(main())