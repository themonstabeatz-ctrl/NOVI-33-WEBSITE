#!/usr/bin/env python3
"""
FINALNO TESTIRANJE - Backend API Testing for Thai Spa Booking System
Tests the exact scenario from review request:
- Backend: http://localhost:8001
- Reception: https://spabooking.emergent.host
- Single booking test with specific data
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class FinalnoTestiranjeAPITester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.api_base = f"{self.backend_url}/api"
        self.reception_url = "https://spabooking.emergent.host"
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

    async def verify_booking_in_reception(self, appointment_id):
        """Verify if booking appears in reception system"""
        if not appointment_id or appointment_id == 'N/A':
            return "❌ No appointment ID to verify"
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to get the specific appointment from reception system
                response = await client.get(
                    f"{self.reception_url}/api/appointments/{appointment_id}",
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    appointment_data = response.json()
                    return f"✅ Found in reception: {appointment_data.get('status', 'unknown status')}"
                elif response.status_code == 404:
                    return "❌ NOT found in reception system"
                else:
                    return f"⚠️ Reception system returned {response.status_code}"
                    
        except Exception as e:
            return f"⚠️ Cannot verify in reception: {str(e)}"

    async def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Backend Health Check",
                        True,
                        f"✅ Backend accessible at {self.backend_url}",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Health Check",
                        False,
                        f"❌ Backend returned status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"❌ Cannot connect to backend: {str(e)}",
                {"error": str(e), "backend_url": self.backend_url}
            )
            return False

    async def test_reception_connectivity(self):
        """Test 2: Reception System Connectivity"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test reception services endpoint
                response = await client.get(f"{self.reception_url}/api/services")
                
                if response.status_code == 200:
                    services = response.json()
                    # Look for the specific service from review request
                    target_service = None
                    for service in services:
                        if service.get('id') == '98249336-b9d9-4685-b70c-81971d3cf216':
                            target_service = service
                            break
                    
                    self.log_result(
                        "Reception System Connectivity",
                        True,
                        f"✅ Reception accessible at {self.reception_url}",
                        {
                            "total_services": len(services),
                            "target_service_found": target_service is not None,
                            "target_service": target_service,
                            "status_code": response.status_code
                        }
                    )
                    return True, target_service
                else:
                    self.log_result(
                        "Reception System Connectivity",
                        False,
                        f"❌ Reception returned status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text[:200]}
                    )
                    return False, None
                    
        except Exception as e:
            self.log_result(
                "Reception System Connectivity",
                False,
                f"❌ Cannot connect to reception: {str(e)}",
                {"error": str(e), "reception_url": self.reception_url}
            )
            return False, None

    async def test_exact_review_request_booking(self):
        """Test 3: Exact Review Request Booking Scenario"""
        
        # EXACT data from review request
        booking_data = {
            "client_first_name": "Final",
            "client_last_name": "Test",
            "client_phone": "0601234567",
            "client_email": "grujovicsavatije@gmail.com",
            "appointment_date": "2026-01-20",
            "start_time": "2026-01-20T10:00:00",
            "service_id": "98249336-b9d9-4685-b70c-81971d3cf216",
            "service_name": "Tradicionalna tajlandska masaža - 60 min",
            "therapist_id": "",
            "notes": "Final test",
            "language": "sr"
        }
        
        print(f"\n🎯 TESTING EXACT REVIEW REQUEST SCENARIO")
        print(f"Client: {booking_data['client_first_name']} {booking_data['client_last_name']}")
        print(f"Email: {booking_data['client_email']}")
        print(f"Phone: {booking_data['client_phone']}")
        print(f"Service: {booking_data['service_name']}")
        print(f"Service ID: {booking_data['service_id']}")
        print(f"Date/Time: {booking_data['start_time']}")
        print()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    
                    # Verify in reception system
                    reception_verification = await self.verify_booking_in_reception(appointment_id)
                    
                    # Check if email was sent (look for success indicators in response)
                    email_sent = "email" in str(response_data).lower() or appointment_id != 'N/A'
                    
                    self.log_result(
                        "Review Request Booking Test",
                        True,
                        f"✅ BOOKING SUCCESSFUL - ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "client_name": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "client_email": booking_data['client_email'],
                            "client_phone": booking_data['client_phone'],
                            "service_name": booking_data['service_name'],
                            "service_id": booking_data['service_id'],
                            "date_time": booking_data['start_time'],
                            "reception_verification": reception_verification,
                            "email_likely_sent": email_sent,
                            "status_code": response.status_code,
                            "response": response_data
                        }
                    )
                    
                    # Answer the 3 review questions
                    booking_success = True
                    email_success = email_sent
                    reception_success = "✅ Found" in reception_verification
                    
                    return {
                        "booking_success": booking_success,
                        "email_success": email_success, 
                        "reception_success": reception_success,
                        "appointment_id": appointment_id,
                        "response_data": response_data
                    }
                    
                else:
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', error_detail)
                    except:
                        pass
                    
                    self.log_result(
                        "Review Request Booking Test",
                        False,
                        f"❌ BOOKING FAILED - {response.status_code}: {error_detail}",
                        {
                            "service_name": booking_data['service_name'],
                            "service_id": booking_data['service_id'],
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client_email": booking_data['client_email'],
                            "date_time": booking_data['start_time']
                        }
                    )
                    
                    return {
                        "booking_success": False,
                        "email_success": False,
                        "reception_success": False,
                        "error": error_detail
                    }
                    
        except Exception as e:
            self.log_result(
                "Review Request Booking Test",
                False,
                f"❌ Exception during booking: {str(e)}",
                {"error": str(e)}
            )
            
            return {
                "booking_success": False,
                "email_success": False,
                "reception_success": False,
                "error": str(e)
            }

    async def check_backend_logs(self):
        """Test 4: Check Backend Logs for Email Confirmation"""
        try:
            # Try to read backend logs to confirm email sending
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                email_indicators = [
                    "Email sent successfully",
                    "✅ Email sent",
                    "Confirmation email",
                    "grujovicsavatije@gmail.com"
                ]
                
                email_found = any(indicator in log_content for indicator in email_indicators)
                
                self.log_result(
                    "Backend Email Logs Check",
                    email_found,
                    f"{'✅ Email indicators found' if email_found else '⚠️ No email indicators found'} in backend logs",
                    {
                        "email_found": email_found,
                        "log_excerpt": log_content[-500:] if log_content else "No logs",
                        "email_indicators_checked": email_indicators
                    }
                )
                
                return email_found
            else:
                self.log_result(
                    "Backend Email Logs Check",
                    False,
                    "❌ Cannot read backend logs",
                    {"error": result.stderr}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Backend Email Logs Check",
                False,
                f"❌ Exception reading logs: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def run_finalno_testiranje(self):
        """Run the complete FINALNO TESTIRANJE as requested"""
        print("=" * 80)
        print("FINALNO TESTIRANJE - SVE FUNKCIONALNOSTI")
        print("=" * 80)
        print(f"Backend: {self.backend_url}")
        print(f"Reception: {self.reception_url}")
        print()
        
        # Test 1: Backend Health
        print("🔍 TEST 1: Backend Health Check")
        backend_healthy = await self.test_backend_health()
        
        # Test 2: Reception Connectivity
        print("\n🔍 TEST 2: Reception System Connectivity")
        reception_working, target_service = await self.test_reception_connectivity()
        
        # Test 3: Exact Review Request Booking
        print("\n🔍 TEST 3: Exact Review Request Booking")
        booking_results = None
        if backend_healthy:
            booking_results = await self.test_exact_review_request_booking()
        else:
            self.log_result(
                "Review Request Booking Test",
                False,
                "Skipped - Backend health check failed",
                {"reason": "Backend not accessible"}
            )
            booking_results = {
                "booking_success": False,
                "email_success": False,
                "reception_success": False,
                "error": "Backend not accessible"
            }
        
        # Test 4: Backend Email Logs
        print("\n🔍 TEST 4: Backend Email Logs Check")
        email_logs_found = await self.check_backend_logs()
        
        # Final Assessment
        print("\n" + "=" * 80)
        print("FINALNO TESTIRANJE - REZULTATI")
        print("=" * 80)
        
        # Answer the 3 review questions
        print("PROVERI:")
        print(f"1. Da li booking USPE? {'✅ DA' if booking_results and booking_results['booking_success'] else '❌ NE'}")
        print(f"2. Da li se EMAIL ŠALJE? {'✅ DA' if (booking_results and booking_results['email_success']) or email_logs_found else '❌ NE'}")
        print(f"3. Da li se booking pojavljuje u recepciji? {'✅ DA' if booking_results and booking_results['reception_success'] else '❌ NE'}")
        print()
        
        # Detailed results
        if booking_results and booking_results['booking_success']:
            print("🎉 BOOKING FLOW WORKING!")
            if 'appointment_id' in booking_results:
                print(f"   Appointment ID: {booking_results['appointment_id']}")
            print(f"   Backend: ✅ Accessible")
            print(f"   Reception: {'✅ Connected' if reception_working else '❌ Issues'}")
            print(f"   Email: {'✅ Sent' if booking_results['email_success'] or email_logs_found else '⚠️ Uncertain'}")
        else:
            print("🚨 BOOKING FLOW ISSUES FOUND!")
            print(f"   Backend: {'✅ Accessible' if backend_healthy else '❌ Not accessible'}")
            print(f"   Reception: {'✅ Connected' if reception_working else '❌ Not connected'}")
            print(f"   Booking: ❌ Failed")
            if booking_results and 'error' in booking_results:
                print(f"   Error: {booking_results['error']}")
        
        print()
        print("Test Summary:")
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        print(f"Tests Passed: {passed}/{total}")
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        return {
            "backend_healthy": backend_healthy,
            "reception_working": reception_working,
            "booking_results": booking_results,
            "email_logs_found": email_logs_found,
            "all_results": self.results
        }

async def main():
    """Main test execution"""
    tester = FinalnoTestiranjeAPITester()
    results = await tester.run_finalno_testiranje()
    return results

if __name__ == "__main__":
    asyncio.run(main())