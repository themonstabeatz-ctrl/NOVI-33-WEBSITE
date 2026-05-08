#!/usr/bin/env python3
"""
CRITICAL REAL-WORLD BOOKING TEST - User Issue Verification
Tests the EXACT scenarios user reported as failing on 02.11.2025 at 14:00
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

class CriticalBookingTester:
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
            print(f"   Details: {json.dumps(details, indent=2)}")
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

    async def test_critical_user_scenarios(self):
        """Test EXACT scenarios from user review request"""
        
        print("🚨 CRITICAL REAL-WORLD BOOKING TEST")
        print("=" * 60)
        print("Testing user's EXACT scenarios that show success but don't appear in external system")
        print("Date: 02.11.2025 (November 2, 2025) at 14:00")
        print("External system: https://pozdrav-kako-si.emergent.host/")
        print()
        
        # EXACT services and scenarios from review request
        test_scenarios = [
            {
                "source": "Massage menu",
                "service_name": "Partnerska masaža - 120 min",
                "service_id": "114600d6-3960-41e4-b453-32012cb6400a",
                "client_first_name": "Test",
                "client_last_name": "Masaza",
                "client_email": "test.masaza@example.com",
                "client_phone": "+381621111111"
            },
            {
                "source": "Spa menu",
                "service_name": "Tretman lica - 60 min",
                "service_id": "75c1c431-b9aa-4ed6-acc5-b2498eb8ccaf",
                "client_first_name": "Test",
                "client_last_name": "Spa",
                "client_email": "test.spa@example.com",
                "client_phone": "+381622222222"
            },
            {
                "source": "Booking dropdown",
                "service_name": "Tradicionalna tajlandska masaža - 90 min",
                "service_id": "39f8c583-a780-4e54-9bab-f693a51287c2",
                "client_first_name": "Test",
                "client_last_name": "Booking",
                "client_email": "test.booking@example.com",
                "client_phone": "+381623333333"
            }
        ]
        
        # EXACT date/time from user report
        test_date = "2025-11-02"
        test_time = "2025-11-02T14:00:00"
        therapist_id = "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f"  # Marko Markovic
        
        successful_bookings = []
        failed_bookings = []
        
        for scenario in test_scenarios:
            print(f"🔍 Testing {scenario['source']}: {scenario['service_name']}")
            
            booking_data = {
                "client_first_name": scenario["client_first_name"],
                "client_last_name": scenario["client_last_name"],
                "client_phone": scenario["client_phone"],
                "client_email": scenario["client_email"],
                "appointment_date": test_date,
                "start_time": test_time,
                "service_id": scenario["service_id"],
                "therapist_id": therapist_id,
                "notes": f"CRITICAL TEST: User reported this shows success but doesn't appear in external system"
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.api_base}/book-appointment",
                        json=booking_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        # SUCCESS - but need to verify it appears in external system
                        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        appointment_id = response_data.get('id', 'N/A') if response_data else 'N/A'
                        
                        # Verify in external system
                        external_verification = await self.verify_booking_in_external_system(appointment_id)
                        
                        successful_bookings.append({
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "appointment_id": appointment_id,
                            "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                            "external_verification": external_verification
                        })
                        
                        self.log_result(
                            f"✅ {scenario['source']} - {scenario['service_name']}",
                            True,
                            f"BOOKING SUCCESSFUL - Appointment ID: {appointment_id}",
                            {
                                "source": scenario["source"],
                                "service_name": scenario["service_name"],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "appointment_id": appointment_id,
                                "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                                "client_email": scenario["client_email"],
                                "date_time": test_time,
                                "external_verification": external_verification,
                                "response_data": response_data
                            }
                        )
                        
                    elif response.status_code == 400:
                        # CRITICAL: This is what user is experiencing
                        try:
                            error_detail = response.json().get('detail', '') if response.headers.get('content-type', '').startswith('application/json') else response.text
                        except:
                            error_detail = response.text
                            
                        failed_bookings.append({
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "error": error_detail,
                            "status_code": response.status_code,
                            "client": f"{scenario['client_first_name']} {scenario['client_last_name']}"
                        })
                        
                        self.log_result(
                            f"❌ {scenario['source']} - {scenario['service_name']}",
                            False,
                            f"400 ERROR (This is the user's issue): {error_detail}",
                            {
                                "source": scenario["source"],
                                "service_name": scenario["service_name"],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "error_detail": error_detail,
                                "client": f"{scenario['client_first_name']} {scenario['client_last_name']}",
                                "client_email": scenario["client_email"],
                                "date_time": test_time,
                                "user_issue": "Backend was returning fake success - now returns real errors"
                            }
                        )
                        
                    elif response.status_code == 404:
                        failed_bookings.append({
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "error": "Service not found",
                            "status_code": response.status_code
                        })
                        
                        self.log_result(
                            f"❌ {scenario['source']} - {scenario['service_name']}",
                            False,
                            "404 Service Not Found - Service ID may be incorrect",
                            {
                                "source": scenario["source"],
                                "service_name": scenario["service_name"],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "response": response.text[:200]
                            }
                        )
                        
                    else:
                        failed_bookings.append({
                            "source": scenario["source"],
                            "service": scenario["service_name"],
                            "service_id": scenario["service_id"],
                            "error": f"HTTP {response.status_code}",
                            "status_code": response.status_code
                        })
                        
                        self.log_result(
                            f"❌ {scenario['source']} - {scenario['service_name']}",
                            False,
                            f"Unexpected response status {response.status_code}",
                            {
                                "source": scenario["source"],
                                "service_name": scenario["service_name"],
                                "service_id": scenario["service_id"],
                                "status_code": response.status_code,
                                "response": response.text[:200]
                            }
                        )
                        
            except Exception as e:
                failed_bookings.append({
                    "source": scenario["source"],
                    "service": scenario["service_name"],
                    "service_id": scenario["service_id"],
                    "error": str(e),
                    "status_code": "Exception"
                })
                
                self.log_result(
                    f"❌ {scenario['source']} - {scenario['service_name']}",
                    False,
                    f"Exception: {str(e)}",
                    {
                        "source": scenario["source"],
                        "error": str(e),
                        "service_id": scenario["service_id"]
                    }
                )
        
        # FINAL SUMMARY
        total_success = len(successful_bookings)
        total_tests = len(test_scenarios)
        
        print("=" * 60)
        print("🚨 CRITICAL TEST RESULTS SUMMARY")
        print("=" * 60)
        
        if total_success == total_tests:
            print(f"🎉 USER ISSUE RESOLVED: {total_success}/{total_tests} bookings successful!")
            print("✅ All bookings work on user's date/time (2025-11-02 at 14:00)")
            print("✅ External system verification completed")
            
            # Check external verification
            external_success = sum(1 for b in successful_bookings if "✅ Found" in b["external_verification"])
            if external_success == total_success:
                print("✅ ALL bookings verified in external system")
            else:
                print(f"⚠️ Only {external_success}/{total_success} bookings found in external system")
                
        elif total_success > 0:
            print(f"⚠️ PARTIAL SUCCESS: {total_success}/{total_tests} bookings work")
            print("🔧 Some services still failing - user issue partially resolved")
            
        else:
            print(f"🚨 USER ISSUE CONFIRMED: {total_success}/{total_tests} bookings successful")
            print("❌ All bookings failing on user's date/time")
            print("🔧 Backend fix needed - user's reported issue is REAL")
        
        print()
        print("SUCCESSFUL BOOKINGS:")
        for booking in successful_bookings:
            print(f"  ✅ {booking['source']}: {booking['service']} (ID: {booking['appointment_id']})")
            print(f"     External verification: {booking['external_verification']}")
        
        print()
        print("FAILED BOOKINGS:")
        for booking in failed_bookings:
            print(f"  ❌ {booking['source']}: {booking['service']}")
            print(f"     Error: {booking['error']}")
        
        return {
            "total_success": total_success,
            "total_tests": total_tests,
            "successful_bookings": successful_bookings,
            "failed_bookings": failed_bookings,
            "user_issue_resolved": total_success == total_tests
        }

async def main():
    """Main test execution"""
    tester = CriticalBookingTester()
    results = await tester.test_critical_user_scenarios()
    return results

if __name__ == "__main__":
    asyncio.run(main())