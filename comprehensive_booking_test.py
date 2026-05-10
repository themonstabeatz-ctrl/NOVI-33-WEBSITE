#!/usr/bin/env python3
"""
Comprehensive Booking Integration Test
Tests all service IDs with the backend proxy endpoint
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://wavy-parallax-hero.preview.emergentagent.com')

async def test_comprehensive_booking():
    """Test all service IDs with backend proxy"""
    
    # All service IDs provided by user
    services = [
        {"name": "Klasicna Tajlandska masaza", "id": "057c8535-bb25-4712-9014-60e378d06b6d"},
        {"name": "Relax masaža celog tela", "id": "e7ee5fb3-1688-41fb-9c74-a2e0d0b79fbf"},
        {"name": "Sportska masaža", "id": "d6cf94e7-5eac-4a8a-8a33-c92e18830021"},
        {"name": "Spa + tradicionalna tajlandska masaza", "id": "0483de92-b1ca-49d8-bd1d-0b8a39ed50a4"},
        {"name": "Dubinska masaža", "id": "4c135b02-641e-4f66-a13b-f420c89ff3bd"}
    ]
    
    therapist_id = "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f"  # Marko Markovic
    api_base = f"{BACKEND_URL}/api"
    
    print("=" * 80)
    print("COMPREHENSIVE BOOKING INTEGRATION TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing {len(services)} services with therapist: {therapist_id}")
    print()
    
    successful_bookings = []
    failed_bookings = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test backend health first
        try:
            health_response = await client.get(f"{api_base}/")
            if health_response.status_code != 200:
                print("❌ Backend health check failed!")
                return
            print("✅ Backend health check passed")
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return
        
        print()
        
        # Test each service
        for i, service in enumerate(services):
            # Use different dates to avoid conflicts
            test_date = f"2025-07-{10+i:02d}"
            test_time = f"{test_date}T{10+i}:00:00"
            
            booking_data = {
                "client_first_name": "Comprehensive",
                "client_last_name": "Test",
                "client_phone": "+381621234567",
                "client_email": f"comprehensive.test.{i+1}@example.com",
                "appointment_date": test_date,
                "start_time": test_time,
                "service_id": service["id"],
                "therapist_id": therapist_id,
                "notes": f"Comprehensive test for {service['name']}"
            }
            
            print(f"Testing: {service['name']}")
            print(f"  Service ID: {service['id']}")
            print(f"  Date/Time: {test_date} at {test_time}")
            
            try:
                response = await client.post(
                    f"{api_base}/book-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    appointment_id = response_data.get('id', 'N/A')
                    end_time = response_data.get('end_time', 'N/A')
                    
                    successful_bookings.append({
                        "service": service["name"],
                        "service_id": service["id"],
                        "appointment_id": appointment_id,
                        "start_time": test_time,
                        "end_time": end_time
                    })
                    
                    print(f"  ✅ SUCCESS - Appointment ID: {appointment_id}")
                    print(f"     End time: {end_time}")
                    
                else:
                    failed_bookings.append({
                        "service": service["name"],
                        "service_id": service["id"],
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    
                    print(f"  ❌ FAILED - Status: {response.status_code}")
                    print(f"     Error: {response.text}")
                    
            except Exception as e:
                failed_bookings.append({
                    "service": service["name"],
                    "service_id": service["id"],
                    "error": str(e)
                })
                print(f"  ❌ ERROR - {str(e)}")
            
            print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_services = len(services)
    successful_count = len(successful_bookings)
    failed_count = len(failed_bookings)
    
    print(f"Total Services Tested: {total_services}")
    print(f"Successful Bookings: {successful_count}")
    print(f"Failed Bookings: {failed_count}")
    print(f"Success Rate: {(successful_count/total_services)*100:.1f}%")
    print()
    
    if successful_bookings:
        print("✅ SUCCESSFUL BOOKINGS:")
        for booking in successful_bookings:
            print(f"  • {booking['service']}")
            print(f"    ID: {booking['appointment_id']}")
            print(f"    Time: {booking['start_time']} - {booking['end_time']}")
        print()
    
    if failed_bookings:
        print("❌ FAILED BOOKINGS:")
        for booking in failed_bookings:
            print(f"  • {booking['service']}")
            if 'status_code' in booking:
                print(f"    Status: {booking['status_code']}")
            print(f"    Error: {booking['error']}")
        print()
    
    # Final verdict
    if successful_count == total_services:
        print("🎉 ALL BOOKING TESTS PASSED - Complete integration working!")
    elif successful_count > 0:
        print(f"✅ PARTIAL SUCCESS - {successful_count}/{total_services} services working")
    else:
        print("🚨 ALL BOOKING TESTS FAILED")
    
    return {
        "total": total_services,
        "successful": successful_count,
        "failed": failed_count,
        "successful_bookings": successful_bookings,
        "failed_bookings": failed_bookings
    }

if __name__ == "__main__":
    asyncio.run(test_comprehensive_booking())