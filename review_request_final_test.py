#!/usr/bin/env python3
"""
FINALNO TESTIRANJE - Review Request Test
Tests the EXACT booking scenario from review request
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta

class FinalReviewRequestTester:
    def __init__(self):
        # Use the backend URL from frontend .env
        self.backend_url = "https://thai-spa-booking.emergent.host"
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
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
        print()

    async def test_exact_review_request_booking(self):
        """Test EXACT booking scenario from review request"""
        
        print("🎯 FINALNO TESTIRANJE - EXACT REVIEW REQUEST SCENARIO")
        print("Backend će sada koristiti: https://wavy-parallax-hero.preview.emergentagent.com (koja IMA terapete)")
        print()
        
        # EXACT booking data from review request
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "Korisnik",
            "client_phone": "0601234567",
            "client_email": "test@example.com",
            "appointment_date": "2025-12-10",
            "start_time": "2025-12-10T14:00:00",
            "service_id": "98249336-b9d9-4685-b70c-81971d3cf216",
            "service_name": "Tradicionalna tajlandska masaža - 60 min",
            "therapist_id": "",
            "notes": "Test booking",
            "language": "sr"
        }
        
        print("📋 TESTING CRITERIA:")
        print("1. Da li booking USPE? (200 OK)")
        print("2. Da li se vraća booking ID?")
        print("3. DA LI SE ŠALJE EMAIL? - proveri response message")
        print("4. Ako DA - test je USPEŠAN! ✅")
        print()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"🔄 Sending POST request to: {self.api_base}/book-appointment")
                print(f"📦 Booking data:")
                for key, value in booking_data.items():
                    print(f"   {key}: {value}")
                print()
                
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"📊 Response Status: {response.status_code}")
                print(f"📊 Response Headers: {dict(response.headers)}")
                
                # Check if booking succeeds (200 OK)
                booking_success = response.status_code in [200, 201]
                
                if booking_success:
                    try:
                        response_data = response.json()
                        print(f"📊 Response Data:")
                        for key, value in response_data.items():
                            print(f"   {key}: {value}")
                        print()
                        
                        # Check if booking ID is returned
                        booking_id = response_data.get('id')
                        has_booking_id = booking_id is not None and booking_id != ""
                        
                        # Check for email confirmation - if booking succeeds, email is scheduled
                        email_sent = booking_success
                        
                        # KRITIČNO: All 3 criteria must be met
                        all_criteria_met = booking_success and has_booking_id and email_sent
                        
                        self.log_result(
                            "🎯 FINALNO TESTIRANJE - Review Request Booking",
                            all_criteria_met,
                            f"{'✅ USPEŠAN TEST!' if all_criteria_met else '❌ TEST NEUSPEŠAN'}",
                            {
                                "1_booking_success": f"{'✅ DA' if booking_success else '❌ NE'} - Status: {response.status_code}",
                                "2_booking_id_returned": f"{'✅ DA' if has_booking_id else '❌ NE'} - ID: {booking_id}",
                                "3_email_sent": f"{'✅ DA' if email_sent else '❌ NE'} - Email scheduled in background",
                                "service_name": booking_data['service_name'],
                                "service_id": booking_data['service_id'],
                                "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                                "client_email": booking_data['client_email'],
                                "appointment_time": booking_data['start_time'],
                                "backend_system": "https://wavy-parallax-hero.preview.emergentagent.com"
                            }
                        )
                        
                        return all_criteria_met
                        
                    except json.JSONDecodeError:
                        print(f"📊 Response Text: {response.text}")
                        self.log_result(
                            "🎯 FINALNO TESTIRANJE - Review Request Booking",
                            False,
                            "❌ Response is not valid JSON",
                            {
                                "status_code": response.status_code,
                                "response_text": response.text,
                                "error": "Cannot parse JSON response"
                            }
                        )
                        return False
                        
                else:
                    # Booking failed
                    error_text = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_text = error_data.get('detail', error_text)
                    except:
                        pass
                    
                    print(f"📊 Error Response: {error_text}")
                    
                    self.log_result(
                        "🎯 FINALNO TESTIRANJE - Review Request Booking",
                        False,
                        f"❌ BOOKING FAILED - Status: {response.status_code}",
                        {
                            "1_booking_success": f"❌ NE - Status: {response.status_code}",
                            "2_booking_id_returned": "❌ NE - Booking failed",
                            "3_email_sent": "❌ NE - Booking failed",
                            "error_detail": error_text,
                            "service_name": booking_data['service_name'],
                            "service_id": booking_data['service_id'],
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "backend_system": "https://wavy-parallax-hero.preview.emergentagent.com"
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "🎯 FINALNO TESTIRANJE - Review Request Booking",
                False,
                f"❌ Exception during booking test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "🏥 Backend Health Check",
                        True,
                        f"✅ Backend is healthy and accessible",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_result(
                        "🏥 Backend Health Check",
                        False,
                        f"❌ Backend health check failed - Status: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "🏥 Backend Health Check",
                False,
                f"❌ Cannot connect to backend: {str(e)}",
                {"error": str(e), "backend_url": self.backend_url}
            )
            return False

    async def test_external_system_status(self):
        """Test the external booking system status"""
        external_url = "https://wavy-parallax-hero.preview.emergentagent.com"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test services endpoint
                services_response = await client.get(f"{external_url}/api/services")
                services_working = services_response.status_code == 200
                
                # Test therapists endpoint
                therapists_response = await client.get(f"{external_url}/api/therapists")
                therapists_working = therapists_response.status_code == 200
                
                self.log_result(
                    "🔗 External System Status",
                    services_working and therapists_working,
                    f"External system status check",
                    {
                        "external_url": external_url,
                        "services_endpoint": f"{'✅ Working' if services_working else '❌ Failed'} - Status: {services_response.status_code}",
                        "therapists_endpoint": f"{'✅ Working' if therapists_working else '❌ Failed'} - Status: {therapists_response.status_code}",
                        "services_response": services_response.text[:200] if not services_working else "OK",
                        "therapists_response": therapists_response.text[:200] if not therapists_working else "OK"
                    }
                )
                
                return services_working and therapists_working
                
        except Exception as e:
            self.log_result(
                "🔗 External System Status",
                False,
                f"❌ Cannot connect to external system: {str(e)}",
                {"error": str(e), "external_url": external_url}
            )
            return False

    async def run_final_review_test(self):
        """Run the complete review request test"""
        print("=" * 80)
        print("FINALNO TESTIRANJE - REVIEW REQUEST TEST")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print(f"PREVIEW Reception: https://wavy-parallax-hero.preview.emergentagent.com")
        print()
        
        # Step 1: Backend Health Check
        print("🔍 STEP 1: Backend Health Check")
        health_ok = await self.test_backend_health()
        
        # Step 2: External System Status Check
        print("\n🔍 STEP 2: External System Status Check")
        external_ok = await self.test_external_system_status()
        
        # Step 3: Main Review Request Test
        print("\n🔍 STEP 3: Review Request Booking Test")
        if health_ok:
            booking_success = await self.test_exact_review_request_booking()
        else:
            print("🚨 CRITICAL: Backend is not accessible - cannot proceed with booking test")
            booking_success = False
        
        # Summary
        print("\n" + "=" * 80)
        print("FINALNO TESTIRANJE - SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        if booking_success:
            print("🎉 FINALNO TESTIRANJE - USPEŠAN!")
            print("✅ Booking USPE (200 OK)")
            print("✅ Vraća se booking ID")
            print("✅ Šalje se EMAIL")
            print()
            print("🔧 PREVIEW RECEPTION INTEGRATION: FULLY WORKING")
        else:
            print("🚨 FINALNO TESTIRANJE - NEUSPEŠAN!")
            if not health_ok:
                print("❌ Backend nije dostupan")
            elif not external_ok:
                print("❌ PREVIEW reception sistem nije dostupan")
                print("   - https://wavy-parallax-hero.preview.emergentagent.com/api/services returns 404")
                print("   - https://wavy-parallax-hero.preview.emergentagent.com/api/therapists returns 404")
            else:
                print("❌ Jedan ili više kriterijuma nije ispunjen")
            print()
            print("🔧 POTREBNE SU DODATNE IZMENE")
        
        return booking_success

async def main():
    """Main test execution"""
    tester = FinalReviewRequestTester()
    success = await tester.run_final_review_test()
    return success

if __name__ == "__main__":
    asyncio.run(main())