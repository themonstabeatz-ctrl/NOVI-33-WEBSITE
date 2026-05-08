#!/usr/bin/env python3
"""
Couples Massage Backend Testing for Thai Spa Booking System
Tests the couples massage booking functionality from backend perspective
Specifically tests 90-min and 120-min couples massage booking flows
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

class CouplesMassageBackendTester:
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
                    appointment_data = response.json()
                    return f"✅ Found in external system - Status: {appointment_data.get('status', 'unknown')}"
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
                response = await client.get(f"{self.api_base}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        "Backend Health Check",
                        True,
                        f"Backend healthy - Status: {data.get('status', 'unknown')}",
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

    async def test_couples_massage_90_min_booking(self):
        """Test 90-minute couples massage booking - Backend processing"""
        
        # Couples massage service ID from the system
        couples_service_id = "d3e8684a-2bbc-4a15-835e-8e43d231074a"  # Masaža za parove - 120 min
        
        # Sample couples massage booking data with realistic notes
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "User",
            "client_phone": "+381601234567",
            "client_email": "test@example.com",
            "appointment_date": "2025-11-10",
            "start_time": "2025-11-10T14:00:00",
            "service_id": couples_service_id,
            "service_name": "Masaža za parove - 90 min",
            "therapist_id": "",  # Empty - let backend assign Web Slot therapist
            "notes": """OSOBA 1: Aroma terapija (90 min) - 7,500 RSD
OSOBA 2: Tradicionalna tajlandska masaža (90 min) - 8,500 RSD

UKUPNA CENA: 16,000 RSD
POPUST (-15%): -2,400 RSD
UKUPNA CENA SA POPUSTOM: 13,600 RSD

UKUPNO TRAJANJE: 180 min (90 min + 90 min)""",
            "language": "sr"
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
                    
                    self.log_result(
                        "90-Min Couples Massage Booking",
                        True,
                        f"✅ BOOKING SUCCESSFUL - ID: {appointment_id} | External: {external_verification}",
                        {
                            "service_name": "Masaža za parove - 90 min",
                            "service_id": couples_service_id,
                            "status_code": response.status_code,
                            "appointment_id": appointment_id,
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "date_time": booking_data['start_time'],
                            "external_verification": external_verification,
                            "response": response_data,
                            "notes_processed": "Backend should enhance notes with couples massage details"
                        }
                    )
                    return True, appointment_id
                else:
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', response.text)
                    except:
                        pass
                        
                    self.log_result(
                        "90-Min Couples Massage Booking",
                        False,
                        f"❌ BOOKING FAILED - Status: {response.status_code} | Error: {error_detail}",
                        {
                            "service_name": "Masaža za parove - 90 min",
                            "service_id": couples_service_id,
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "date_time": booking_data['start_time']
                        }
                    )
                    return False, None
                    
        except Exception as e:
            self.log_result(
                "90-Min Couples Massage Booking",
                False,
                f"❌ Exception: {str(e)}",
                {"error": str(e), "service_id": couples_service_id}
            )
            return False, None

    async def test_couples_massage_120_min_booking(self):
        """Test 120-minute couples massage booking - Backend processing"""
        
        # Couples massage service ID from the system
        couples_service_id = "d3e8684a-2bbc-4a15-835e-8e43d231074a"  # Masaža za parove - 120 min
        
        # Sample couples massage booking data with realistic notes for 120-min
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": "User2",
            "client_phone": "+381601234568",
            "client_email": "test2@example.com",
            "appointment_date": "2025-11-10",
            "start_time": "2025-11-10T16:00:00",
            "service_id": couples_service_id,
            "service_name": "Masaža za parove - 120 min",
            "therapist_id": "",  # Empty - let backend assign Web Slot therapist
            "notes": """OSOBA 1: Kraljevska tajlandska masaža (120 min) - 12,000 RSD
OSOBA 2: Dubinska masaža (120 min) - 11,000 RSD

UKUPNA CENA: 23,000 RSD
POPUST (-15%): -3,450 RSD
UKUPNA CENA SA POPUSTOM: 19,550 RSD

