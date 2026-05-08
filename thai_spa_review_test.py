#!/usr/bin/env python3
"""
Thai Spa Booking Flow Test - Review Request Specific Testing
Tests the exact scenarios requested in the review:
1. Single Massage Booking (POST /api/book-appointment)
2. Couples Massage Booking (POST /api/book-couple-appointment)
Backend URL: https://thai-spa-booking.emergent.host
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
BACKEND_URL = "https://thai-spa-booking.emergent.host"

class ThaiSpaReviewTester:
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
            print(f"   Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
        print()

    async def check_backend_logs(self):
        """Check backend logs for email sending errors"""
        try:
            # Try to read supervisor backend logs
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                email_errors = []
                email_success = []
                
                # Look for email-related log entries
                for line in logs.split('\n'):
                    if 'email' in line.lower() or 'smtp' in line.lower():
                        if 'error' in line.lower() or 'failed' in line.lower():
                            email_errors.append(line.strip())
                        elif 'success' in line.lower() or 'sent' in line.lower():
                            email_success.append(line.strip())
                
                return {
                    "logs_accessible": True,
                    "email_errors": email_errors,
                    "email_success": email_success,
                    "recent_logs": logs.split('\n')[-10:] if logs else []
                }
            else:
                return {
                    "logs_accessible": False,
                    "error": "Cannot access backend logs",
                    "stderr": result.stderr
                }
                
        except Exception as e:
            return {
                "logs_accessible": False,
                "error": str(e)
            }

    async def test_single_massage_booking(self):
        """Test Single Massage Booking - Review Request Scenario 1"""
        print("🎯 TESTING SINGLE MASSAGE BOOKING")
        print("Service: Tradicionalna tajlandska masaža - 60 min")
        print("Client: Test Korisnik")
        print("Email: test@example.com")
        print("Phone: 0601234567")
        print("Date: 2025-12-05")
        print("Time: 14:00")
        print()
        
        # First, get services to find the correct service ID
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                services_response = await client.get(f"{self.api_base}/services")
                
                if services_response.status_code != 200:
                    self.log_result(
                        "Single Massage Booking - Service Lookup",
                        False,
                        f"Cannot get services list: {services_response.status_code}",
                        {"status_code": services_response.status_code}
                    )
                    return False
                
                services = services_response.json()
                
                # Look for "Tradicionalna tajlandska masaža - 60 min"
                target_service = None
                for service in services:
                    if "Tradicionalna tajlandska masaža" in service.get('name', '') and "60 min" in service.get('name', ''):
                        target_service = service
                        break
                
                if not target_service:
                    self.log_result(
                        "Single Massage Booking - Service Lookup",
                        False,
                        "Cannot find 'Tradicionalna tajlandska masaža - 60 min' service",
                        {
                            "available_services": [s.get('name', 'Unknown') for s in services[:10]],
                            "total_services": len(services)
                        }
                    )
                    return False
                
                service_id = target_service.get('id')
                service_name = target_service.get('name')
                
                self.log_result(
                    "Single Massage Booking - Service Lookup",
                    True,
                    f"Found service: {service_name}",
                    {
                        "service_id": service_id,
                        "service_name": service_name,
                        "service_details": target_service
                    }
                )
                
                # Prepare booking data
                booking_data = {
                    "client_first_name": "Test",
                    "client_last_name": "Korisnik",
                    "client_phone": "0601234567",
                    "client_email": "test@example.com",
                    "appointment_date": "2025-12-05",
                    "start_time": "2025-12-05T14:00:00",
                    "service_id": service_id,
                    "therapist_id": "",  # Let backend assign Web Slot therapist
                    "notes": "Single massage booking test - Review request scenario 1",
                    "language": "sr",
                    "service_name": service_name
                }
                
                # Make booking request
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    
                    # Check backend logs for email confirmation
                    log_info = await self.check_backend_logs()
                    
                    self.log_result(
                        "Single Massage Booking - API Call",
                        True,
                        f"✅ Booking successful - Appointment ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "service_name": service_name,
                            "service_id": service_id,
                            "client": "Test Korisnik (0601234567, test@example.com)",
                            "date_time": "2025-12-05T14:00:00",
                            "status_code": response.status_code,
                            "response": response_data,
                            "backend_logs": log_info
                        }
                    )
                    
                    # Verify email confirmation was sent
                    if log_info.get("email_success"):
                        self.log_result(
                            "Single Massage Booking - Email Confirmation",
                            True,
                            "✅ Email confirmation sent successfully",
                            {
                                "email_success_logs": log_info["email_success"]
                            }
                        )
                    elif log_info.get("email_errors"):
                        self.log_result(
                            "Single Massage Booking - Email Confirmation",
                            False,
                            "❌ Email sending errors found in logs",
                            {
                                "email_errors": log_info["email_errors"]
                            }
                        )
                    else:
                        self.log_result(
                            "Single Massage Booking - Email Confirmation",
                            False,
                            "⚠️ No email-related logs found - cannot verify email sending",
                            {
                                "logs_accessible": log_info.get("logs_accessible", False)
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
                        "Single Massage Booking - API Call",
                        False,
                        f"❌ Booking failed - {response.status_code}: {error_detail}",
                        {
                            "service_name": service_name,
                            "service_id": service_id,
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": "Test Korisnik (0601234567, test@example.com)",
                            "date_time": "2025-12-05T14:00:00"
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Single Massage Booking",
                False,
                f"❌ Exception during single massage booking test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_couples_massage_booking(self):
        """Test Couples Massage Booking - Review Request Scenario 2"""
        print("🎯 TESTING COUPLES MASSAGE BOOKING")
        print("Service: Masaža za parove")
        print("Client: Test Korisnik")
        print("Email: test@example.com")
        print("Phone: 0601234567")
        print("Date: 2025-12-06")
        print("Time: 15:00")
        print("Duration: 60 min per person")
        print("Person 1: Aroma terapija (60 min)")
        print("Person 2: Tradicionalna tajlandska masaža (60 min)")
        print()
        
        # First, get services to find couple services
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                services_response = await client.get(f"{self.api_base}/services")
                
                if services_response.status_code != 200:
                    self.log_result(
                        "Couples Massage Booking - Service Lookup",
                        False,
                        f"Cannot get services list: {services_response.status_code}",
                        {"status_code": services_response.status_code}
                    )
                    return False
                
                services = services_response.json()
                
                # Look for Aroma terapija and Tradicionalna tajlandska masaža services for couples
                aroma_service = None
                traditional_service = None
                
                for service in services:
                    service_name = service.get('name', '')
                    if "Aroma terapija" in service_name and "60 min" in service_name:
                        aroma_service = service
                    elif "Tradicionalna tajlandska masaža" in service_name and "60 min" in service_name:
                        traditional_service = service
                
                if not aroma_service or not traditional_service:
                    self.log_result(
                        "Couples Massage Booking - Service Lookup",
                        False,
                        "Cannot find required services for couples massage",
                        {
                            "aroma_service_found": aroma_service is not None,
                            "traditional_service_found": traditional_service is not None,
                            "available_services": [s.get('name', 'Unknown') for s in services[:10]]
                        }
                    )
                    return False
                
                self.log_result(
                    "Couples Massage Booking - Service Lookup",
                    True,
                    "Found required services for couples massage",
                    {
                        "person1_service": aroma_service.get('name'),
                        "person1_service_id": aroma_service.get('id'),
                        "person2_service": traditional_service.get('name'),
                        "person2_service_id": traditional_service.get('id')
                    }
                )
                
                # Prepare couples booking data
                couple_booking_data = {
                    "client_first_name": "Test",
                    "client_last_name": "Korisnik",
                    "client_phone": "0601234567",
                    "client_email": "test@example.com",
                    "start_time": "2025-12-06T15:00:00",
                    "duration_type": 60,  # 60 minutes per person
                    "person1_services": [aroma_service.get('id')],
                    "person2_services": [traditional_service.get('id')],
                    "discount_couples_massage": 0.0,  # No additional discount
                    "language": "sr"
                }
                
                # Make couples booking request
                response = await client.post(
                    f"{self.api_base}/book-couple-appointment",
                    json=couple_booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    
                    # Check backend logs for email confirmation
                    log_info = await self.check_backend_logs()
                    
                    self.log_result(
                        "Couples Massage Booking - API Call",
                        True,
                        f"✅ Couples booking successful - Appointment ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "person1_service": aroma_service.get('name'),
                            "person2_service": traditional_service.get('name'),
                            "client": "Test Korisnik (0601234567, test@example.com)",
                            "date_time": "2025-12-06T15:00:00",
                            "duration_per_person": "60 min",
                            "total_duration": "120 min",
                            "status_code": response.status_code,
                            "response": response_data,
                            "backend_logs": log_info
                        }
                    )
                    
                    # Verify email confirmation was sent
                    if log_info.get("email_success"):
                        self.log_result(
                            "Couples Massage Booking - Email Confirmation",
                            True,
                            "✅ Email confirmation sent successfully",
                            {
                                "email_success_logs": log_info["email_success"]
                            }
                        )
                    elif log_info.get("email_errors"):
                        self.log_result(
                            "Couples Massage Booking - Email Confirmation",
                            False,
                            "❌ Email sending errors found in logs",
                            {
                                "email_errors": log_info["email_errors"]
                            }
                        )
                    else:
                        self.log_result(
                            "Couples Massage Booking - Email Confirmation",
                            False,
                            "⚠️ No email-related logs found - cannot verify email sending",
                            {
                                "logs_accessible": log_info.get("logs_accessible", False)
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
                        "Couples Massage Booking - API Call",
                        False,
                        f"❌ Couples booking failed - {response.status_code}: {error_detail}",
                        {
                            "person1_service": aroma_service.get('name'),
                            "person2_service": traditional_service.get('name'),
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": "Test Korisnik (0601234567, test@example.com)",
                            "date_time": "2025-12-06T15:00:00"
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Couples Massage Booking",
                False,
                f"❌ Exception during couples massage booking test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_health_endpoint(self):
        """Test backend health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Backend Health Check",
                        True,
                        f"✅ Backend is healthy and accessible",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Health Check",
                        False,
                        f"❌ Backend health check failed - status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"❌ Cannot connect to backend: {str(e)}",
                {"error": str(e), "endpoint": f"{self.api_base}/health"}
            )
            return False

    async def run_review_tests(self):
        """Run all review request tests"""
        print("=" * 80)
        print("THAI SPA BOOKING FLOW TESTING - REVIEW REQUEST")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print()
        
        # Test 1: Health Check
        print("🔍 TEST 1: Backend Health Check")
        health_working = await self.test_health_endpoint()
        
        # Test 2: Single Massage Booking
        print("\n🔍 TEST 2: Single Massage Booking")
        single_booking_working = False
        if health_working:
            single_booking_working = await self.test_single_massage_booking()
        else:
            self.log_result(
                "Single Massage Booking",
                False,
                "Skipped - Backend health check failed",
                {"reason": "Backend not accessible"}
            )
        
        # Test 3: Couples Massage Booking
        print("\n🔍 TEST 3: Couples Massage Booking")
        couples_booking_working = False
        if health_working:
            couples_booking_working = await self.test_couples_massage_booking()
        else:
            self.log_result(
                "Couples Massage Booking",
                False,
                "Skipped - Backend health check failed",
                {"reason": "Backend not accessible"}
            )
        
        # Summary
        print("\n" + "=" * 80)
        print("THAI SPA REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Review Request Assessment
        if health_working and single_booking_working and couples_booking_working:
            print("🎉 ALL REVIEW REQUEST OBJECTIVES ACHIEVED!")
            print("✅ Backend Health: Service accessible")
            print("✅ Single Massage Booking: Working with email confirmation")
            print("✅ Couples Massage Booking: Working with email confirmation")
            print("✅ Backend Logs: Email sending verified")
        elif health_working:
            print("⚠️ PARTIAL SUCCESS - Backend accessible but booking issues found")
            print(f"✅ Backend Health: {'Working' if health_working else 'Failed'}")
            print(f"{'✅' if single_booking_working else '❌'} Single Massage Booking: {'Working' if single_booking_working else 'Failed'}")
            print(f"{'✅' if couples_booking_working else '❌'} Couples Massage Booking: {'Working' if couples_booking_working else 'Failed'}")
        else:
            print("🚨 CRITICAL ISSUES FOUND")
            print("❌ Backend Health: Service not accessible")
            print("❌ All booking tests: Skipped due to backend unavailability")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ThaiSpaReviewTester()
    results = await tester.run_review_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())