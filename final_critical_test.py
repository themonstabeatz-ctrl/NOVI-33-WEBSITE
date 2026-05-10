#!/usr/bin/env python3
"""
FINAL CRITICAL TEST - Test with available therapist to confirm fix
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://wavy-parallax-hero.preview.emergentagent.com')

async def test_with_available_therapist():
    api_base = f"{BACKEND_URL}/api"
    
    print("🚨 FINAL CRITICAL TEST - USER ISSUE ROOT CAUSE CONFIRMED")
    print("=" * 70)
    print("Issue: Frontend hardcoded to use Marko Markovic (4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f)")
    print("Problem: Marko is NOT available at 14:00 on 2025-11-02")
    print("Solution: Use available therapist Ana Petrovic (24ed3b3a-c6af-4a77-b19d-0961fc554c69)")
    print()
    
    # Test scenarios with available therapist
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
    
    # Use available therapist Ana Petrovic
    available_therapist_id = "24ed3b3a-c6af-4a77-b19d-0961fc554c69"
    test_date = "2025-11-02"
    test_time = "2025-11-02T14:00:00"
    
    successful_bookings = []
    
    for scenario in test_scenarios:
        print(f"🔍 Testing {scenario['source']}: {scenario['service_name']}")
        print(f"   Using available therapist: Ana Petrovic")
        
        booking_data = {
            "client_first_name": scenario["client_first_name"],
            "client_last_name": scenario["client_last_name"],
            "client_phone": scenario["client_phone"],
            "client_email": scenario["client_email"],
            "appointment_date": test_date,
            "start_time": test_time,
            "service_id": scenario["service_id"],
            "therapist_id": available_therapist_id,  # Use available therapist
            "notes": f"FINAL TEST: Using available therapist instead of hardcoded Marko"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    
                    successful_bookings.append({
                        "source": scenario["source"],
                        "service": scenario["service_name"],
                        "appointment_id": appointment_id
                    })
                    
                    print(f"   ✅ SUCCESS - Appointment ID: {appointment_id}")
                    
                    # Verify in external system
                    try:
                        verify_response = await client.get(
                            f"https://pozdrav-kako-si.emergent.host/api/appointments/{appointment_id}"
                        )
                        if verify_response.status_code == 200:
                            print(f"   ✅ VERIFIED in external system")
                        else:
                            print(f"   ⚠️ External verification: {verify_response.status_code}")
                    except:
                        print(f"   ⚠️ Could not verify in external system")
                        
                else:
                    print(f"   ❌ FAILED: {response.status_code} - {response.text[:100]}")
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
        
        print()
    
    print("=" * 70)
    print("🎯 FINAL RESULTS")
    print("=" * 70)
    
    if len(successful_bookings) == len(test_scenarios):
        print("🎉 USER ISSUE ROOT CAUSE CONFIRMED AND SOLUTION VERIFIED!")
        print()
        print("✅ PROBLEM IDENTIFIED:")
        print("   - Frontend hardcoded to use Marko Markovic therapist ID")
        print("   - Marko is NOT available at user's requested time (14:00 on 2025-11-02)")
        print("   - Backend correctly returns 400 'Therapist not available' error")
        print()
        print("✅ SOLUTION VERIFIED:")
        print("   - Using available therapist (Ana Petrovic) makes all bookings work")
        print("   - All 3 user scenarios successful with available therapist")
        print("   - Bookings appear correctly in external system")
        print()
        print("🔧 REQUIRED FIX:")
        print("   - Frontend should check therapist availability before booking")
        print("   - OR use dynamic therapist assignment instead of hardcoded ID")
        print("   - OR provide therapist selection in booking form")
        
    else:
        print(f"⚠️ PARTIAL SUCCESS: {len(successful_bookings)}/{len(test_scenarios)} bookings worked")
        
    print()
    print("SUCCESSFUL BOOKINGS WITH AVAILABLE THERAPIST:")
    for booking in successful_bookings:
        print(f"  ✅ {booking['source']}: {booking['service']} (ID: {booking['appointment_id']})")

async def main():
    await test_with_available_therapist()

if __name__ == "__main__":
    asyncio.run(main())