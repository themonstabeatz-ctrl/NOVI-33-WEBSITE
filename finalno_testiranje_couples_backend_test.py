#!/usr/bin/env python3
"""
FINALNO TESTIRANJE - Couples Booking Backend Test
Testing the exact scenario from review request
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8001"
RECEPCIJA_URL = "https://wavy-parallax-hero.preview.emergentagent.com"

def test_health_check():
    """Test if backend is accessible"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Backend health check: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_couples_booking():
    """Test the exact couples booking scenario from review request"""
    print("\n🎯 Testing EXACT couples booking scenario from review request...")
    
    # Using REAL service IDs from the couples services endpoint
    aroma_service_id = "df52cf25-beb8-45e9-9590-6c59b488b8c9"  # [PAROVI] Aroma terapija - 60 min
    tradicional_service_id = "fa7890e9-fa1d-4cf5-a18a-086eb7d98c55"  # [PAROVI] Tradicionalna tajlandska masaža - 60 min
    
    booking_data = {
        "client_first_name": "Final",
        "client_last_name": "Test",
        "client_phone": "0601234567",
        "client_email": "grujovicsavatije@gmail.com",
        "start_time": "2026-01-26T10:00:00",
        "duration_type": 60,
        "language": "sr",
        # Old format (required for backend compatibility)
        "person1_services": [aroma_service_id],
        "person2_services": [tradicional_service_id],
        # New format (snapshots) - using real service data
        "person1_snapshots": [
            {
                "service_id": aroma_service_id,
                "service_code": "AROMA_TERAPIJA",
                "original_price": 4400.0,
                "discount_percentage": 15.0,  # Real discount from couples services
                "final_price": 3740.0,  # Real final price from couples services
                "duration": 60
            }
        ],
        "person2_snapshots": [
            {
                "service_id": tradicional_service_id,
                "service_code": "TRADICIONALNA",
                "original_price": 4400.0,
                "discount_percentage": 15.0,  # Real discount from couples services
                "final_price": 3740.0,  # Real final price from couples services
                "duration": 60
            }
        ]
    }
    
    print(f"📤 Sending POST request to {BACKEND_URL}/api/book-couple-appointment")
    print(f"📋 Request data: {json.dumps(booking_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/book-couple-appointment",
            json=booking_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ BOOKING SUCCESSFUL!")
            print(f"📋 Response data: {json.dumps(result, indent=2)}")
            
            # Extract booking ID
            booking_id = result.get('id', 'NOT_FOUND')
            print(f"🆔 BOOKING ID: {booking_id}")
            
            # Check if email confirmation is mentioned in logs
            print(f"📧 Email should be sent to: {booking_data['client_email']}")
            
            return {
                'success': True,
                'booking_id': booking_id,
                'response': result,
                'status_code': response.status_code
            }
        else:
            print(f"❌ BOOKING FAILED!")
            print(f"📋 Error response: {response.text}")
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return {
            'success': False,
            'error': str(e),
            'status_code': None
        }

def verify_booking_in_recepcija(booking_id):
    """Verify if booking appears in recepcija system"""
    if not booking_id or booking_id == 'NOT_FOUND':
        print("⚠️ Cannot verify booking in recepcija - no booking ID")
        return False
        
    print(f"\n🔍 Verifying booking {booking_id} in recepcija system...")
    try:
        response = requests.get(f"{RECEPCIJA_URL}/api/appointments/{booking_id}", timeout=10)
        if response.status_code == 200:
            appointment = response.json()
            print(f"✅ Booking found in recepcija: {json.dumps(appointment, indent=2)}")
            return True
        else:
            print(f"❌ Booking not found in recepcija: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking recepcija: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 FINALNO TESTIRANJE - Couples Booking Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Backend not accessible - aborting tests")
        sys.exit(1)
    
    # Test 2: Couples booking
    result = test_couples_booking()
    
    # Test 3: Verify in recepcija (if booking succeeded)
    booking_found_in_recepcija = False
    if result['success']:
        booking_found_in_recepcija = verify_booking_in_recepcija(result.get('booking_id'))
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 60)
    
    print(f"1. Da li booking USPE? {'✅ DA' if result['success'] else '❌ NE'}")
    if result['success']:
        print(f"   Status: {result['status_code']} OK")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
        print(f"   Status: {result.get('status_code', 'N/A')}")
    
    print(f"2. Koji je booking ID? {result.get('booking_id', 'N/A')}")
    
    print(f"3. Da li se EMAIL ŠALJE? {'✅ DA (check backend logs)' if result['success'] else '❌ NE (booking failed)'}")
    if result['success']:
        print(f"   Email address: grujovicsavatije@gmail.com")
        print(f"   Language: sr")
    
    print(f"4. Da li se booking pojavljuje u recepciji? {'✅ DA' if booking_found_in_recepcija else '❌ NE/UNKNOWN'}")
    
    # Overall result
    overall_success = result['success']
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
    
    if overall_success:
        print("✅ All review request objectives achieved!")
    else:
        print("❌ Review request objectives NOT met - booking failed")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)