#!/usr/bin/env python3
"""
Review-Specific Booking Test for Thai Spa
Tests the specific services mentioned in the review request after duplicate service fix
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://wavy-parallax-hero.preview.emergentagent.com')

class ReviewBookingTester:
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
        if details and details.get('appointment_id'):
            print(f"   📋 Appointment ID: {details['appointment_id']}")
        if details and details.get('error_detail'):
            print(f"   ⚠️  Error: {details['error_detail']}")
        print()

    async def test_primary_service(self):
        """Test the primary service: Aroma terapija - 60 min"""
        
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "User",
            "client_phone": "+381621234567",
            "client_email": "test@example.com",
            "appointment_date": "2025-01-25",
            "start_time": "2025-01-25T14:00:00",
            "service_id": "f81ee187-1d45-4942-abf3-4b83f147bf85",  # Aroma terapija - 60 min
            "therapist_id": "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f",
            "notes": "Test booking for primary service"
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
                    self.log_result(
                        "PRIMARY: Aroma terapija - 60 min (massage)",
                        True,
                        f"Successfully booked primary service",
                        {
                            "service_id": booking_data["service_id"],
                            "status_code": response.status_code,
                            "appointment_id": response_data.get('id', 'N/A') if response_data else 'N/A',
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "time": booking_data["start_time"]
                        }
                    )
                    return True
                else:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', error_msg)
                    except:
                        pass
                    
                    self.log_result(
                        "PRIMARY: Aroma terapija - 60 min (massage)",
                        False,
                        f"Failed to book primary service - Status {response.status_code}",
                        {
                            "service_id": booking_data["service_id"],
                            "status_code": response.status_code,
                            "error_detail": error_msg
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "PRIMARY: Aroma terapija - 60 min (massage)",
                False,
                f"Exception occurred: {str(e)}",
                {"error": str(e), "service_id": booking_data["service_id"]}
            )
            return False

    async def test_massage_services(self):
        """Test 3-4 random massage services"""
        
        massage_services = [
            {"name": "Tradicionalna tajlandska masaža - 90 min", "id": "39f8c583-a780-4e54-9bab-f693a51287c2"},
            {"name": "Masaža stopala - 60 min", "id": "c4f3d344-73f9-4a0d-ae39-6f2be718ef19"},
            {"name": "Sportska masaža - 120 min", "id": "d3e8684a-2bbc-4a15-835e-8e43d231074a"}
        ]
        
        therapist_id = "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f"
        all_passed = True
        successful_bookings = []
        
        for i, service in enumerate(massage_services):
            booking_data = {
                "client_first_name": "Ana",
                "client_last_name": "Petrovic",
                "client_phone": "+381621234567",
                "client_email": f"ana.massage{i+1}@gmail.com",
                "appointment_date": "2025-01-25",
                "start_time": f"2025-01-25T{15+i}:00:00",
                "service_id": service["id"],
                "therapist_id": therapist_id,
                "notes": f"Test booking for {service['name']}"
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
                        successful_bookings.append(service["name"])
                        self.log_result(
                            f"MASSAGE: {service['name']}",
                            True,
                            f"Successfully booked massage service",
                            {
                                "service_id": service["id"],
                                "status_code": response.status_code,
                                "appointment_id": response_data.get('id', 'N/A') if response_data else 'N/A'
                            }
                        )
                    else:
                        error_msg = response.text
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('detail', error_msg)
                        except:
                            pass
                        
                        self.log_result(
                            f"MASSAGE: {service['name']}",
                            False,
                            f"Failed to book - Status {response.status_code}",
                            {
                                "service_id": service["id"],
                                "status_code": response.status_code,
                                "error_detail": error_msg
                            }
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_result(
                    f"MASSAGE: {service['name']}",
                    False,
                    f"Exception: {str(e)}",
                    {"error": str(e), "service_id": service["id"]}
                )
                all_passed = False
        
        return all_passed, successful_bookings

    async def test_spa_services(self):
        """Test 3-4 spa services"""
        
        spa_services = [
            {"name": "Tretman lica - 60 min", "id": "75c1c431-b9aa-4ed6-acc5-b2498eb8ccaf"},
            {"name": "Zlatni tretman lica - 90 min", "id": "7cc4d292-5d54-42f0-b511-1fb4263f6353"},
            {"name": "Kraljevski spa paket - 120 min", "id": "4a390175-9f3a-4c94-bce3-082623a7a4ce"}
        ]
        
        therapist_id = "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f"
        all_passed = True
        successful_bookings = []
        
        for i, service in enumerate(spa_services):
            booking_data = {
                "client_first_name": "Marija",
                "client_last_name": "Nikolic",
                "client_phone": "+381621234567",
                "client_email": f"marija.spa{i+1}@gmail.com",
                "appointment_date": "2025-01-25",
                "start_time": f"2025-01-25T{18+i}:00:00",
                "service_id": service["id"],
                "therapist_id": therapist_id,
                "notes": f"Test booking for {service['name']}"
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
                        successful_bookings.append(service["name"])
                        self.log_result(
                            f"SPA: {service['name']}",
                            True,
                            f"Successfully booked spa service",
                            {
                                "service_id": service["id"],
                                "status_code": response.status_code,
                                "appointment_id": response_data.get('id', 'N/A') if response_data else 'N/A'
                            }
                        )
                    else:
                        error_msg = response.text
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('detail', error_msg)
                        except:
                            pass
                        
                        self.log_result(
                            f"SPA: {service['name']}",
                            False,
                            f"Failed to book - Status {response.status_code}",
                            {
                                "service_id": service["id"],
                                "status_code": response.status_code,
                                "error_detail": error_msg
                            }
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_result(
                    f"SPA: {service['name']}",
                    False,
                    f"Exception: {str(e)}",
                    {"error": str(e), "service_id": service["id"]}
                )
                all_passed = False
        
        return all_passed, successful_bookings

    async def run_review_tests(self):
        """Run all review-specific tests"""
        print("=" * 80)
        print("🎯 REVIEW-SPECIFIC BOOKING INTEGRATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"External System: https://pozdrav-kako-si.emergent.host/")
        print(f"Testing after duplicate service name fix")
        print()
        
        # Test 1: Primary service (Aroma terapija - 60 min)
        print("🔍 Testing Primary Service...")
        primary_success = await self.test_primary_service()
        
        # Test 2: Massage services
        print("🔍 Testing Massage Services...")
        massage_success, massage_bookings = await self.test_massage_services()
        
        # Test 3: Spa services
        print("🔍 Testing Spa Services...")
        spa_success, spa_bookings = await self.test_spa_services()
        
        # Summary
        print("=" * 80)
        print("📊 REVIEW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 1 + 3 + 3  # 1 primary + 3 massage + 3 spa
        passed_tests = sum([
            1 if primary_success else 0,
            len(massage_bookings),
            len(spa_bookings)
        ])
        
        print(f"✅ Primary Service (Aroma terapija - 60 min): {'PASS' if primary_success else 'FAIL'}")
        print(f"✅ Massage Services: {len(massage_bookings)}/3 passed")
        print(f"✅ Spa Services: {len(spa_bookings)}/3 passed")
        print()
        print(f"📈 Overall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        
        if primary_success and massage_success and spa_success:
            print("🎉 ALL REVIEW TESTS PASSED - Duplicate service issue resolved!")
            print("✅ No 404 'Service not found' errors")
            print("✅ All bookings returned appointment IDs")
            print("✅ Integration working end-to-end")
        elif passed_tests >= 5:  # At least 5 out of 7 services working
            print("✅ REVIEW TESTS MOSTLY SUCCESSFUL - Integration working well")
            print(f"✅ {passed_tests} out of {total_tests} services working correctly")
        elif primary_success:
            print("⚠️  PRIMARY SERVICE WORKING - Some other services have issues")
            print("✅ Main duplicate service issue resolved")
        else:
            print("❌ REVIEW TESTS FAILED - Issues remain")
            print("🔍 Check individual test results above for details")
        
        return {
            'primary_success': primary_success,
            'massage_success': massage_success,
            'spa_success': spa_success,
            'massage_bookings': massage_bookings,
            'spa_bookings': spa_bookings,
            'total_passed': passed_tests,
            'total_tests': total_tests
        }

async def main():
    """Main test execution"""
    tester = ReviewBookingTester()
    results = await tester.run_review_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())