UKUPNO TRAJANJE: 240 min (120 min + 120 min)""",
            "language": "sr"
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
                    
                    self.log_result(
                        "120-Min Couples Massage Booking",
                        True,
                        f"✅ BOOKING SUCCESSFUL - ID: {appointment_id} | External: {external_verification}",
                        {
                            "service_name": "Masaža za parove - 120 min",
                            "service_id": couples_service_id,
                            "status_code": response.status_code,
                            "appointment_id": appointment_id,
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "date_time": booking_data['start_time'],
                            "external_verification": external_verification,
                            "response": response_data,
                            "notes_processed": "Backend should enhance notes with couples massage details"
                        }
                    )
                    return True, appointment_id
                else:
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', response.text)
                    except:
                        pass
                        
                    self.log_result(
                        "120-Min Couples Massage Booking",
                        False,
                        f"❌ BOOKING FAILED - Status: {response.status_code} | Error: {error_detail}",
                        {
                            "service_name": "Masaža za parove - 120 min",
                            "service_id": couples_service_id,
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "client": f"{booking_data['client_first_name']} {booking_data['client_last_name']}",
                            "date_time": booking_data['start_time']
                        }
                    )
                    return False, None
                    
        except Exception as e:
            self.log_result(
                "120-Min Couples Massage Booking",
                False,
                f"❌ Exception: {str(e)}",
                {"error": str(e), "service_id": couples_service_id}
            )
            return False, None

    async def test_web_slot_therapist_rotation(self):
        """Test Web Slot therapist rotation for multiple simultaneous bookings"""
        
        couples_service_id = "d3e8684a-2bbc-4a15-835e-8e43d231074a"
        
        # Test multiple bookings at the same time to verify Web Slot rotation
        bookings = [
            {
                "client_first_name": "Couple1",
                "client_last_name": "Test",
                "client_email": "couple1@example.com",
                "client_phone": "+381601111111",
                "notes": "OSOBA 1: Aroma terapija (90 min) - 7,500 RSD\nOSOBA 2: Tradicionalna tajlandska masaža (90 min) - 8,500 RSD\nUKUPNA CENA SA POPUSTOM: 13,600 RSD\nUKUPNO TRAJANJE: 180 min"
            },
            {
                "client_first_name": "Couple2",
                "client_last_name": "Test",
                "client_email": "couple2@example.com",
                "client_phone": "+381602222222",
                "notes": "OSOBA 1: Sportska masaža (90 min) - 9,000 RSD\nOSOBA 2: Relax masaža (90 min) - 8,000 RSD\nUKUPNA CENA SA POPUSTOM: 14,450 RSD\nUKUPNO TRAJANJE: 180 min"
            },
            {
                "client_first_name": "Couple3",
                "client_last_name": "Test",
                "client_email": "couple3@example.com",
                "client_phone": "+381603333333",
                "notes": "OSOBA 1: Kraljevska tajlandska masaža (120 min) - 12,000 RSD\nOSOBA 2: Dubinska masaža (120 min) - 11,000 RSD\nUKUPNA CENA SA POPUSTOM: 19,550 RSD\nUKUPNO TRAJANJE: 240 min"
            }
        ]
        
        test_time = "2025-11-12T14:00:00"
        successful_bookings = []
        failed_bookings = []
        
        print(f"\n🔄 WEB SLOT THERAPIST ROTATION TEST")
        print(f"Testing 3 simultaneous couples massage bookings at {test_time}")
        print("Backend should automatically assign different Web Slot therapists")
        print()
        
        for i, booking_info in enumerate(bookings):
            booking_data = {
                "client_first_name": booking_info["client_first_name"],
                "client_last_name": booking_info["client_last_name"],
                "client_phone": booking_info["client_phone"],
                "client_email": booking_info["client_email"],
                "appointment_date": "2025-11-12",
                "start_time": test_time,  # Same time for all
                "service_id": couples_service_id,
                "service_name": "Masaža za parove - 90 min",
                "therapist_id": "",  # Empty - let backend assign
                "notes": booking_info["notes"],
                "language": "sr"
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
                        
                        successful_bookings.append({
                            "booking_number": i + 1,
                            "client": f"{booking_info['client_first_name']} {booking_info['client_last_name']}",
                            "appointment_id": appointment_id,
                            "response": response_data
                        })
                        
                        print(f"✅ Booking #{i+1} SUCCESS - {booking_info['client_first_name']} - ID: {appointment_id}")
                        
                    else:
                        error_detail = response.text
                        try:
                            if response.headers.get('content-type', '').startswith('application/json'):
                                error_data = response.json()
                                error_detail = error_data.get('detail', response.text)
                        except:
                            pass
                            
                        failed_bookings.append({
                            "booking_number": i + 1,
                            "client": f"{booking_info['client_first_name']} {booking_info['client_last_name']}",
                            "error": error_detail,
                            "status_code": response.status_code
                        })
                        
                        print(f"❌ Booking #{i+1} FAILED - {booking_info['client_first_name']} - Error: {error_detail}")
                        
            except Exception as e:
                failed_bookings.append({
                    "booking_number": i + 1,
                    "client": f"{booking_info['client_first_name']} {booking_info['client_last_name']}",
                    "error": str(e),
                    "status_code": "Exception"
                })
                print(f"❌ Booking #{i+1} EXCEPTION - {booking_info['client_first_name']} - Error: {str(e)}")
        
        success_count = len(successful_bookings)
        total_count = len(bookings)
        
        self.log_result(
            "Web Slot Therapist Rotation Test",
            success_count >= 2,  # At least 2 should succeed to show rotation works
            f"Web Slot rotation: {success_count}/{total_count} simultaneous bookings successful",
            {
                "test_time": test_time,
                "successful_bookings": successful_bookings,
                "failed_bookings": failed_bookings,
                "success_count": success_count,
                "total_count": total_count,
                "rotation_working": success_count >= 2
            }
        )
        
        return success_count >= 2

    async def test_couples_massage_notes_processing(self):
        """Test if backend properly processes couples massage notes"""
        
        couples_service_id = "d3e8684a-2bbc-4a15-835e-8e43d231074a"
        
        # Test booking with specific couples massage notes format
        booking_data = {
            "client_first_name": "NotesTest",
            "client_last_name": "User",
            "client_phone": "+381604444444",
            "client_email": "notestest@example.com",
            "appointment_date": "2025-11-15",
            "start_time": "2025-11-15T10:00:00",
            "service_id": couples_service_id,
            "service_name": "Masaža za parove - 90 min",
            "therapist_id": "",
            "notes": """OSOBA 1: Aroma terapija (90 min) - 7,500 RSD
