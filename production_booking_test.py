#!/usr/bin/env python3
"""
PRODUCTION BOOKING FLOW TEST - Thai Spa Booking System
Testing complete booking flow on PRODUCTION: https://thai-spa-booking.emergent.host

Test scenarios from review request:
1. Single Massage Booking
2. Couples Massage Booking

CRITICAL VERIFICATION POINTS:
- Does booking succeed? (200 OK)
- Does it return booking ID?
- IS EMAIL SENT? (check response message)
- If NO - what is the EXACT error?
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Production URL from review request
PRODUCTION_URL = "https://thai-spa-booking.emergent.host"

def test_health_check():
    """Test if backend is accessible"""
    print("🔍 TESTING BACKEND HEALTH CHECK...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/health", timeout=10)
        print(f"Health Check Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_single_massage_booking():
    """
    Test Scenario 1 - Single Massage Booking
    Exact payload from review request
    """
    print("\n" + "="*60)
    print("🎯 TEST SCENARIO 1 - SINGLE MASSAGE BOOKING")
    print("="*60)
    
    # Exact payload from review request
    booking_payload = {
        "client_first_name": "Test",
        "client_last_name": "Korisnik",
        "client_phone": "0601234567",
        "client_email": "test@example.com",
        "appointment_date": "2025-12-10",
        "start_time": "2025-12-10T14:00:00",
        "service_id": "98249336-b9d9-4685-b70c-81971d3cf216",
        "service_name": "Tradicionalna tajlandska masaža - 60 min",
        "therapist_id": "1490364f-31c8-49a6-a370-2e19fed34e81",
        "notes": "Test booking",
        "language": "sr"
    }
    
    print(f"📤 Sending booking request to: {PRODUCTION_URL}/api/book-appointment")
    print(f"📋 Payload: {json.dumps(booking_payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/api/book-appointment",
            json=booking_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📊 RESPONSE STATUS: {response.status_code}")
        print(f"📄 RESPONSE HEADERS: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS! Response data: {json.dumps(data, indent=2)}")
                
                # Check for booking ID
                booking_id = data.get('id') or data.get('appointment_id') or data.get('booking_id')
                if booking_id:
                    print(f"✅ BOOKING ID RETURNED: {booking_id}")
                else:
                    print(f"⚠️ NO BOOKING ID FOUND in response")
                
                # Check for email confirmation message
                response_text = json.dumps(data).lower()
                if 'email' in response_text or 'confirmation' in response_text or 'sent' in response_text:
                    print(f"✅ EMAIL CONFIRMATION DETECTED in response")
                else:
                    print(f"⚠️ NO EMAIL CONFIRMATION MESSAGE found")
                
                return True, data
                
            except json.JSONDecodeError:
                print(f"✅ SUCCESS! Response (non-JSON): {response.text}")
                return True, response.text
        else:
            print(f"❌ BOOKING FAILED!")
            print(f"📄 Error Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"📋 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
            return False, response.text
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False, str(e)

def test_couples_massage_booking():
    """
    Test Scenario 2 - Couples Massage Booking
    First load couples services, then book
    """
    print("\n" + "="*60)
    print("🎯 TEST SCENARIO 2 - COUPLES MASSAGE BOOKING")
    print("="*60)
    
    # Step 1: Load couples services
    print("📋 STEP 1: Loading couples services...")
    try:
        services_response = requests.get(
            f"{PRODUCTION_URL}/api/services/couples/list",
            timeout=10
        )
        
        print(f"Services API Status: {services_response.status_code}")
        
        if services_response.status_code == 200:
            services = services_response.json()
            print(f"✅ Loaded {len(services)} couples services")
            
            # Show first few services
            for i, service in enumerate(services[:3]):
                print(f"  Service {i+1}: {service.get('name', 'N/A')} (ID: {service.get('id', 'N/A')})")
        else:
            print(f"❌ Failed to load couples services: {services_response.text}")
            return False, "Failed to load couples services"
            
    except Exception as e:
        print(f"❌ Error loading couples services: {str(e)}")
        return False, str(e)
    
    # Step 2: Book couples massage with exact payload from review request
    print("\n📋 STEP 2: Booking couples massage...")
    
    # Exact payload from review request
    couples_payload = {
        "client_first_name": "Test",
        "client_last_name": "Korisnik",
        "client_phone": "0601234567",
        "client_email": "test@example.com",
        "start_time": "2025-12-11T15:00:00",
        "duration_type": 60,
        "language": "sr",
        "person1_snapshots": [
            {
                "service_id": "38104bdc-d738-474f-beee-0d6ffbbd7707",
                "service_code": "Aroma terapija",
                "original_price": 4400.0,
                "discount_percentage": 10.0,
                "final_price": 3960.0,
                "duration": 60
            }
        ],
        "person2_snapshots": [
            {
                "service_id": "6a6e2ed3-cd9d-4d4f-aa57-d1f221dcdc76",
                "service_code": "Tradicionalna tajlandska masaža",
                "original_price": 4400.0,
                "discount_percentage": 10.0,
                "final_price": 3960.0,
                "duration": 60
            }
        ]
    }
    
    print(f"📤 Sending couples booking request to: {PRODUCTION_URL}/api/book-couple-appointment")
    print(f"📋 Payload: {json.dumps(couples_payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/api/book-couple-appointment",
            json=couples_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📊 RESPONSE STATUS: {response.status_code}")
        print(f"📄 RESPONSE HEADERS: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS! Response data: {json.dumps(data, indent=2)}")
                
                # Check for booking ID
                booking_id = data.get('id') or data.get('appointment_id') or data.get('booking_id')
                if booking_id:
                    print(f"✅ BOOKING ID RETURNED: {booking_id}")
                else:
                    print(f"⚠️ NO BOOKING ID FOUND in response")
                
                # Check for email confirmation message
                response_text = json.dumps(data).lower()
                if 'email' in response_text or 'confirmation' in response_text or 'sent' in response_text:
                    print(f"✅ EMAIL CONFIRMATION DETECTED in response")
                else:
                    print(f"⚠️ NO EMAIL CONFIRMATION MESSAGE found")
                
                return True, data
                
            except json.JSONDecodeError:
                print(f"✅ SUCCESS! Response (non-JSON): {response.text}")
                return True, response.text
        else:
            print(f"❌ COUPLES BOOKING FAILED!")
            print(f"📄 Error Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"📋 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
            return False, response.text
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False, str(e)

def check_therapists_endpoint():
    """Check if /api/therapists endpoint exists (mentioned in review request)"""
    print("\n" + "="*60)
    print("🔍 CHECKING THERAPISTS ENDPOINT")
    print("="*60)
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/therapists", timeout=10)
        print(f"Therapists API Status: {response.status_code}")
        
        if response.status_code == 200:
            therapists = response.json()
            print(f"✅ Found {len(therapists)} therapists")
            
            # Show first few therapists
            for i, therapist in enumerate(therapists[:3]):
                print(f"  Therapist {i+1}: {therapist.get('name', 'N/A')} (ID: {therapist.get('id', 'N/A')})")
            return True
        else:
            print(f"❌ Therapists endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking therapists: {str(e)}")
        return False

def main():
    """Run all production tests"""
    print("🚀 STARTING PRODUCTION BOOKING FLOW TESTS")
    print(f"🎯 Target URL: {PRODUCTION_URL}")
    print(f"🕐 Test Time: {datetime.now().isoformat()}")
    
    results = {
        'health_check': False,
        'single_booking': False,
        'couples_booking': False,
        'therapists_check': False
    }
    
    # Test 1: Health Check
    results['health_check'] = test_health_check()
    
    # Test 2: Check therapists endpoint
    results['therapists_check'] = check_therapists_endpoint()
    
    # Test 3: Single massage booking
    single_success, single_data = test_single_massage_booking()
    results['single_booking'] = single_success
    
    # Test 4: Couples massage booking
    couples_success, couples_data = test_couples_massage_booking()
    results['couples_booking'] = couples_success
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED - CHECK DETAILS ABOVE")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)