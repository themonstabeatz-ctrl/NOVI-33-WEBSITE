#!/usr/bin/env python3
"""
Corrected Booking Test - Using actual service IDs from external system
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://gold-line-fixer.preview.emergentagent.com"

async def test_corrected_booking():
    """Test booking with correct service ID from external system"""
    
    print("🔍 Testing booking with CORRECT service ID from external system...")
    
    # Correct service ID from external system
    correct_service_id = "f3c55c37-5366-4be2-a47a-12322ef735fd"  # Tradicionalna tajlandska masaža - 60 min
    
    booking_data = {
        "client_first_name": "Test",
        "client_last_name": "Korisnik",
        "client_email": "test@example.com", 
        "client_phone": "+381641234567",
        "appointment_date": "2025-11-15",
        "start_time": "2025-11-15T14:00:00",
        "service_id": correct_service_id,
        "service_name": "Tradicionalna tajlandska masaža - 60 min",
        "notes": "Test booking with correct service ID",
        "therapist_id": "",
        "language": "sr"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/api/book-appointment",
                json=booking_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                appointment_id = response_data.get('id', 'N/A')
                print(f"✅ SUCCESS: Booking created with ID: {appointment_id}")
                
                # Verify in external system
                verify_response = await client.get(
                    f"https://pozdrav-kako-si.emergent.host/api/appointments/{appointment_id}"
                )
                if verify_response.status_code == 200:
                    print(f"✅ VERIFIED: Appointment found in external system")
                else:
                    print(f"⚠️ Cannot verify in external system: {verify_response.status_code}")
                
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

async def compare_service_endpoints():
    """Compare services from both endpoints to identify the mismatch"""
    
    print("🔍 Comparing service endpoints...")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Get services from backend proxy
            backend_response = await client.get(f"{BACKEND_URL}/api/services")
            backend_services = backend_response.json() if backend_response.status_code == 200 else []
            
            # Get services from external system directly
            external_response = await client.get("https://pozdrav-kako-si.emergent.host/api/services")
            external_services = external_response.json() if external_response.status_code == 200 else []
            
            print(f"Backend /api/services returned: {len(backend_services)} services")
            print(f"External system returned: {len(external_services)} services")
            
            # Find the target service in both
            target_service_name = "Tradicionalna tajlandska masaža - 60 min"
            
            backend_target = next((s for s in backend_services if s.get('name') == target_service_name), None)
            external_target = next((s for s in external_services if s.get('name') == target_service_name), None)
            
            print(f"\nTarget service: {target_service_name}")
            print(f"Backend service ID: {backend_target.get('id') if backend_target else 'NOT FOUND'}")
            print(f"External service ID: {external_target.get('id') if external_target else 'NOT FOUND'}")
            
            if backend_target and external_target:
                if backend_target['id'] != external_target['id']:
                    print(f"🚨 SERVICE ID MISMATCH DETECTED!")
                    print(f"   Backend returns: {backend_target['id']}")
                    print(f"   External has: {external_target['id']}")
                    print(f"   This is why bookings fail with 'Service not found'")
                else:
                    print(f"✅ Service IDs match")
            
            return backend_target, external_target
            
    except Exception as e:
        print(f"❌ Error comparing services: {str(e)}")
        return None, None

async def main():
    print("=" * 80)
    print("CORRECTED BOOKING TEST - SERVICE ID MISMATCH INVESTIGATION")
    print("=" * 80)
    
    # Compare service endpoints
    backend_service, external_service = await compare_service_endpoints()
    
    print("\n" + "=" * 80)
    
    # Test booking with correct service ID
    success = await test_corrected_booking()
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    if success:
        print("✅ Booking works when using correct service ID from external system")
        print("🔧 Issue: Backend /api/services returns wrong service IDs")
        print("🔧 Fix needed: Update service ID mapping in backend")
    else:
        print("❌ Booking still fails even with correct service ID")
        print("🔧 Additional investigation needed")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())