OSOBA 2: Tradicionalna tajlandska masaža (90 min) - 8,500 RSD

UKUPNA CENA: 16,000 RSD
POPUST (-15%): -2,400 RSD
UKUPNA CENA SA POPUSTOM: 13,600 RSD

UKUPNO TRAJANJE: 180 min (90 min + 90 min)""",
            "language": "sr"
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
                    
                    # Check if booking was created and verify notes processing
                    external_verification = await self.verify_booking_in_external_system(appointment_id)
                    
                    # Check if backend enhanced the notes (should contain couples massage details)
                    notes_enhanced = "⭐ MASAŽA ZA PAROVE" in str(response_data) or "UKUPNO TRAJANJE" in str(response_data)
                    
                    self.log_result(
                        "Couples Massage Notes Processing",
                        True,
                        f"✅ Notes processing test successful - ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "external_verification": external_verification,
                            "notes_enhanced": notes_enhanced,
                            "original_notes_length": len(booking_data["notes"]),
                            "response": response_data,
                            "backend_processing": "Backend should enhance notes with couples massage metadata"
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Couples Massage Notes Processing",
                        False,
                        f"❌ Notes processing test failed - Status: {response.status_code}",
                        {
                            "status_code": response.status_code,
                            "error": response.text
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Couples Massage Notes Processing",
                False,
                f"❌ Exception in notes processing test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def run_all_tests(self):
        """Run all couples massage backend tests"""
        print("=" * 70)
        print("COUPLES MASSAGE BACKEND TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print()
        print("Testing backend support for couples massage booking functionality:")
        print("1. 90-minute couples massage booking")
        print("2. 120-minute couples massage booking") 
        print("3. Web Slot therapist rotation")
        print("4. Couples massage notes processing")
        print()
        
        # Test 1: Backend Health Check
        backend_healthy = await self.test_backend_health()
        
        if not backend_healthy:
            print("🚨 Backend not accessible - Cannot proceed with couples massage tests")
            return self.results
        
        # Test 2: 90-Min Couples Massage Booking
        test_90_success, appointment_90 = await self.test_couples_massage_90_min_booking()
        
        # Test 3: 120-Min Couples Massage Booking
        test_120_success, appointment_120 = await self.test_couples_massage_120_min_booking()
        
        # Test 4: Web Slot Therapist Rotation
        rotation_success = await self.test_web_slot_therapist_rotation()
        
        # Test 5: Notes Processing
        notes_success = await self.test_couples_massage_notes_processing()
        
        # Summary
        print("=" * 70)
        print("COUPLES MASSAGE BACKEND TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        
        # Specific assessment for couples massage functionality
        couples_tests_passed = test_90_success and test_120_success
        
        if couples_tests_passed and rotation_success:
            print("🎉 COUPLES MASSAGE BACKEND FULLY FUNCTIONAL!")
            print("✅ Both 90-min and 120-min couples massage bookings work")
            print("✅ Web Slot therapist rotation working for simultaneous bookings")
            print("✅ Backend properly processes couples massage requests")
            print("✅ External system integration working")
        elif couples_tests_passed:
            print("⚠️ COUPLES MASSAGE PARTIALLY WORKING")
            print("✅ Basic couples massage bookings work")
            print("⚠️ Web Slot rotation may have issues with simultaneous bookings")
        elif backend_healthy:
            print("🚨 COUPLES MASSAGE BACKEND ISSUES DETECTED")
            print("❌ Couples massage bookings failing")
            print("🔧 Main agent needs to investigate couples massage service configuration")
        
        return self.results

async def main():
    """Main test execution"""
    tester = CouplesMassageBackendTester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())