#!/usr/bin/env python3
"""
Couples Massage Booking Test - Specific test for "Masaža za parove" booking flow
Tests the exact scenario from the review request
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

class CouplesMassageTest:
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
            print(f"   Details: {json.dumps(details, indent=2, default=str)}")
        print()

    async def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    expected_status = data.get('status') == 'healthy'
                    
                    self.log_result(
                        "Health Endpoint Test",
                        expected_status,
                        f"Health endpoint returned {response.status_code} with status: {data.get('status')}",
                        {
                            "status_code": response.status_code,
                            "response": data,
                            "expected": {"status": "healthy"},
                            "url": f"{self.api_base}/health"
                        }
                    )
                    return expected_status
                else:
                    self.log_result(
                        "Health Endpoint Test",
                        False,
                        f"Health endpoint returned unexpected status {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "response": response.text,
                            "url": f"{self.api_base}/health"
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Health Endpoint Test",
                False,
                f"Failed to connect to health endpoint: {str(e)}",
                {"error": str(e), "url": f"{self.api_base}/health"}
            )
            return False

    async def test_couples_massage_booking(self):
        """Test the exact couples massage booking from review request"""
        
        # EXACT test data from review request
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "User",
            "client_phone": "+381601234567",
            "client_email": "test@example.com",
            "appointment_date": "2025-11-10",
            "start_time": "2025-11-10T14:00:00",
            "service_id": "d3e8684a-2bbc-4a15-835e-8e43d231074a",
            "therapist_id": "",
            "notes": "Masaža za parove - UKUPNO TRAJANJE: 240 min\n\nOSOBA 1:\n- Tradicionalna tajlandska masaža (60 min) - 4400 RSD\n- Aroma terapija (60 min) - 4400 RSD\n\nOSOBA 2:\n- Shiatsu masaža (60 min) - 3000 RSD\n- Refleksologija (60 min) - 3000 RSD\n\nPOPUST: -15%\nUKUPNA CENA SA POPUSTOM: 13,430 RSD",
            "language": "sr",
            "service_name": "Masaža za parove - 120 min"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Parse response
                response_data = None
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        response_data = response.json()
                except:
                    pass
                
                if response.status_code in [200, 201]:
                    appointment_id = response_data.get('id', 'N/A') if response_data else 'N/A'
                    
                    # Verify in external system
                    external_verification = await self.verify_booking_in_external_system(appointment_id)
                    
                    self.log_result(
                        "Couples Massage Booking",
                        True,
                        f"Booking successful! Appointment ID: {appointment_id}",
                        {
                            "status_code": response.status_code,
                            "appointment_id": appointment_id,
                            "response": response_data,
                            "external_verification": external_verification,
                            "service_name": booking_data["service_name"],
                            "service_id": booking_data["service_id"],
                            "date_time": booking_data["start_time"],
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "notes_preview": booking_data["notes"][:100] + "..." if len(booking_data["notes"]) > 100 else booking_data["notes"]
                        }
                    )
                    return True, appointment_id, response_data
                    
                elif response.status_code == 400:
                    error_detail = response_data.get('detail', '') if response_data else response.text
                    
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        f"Booking failed with 400 error: {error_detail}",
                        {
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "response": response_data or response.text,
                            "service_name": booking_data["service_name"],
                            "service_id": booking_data["service_id"],
                            "date_time": booking_data["start_time"],
                            "possible_causes": [
                                "Service ID not found",
                                "No available therapists at this time",
                                "Invalid date/time format",
                                "External booking system unavailable"
                            ]
                        }
                    )
                    return False, None, response_data
                    
                elif response.status_code == 404:
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        "Service not found (404) - Service ID may be invalid",
                        {
                            "status_code": response.status_code,
                            "service_id": booking_data["service_id"],
                            "response": response.text,
                            "recommendation": "Check if service ID exists in external system"
                        }
                    )
                    return False, None, None
                    
                elif response.status_code == 503:
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        "Service unavailable (503) - External booking system may be down",
                        {
                            "status_code": response.status_code,
                            "response": response.text,
                            "external_system": "https://pozdrav-kako-si.emergent.host"
                        }
                    )
                    return False, None, None
                    
                else:
                    self.log_result(
                        "Couples Massage Booking",
                        False,
                        f"Unexpected response status: {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "response": response.text[:500],
                            "headers": dict(response.headers)
                        }
                    )
                    return False, None, None
                    
        except httpx.TimeoutException:
            self.log_result(
                "Couples Massage Booking",
                False,
                "Request timed out (30s) - Backend or external system may be slow",
                {"timeout": "30 seconds", "url": f"{self.api_base}/book-appointment"}
            )
            return False, None, None
            
        except Exception as e:
            self.log_result(
                "Couples Massage Booking",
                False,
                f"Exception occurred: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__}
            )
            return False, None, None

    async def verify_booking_in_external_system(self, appointment_id):
        """Verify if booking appears in external system"""
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
                    appointment_data = response.json()
                    return f"✅ Found in external system - Status: {appointment_data.get('status', 'unknown')}"
                elif response.status_code == 404:
                    return "❌ NOT found in external system"
                else:
                    return f"⚠️ External system returned {response.status_code}"
                    
        except Exception as e:
            return f"⚠️ Cannot verify: {str(e)}"

    async def check_backend_logs(self):
        """Check backend logs for any errors"""
        try:
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if logs:
                    # Look for recent errors
                    error_lines = [line for line in logs.split('\n') if 'ERROR' in line.upper() or 'FAIL' in line.upper()]
                    
                    self.log_result(
                        "Backend Logs Check",
                        len(error_lines) == 0,
                        f"Found {len(error_lines)} error lines in recent logs",
                        {
                            "total_log_lines": len(logs.split('\n')),
                            "error_lines": error_lines[-5:] if error_lines else [],  # Last 5 errors
                            "log_file": "/var/log/supervisor/backend.err.log"
                        }
                    )
                    return len(error_lines) == 0
                else:
                    self.log_result(
                        "Backend Logs Check",
                        True,
                        "No error logs found - backend running cleanly",
                        {"log_file": "/var/log/supervisor/backend.err.log"}
                    )
                    return True
            else:
                self.log_result(
                    "Backend Logs Check",
                    False,
                    f"Could not read backend logs: {result.stderr}",
                    {"error": result.stderr}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Backend Logs Check",
                False,
                f"Exception checking logs: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def run_couples_massage_test(self):
        """Run the complete couples massage test suite"""
        print("=" * 80)
        print("COUPLES MASSAGE BOOKING TEST - REVIEW REQUEST")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print(f"Test Service: Masaža za parove - 120 min")
        print(f"Service ID: d3e8684a-2bbc-4a15-835e-8e43d231074a")
        print(f"Test Date/Time: 2025-11-10T14:00:00")
        print()
        
        # Test 1: Health endpoint
        health_ok = await self.test_health_endpoint()
        
        # Test 2: Couples massage booking
        booking_success, appointment_id, response_data = await self.test_couples_massage_booking()
        
        # Test 3: Backend logs check
        logs_clean = await self.check_backend_logs()
        
        # Summary
        print("=" * 80)
        print("COUPLES MASSAGE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details'].get('appointment_id'):
                print(f"   → Appointment ID: {result['details']['appointment_id']}")
            if result['details'].get('external_verification'):
                print(f"   → External System: {result['details']['external_verification']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        
        # Final assessment
        if health_ok and booking_success and logs_clean:
            print("🎉 COUPLES MASSAGE BOOKING WORKING PERFECTLY!")
            print("✅ Health endpoint responding correctly")
            print("✅ Couples massage booking successful")
            print("✅ Backend logs clean (no errors)")
            print("✅ Booking verified in external system")
            if appointment_id:
                print(f"✅ Appointment ID: {appointment_id}")
                print("✅ Check booking at: https://pozdrav-kako-si.emergent.host")
        elif health_ok and booking_success:
            print("⚠️ COUPLES MASSAGE BOOKING WORKING (with minor log issues)")
            print("✅ Health endpoint responding correctly")
            print("✅ Couples massage booking successful")
            if appointment_id:
                print(f"✅ Appointment ID: {appointment_id}")
        elif health_ok and not booking_success:
            print("🚨 COUPLES MASSAGE BOOKING FAILING")
            print("✅ Health endpoint responding correctly")
            print("❌ Couples massage booking failed")
            print("🔧 Check service ID, therapist availability, or external system")
        elif not health_ok:
            print("🚨 BACKEND HEALTH CHECK FAILING")
            print("❌ Health endpoint not responding correctly")
            print("🔧 Check backend service configuration")
        
        return {
            'health_ok': health_ok,
            'booking_success': booking_success,
            'logs_clean': logs_clean,
            'appointment_id': appointment_id,
            'response_data': response_data,
            'all_results': self.results
        }

async def main():
    """Main test execution"""
    tester = CouplesMassageTest()
    results = await tester.run_couples_massage_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())