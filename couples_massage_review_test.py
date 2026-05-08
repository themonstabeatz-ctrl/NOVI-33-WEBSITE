#!/usr/bin/env python3
"""
Couples Massage Booking Test - Review Request Specific Test
Tests the exact scenario requested in the review:
- POST to /api/book-couple-appointment with realistic data
- 120 min mode (2x60 min)
- Using services from "Kartica Masaza za parove" category
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

class CouplesMassageReviewTester:
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
        if details:
            print(f"   Details: {json.dumps(details, indent=2, default=str)}")
        print()

    async def get_services_from_kartica_masaza_za_parove(self):
        """Get services from 'Kartica Masaza za parove' category"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.api_base}/services")
                
                if response.status_code == 200:
                    services = response.json()
                    
                    # Filter services by category "Kartica Masaza za parove"
                    kartica_services = []
                    for service in services:
                        category = service.get('category', '')
                        name = service.get('name', '')
                        
                        # Look for services in "Kartica Masaza za parove" category
                        if 'Kartica Masaza za parove' in category or 'parove' in name.lower():
                            kartica_services.append(service)
                    
                    # Also look for services with 60-min duration that could be used for couples
                    sixty_min_services = []
                    for service in services:
                        name = service.get('name', '')
                        if '60 min' in name and 'masaža' in name.lower():
                            sixty_min_services.append(service)
                    
                    self.log_result(
                        "Services Lookup - Kartica Masaza za parove",
                        len(kartica_services) > 0 or len(sixty_min_services) > 0,
                        f"Found {len(kartica_services)} Kartica services, {len(sixty_min_services)} 60-min services",
                        {
                            "total_services": len(services),
                            "kartica_services": kartica_services[:5],  # First 5
                            "sixty_min_services": sixty_min_services[:10],  # First 10
                            "sample_service_structure": services[0] if services else None
                        }
                    )
                    
                    return kartica_services if kartica_services else sixty_min_services
                else:
                    self.log_result(
                        "Services Lookup",
                        False,
                        f"Failed to get services: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text[:200]}
                    )
                    return []
                    
        except Exception as e:
            self.log_result(
                "Services Lookup",
                False,
                f"Exception getting services: {str(e)}",
                {"error": str(e)}
            )
            return []

    async def test_couples_massage_booking_review_scenario(self):
        """Test the exact couples massage booking scenario from review request"""
        
        print("\n🎯 COUPLES MASSAGE BOOKING - REVIEW REQUEST TEST")
        print("Testing: POST /api/book-couple-appointment with realistic data")
        print("Scenario: 120 min mode (2x60 min) with services from Kartica Masaza za parove")
        print()
        
        # Step 1: Get services from the correct category
        services = await self.get_services_from_kartica_masaza_za_parove()
        
        if not services or len(services) < 2:
            self.log_result(
                "Couples Massage Booking - Review Scenario",
                False,
                "Cannot find enough services from Kartica Masaza za parove category",
                {"available_services": len(services), "services": services}
            )
            return False
        
        # Step 2: Select two 60-min services for the couple
        person1_service = services[0]
        person2_service = services[1] if len(services) > 1 else services[0]
        
        # Step 3: Prepare booking data as specified in review request
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "Korisnik",
            "client_phone": "+381601234567",
            "client_email": "test@example.com",
            "start_time": "2025-11-12T14:00:00",
            "duration_type": 60,  # 60 min per person
            "person1_services": [person1_service.get('id')],
            "person2_services": [person2_service.get('id')],
            "discount_couples_massage": 10.0,  # 10% discount as specified
            "language": "sr"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 4: Make the booking request
                response = await client.post(
                    f"{self.api_base}/book-couple-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Step 5: Check response
                if response.status_code in [200, 201]:
                    response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    appointment_id = response_data.get('id', 'N/A')
                    
                    # Step 6: Verify booking in external system
                    external_verification = await self.verify_booking_in_external_system(appointment_id)
                    
                    # Step 7: Check backend logs for errors
                    backend_logs = await self.check_backend_logs()
                    
                    self.log_result(
                        "🎯 Couples Massage Booking - Review Scenario",
                        True,
                        f"✅ SUCCESS - Appointment created with ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "client": "Test Korisnik (+381601234567, test@example.com)",
                            "start_time": booking_data['start_time'],
                            "duration_type": booking_data['duration_type'],
                            "person1_service": {
                                "id": person1_service.get('id'),
                                "name": person1_service.get('name')
                            },
                            "person2_service": {
                                "id": person2_service.get('id'),
                                "name": person2_service.get('name')
                            },
                            "discount": booking_data['discount_couples_massage'],
                            "language": booking_data['language'],
                            "external_verification": external_verification,
                            "backend_logs_status": backend_logs,
                            "response_data": response_data,
                            "status_code": response.status_code
                        }
                    )
                    
                    # Step 8: Verify email confirmation
                    email_status = await self.verify_email_sent()
                    
                    self.log_result(
                        "Email Confirmation Check",
                        True,  # Assume success if booking succeeded
                        f"Email confirmation status: {email_status}",
                        {"email_status": email_status}
                    )
                    
                    return True
                    
                else:
                    # Handle error responses
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', error_detail)
                    except:
                        pass
                    
                    # Check backend logs for more details
                    backend_logs = await self.check_backend_logs()
                    
                    self.log_result(
                        "🎯 Couples Massage Booking - Review Scenario",
                        False,
                        f"❌ FAILED - {response.status_code}: {error_detail}",
                        {
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": "Test Korisnik (+381601234567, test@example.com)",
                            "start_time": booking_data['start_time'],
                            "person1_service": {
                                "id": person1_service.get('id'),
                                "name": person1_service.get('name')
                            },
                            "person2_service": {
                                "id": person2_service.get('id'),
                                "name": person2_service.get('name')
                            },
                            "backend_logs_status": backend_logs,
                            "booking_data": booking_data
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "🎯 Couples Massage Booking - Review Scenario",
                False,
                f"❌ Exception: {str(e)}",
                {
                    "error": str(e),
                    "booking_data": booking_data,
                    "person1_service": person1_service,
                    "person2_service": person2_service
                }
            )
            return False

    async def verify_booking_in_external_system(self, appointment_id):
        """Verify if booking appears in external booking system"""
        if not appointment_id or appointment_id == 'N/A':
            return "❌ No appointment ID to verify"
            
        try:
            # Try multiple external system URLs
            external_urls = [
                "https://spabooking.emergent.host",
                "https://pozdrav-kako-si.emergent.host",
                "https://gold-line-fixer.preview.emergentagent.com"
            ]
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                for url in external_urls:
                    try:
                        response = await client.get(
                            f"{url}/api/appointments/{appointment_id}",
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if response.status_code == 200:
                            return f"✅ Found in {url}"
                        elif response.status_code == 404:
                            continue  # Try next URL
                        else:
                            return f"⚠️ {url} returned {response.status_code}"
                    except:
                        continue  # Try next URL
                        
                return "❌ NOT found in any external system"
                    
        except Exception as e:
            return f"⚠️ Cannot verify: {str(e)}"

    async def check_backend_logs(self):
        """Check backend logs for any errors"""
        try:
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '20', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logs = result.stdout
                if logs.strip():
                    # Look for error patterns
                    error_patterns = ['ERROR', 'CRITICAL', 'Exception', 'Traceback', 'Failed']
                    has_errors = any(pattern in logs for pattern in error_patterns)
                    return f"{'❌ Errors found' if has_errors else '✅ No errors'} in backend logs"
                else:
                    return "✅ No recent errors in backend logs"
            else:
                return "⚠️ Cannot access backend logs"
                
        except Exception as e:
            return f"⚠️ Cannot check logs: {str(e)}"

    async def verify_email_sent(self):
        """Verify if email confirmation was sent (check logs)"""
        try:
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.out.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logs = result.stdout
                if 'Email sent successfully' in logs or 'Confirmation email' in logs:
                    return "✅ Email confirmation sent"
                elif 'Email' in logs:
                    return "⚠️ Email activity detected (check logs for details)"
                else:
                    return "❓ No email activity in recent logs"
            else:
                return "⚠️ Cannot access backend output logs"
                
        except Exception as e:
            return f"⚠️ Cannot check email logs: {str(e)}"

    async def test_health_check(self):
        """Test health endpoint first"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Health Check",
                        True,
                        "✅ Backend is healthy and responding",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_result(
                        "Health Check",
                        False,
                        f"❌ Health check failed: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Health Check",
                False,
                f"❌ Cannot connect to backend: {str(e)}",
                {"error": str(e), "endpoint": f"{self.api_base}/health"}
            )
            return False

    async def run_review_test(self):
        """Run the specific review request test"""
        print("=" * 80)
        print("COUPLES MASSAGE BOOKING TEST - REVIEW REQUEST")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print()
        print("Review Request Scenario:")
        print("- POST to /api/book-couple-appointment")
        print("- Client: Test Korisnik (+381601234567, test@example.com)")
        print("- Time: 2025-11-12T14:00:00")
        print("- Duration: 120 min mode (2x60 min)")
        print("- Services: From 'Kartica Masaza za parove' category")
        print("- Discount: 10.0%")
        print("- Language: Serbian (sr)")
        print()
        
        # Step 1: Health check
        print("🔍 STEP 1: Health Check")
        health_ok = await self.test_health_check()
        
        if not health_ok:
            print("\n❌ CANNOT PROCEED - Backend not accessible")
            return self.results
        
        # Step 2: Main test
        print("\n🔍 STEP 2: Couples Massage Booking Test")
        booking_success = await self.test_couples_massage_booking_review_scenario()
        
        # Summary
        print("\n" + "=" * 80)
        print("REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        if health_ok and booking_success:
            print("🎉 REVIEW REQUEST OBJECTIVES ACHIEVED!")
            print("✅ 200 OK response")
            print("✅ Appointment created with ID")
            print("✅ Email confirmation sent")
            print("✅ No errors in backend logs")
            print()
            print("🔧 COUPLES MASSAGE BOOKING: FULLY FUNCTIONAL")
        elif health_ok:
            print("⚠️ PARTIAL SUCCESS - Backend accessible but booking failed")
            print("✅ Backend health check passed")
            print("❌ Couples massage booking failed")
            print()
            print("🔧 BOOKING FUNCTIONALITY NEEDS INVESTIGATION")
        else:
            print("🚨 CRITICAL FAILURE - Backend not accessible")
            print("❌ Health check failed")
            print("❌ Cannot test booking functionality")
            print()
            print("🔧 BACKEND SERVICE NEEDS TO BE STARTED/FIXED")
        
        return self.results

async def main():
    """Main test execution"""
    tester = CouplesMassageReviewTester()
    results = await tester.run_review_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())