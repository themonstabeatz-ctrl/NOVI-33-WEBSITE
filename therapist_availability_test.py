#!/usr/bin/env python3
"""
Test different therapists and times to understand availability issues
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://gold-line-fixer.preview.emergentagent.com')

async def test_therapist_availability():
    api_base = f"{BACKEND_URL}/api"
    
    # Test different therapists
    therapists = [
        {"name": "Marko Markovic", "id": "4cd2ce85-3e9e-41cd-83fc-81a4a48dda2f"},
        {"name": "Ana Petrovic", "id": "24ed3b3a-c6af-4a77-b19d-0961fc554c69"},
        {"name": "Kanokon Sawee", "id": "0304d64f-bee7-4cf6-8ed8-9e0cde58b312"}
    ]
    
    # Test different times on the same date
    test_times = [
        "2025-11-02T10:00:00",  # 10:00 AM
        "2025-11-02T12:00:00",  # 12:00 PM  
        "2025-11-02T14:00:00",  # 2:00 PM (user's time)
        "2025-11-02T16:00:00",  # 4:00 PM
        "2025-11-02T18:00:00"   # 6:00 PM
    ]
    
    # Use one service for testing
    service_id = "114600d6-3960-41e4-b453-32012cb6400a"  # Partnerska masaža - 120 min
    
    print("🔍 THERAPIST AVAILABILITY TEST")
    print("=" * 60)
    print(f"Testing service: Partnerska masaža - 120 min")
    print(f"Date: 2025-11-02 (November 2, 2025)")
    print()
    
    for therapist in therapists:
        print(f"👨‍⚕️ Testing therapist: {therapist['name']}")
        
        for test_time in test_times:
            booking_data = {
                "client_first_name": "Test",
                "client_last_name": "Client",
                "client_phone": "+381621234567",
                "client_email": "test@example.com",
                "appointment_date": "2025-11-02",
                "start_time": test_time,
                "service_id": service_id,
                "therapist_id": therapist["id"],
                "notes": "Availability test"
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{api_base}/book-appointment",
                        json=booking_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    time_str = test_time.split('T')[1][:5]  # Extract HH:MM
                    
                    if response.status_code in [200, 201]:
                        response_data = response.json()
                        appointment_id = response_data.get('id', 'N/A')
                        print(f"  ✅ {time_str}: SUCCESS - Appointment ID: {appointment_id}")
                    elif response.status_code == 400:
                        try:
                            error_detail = response.json().get('detail', '')
                        except:
                            error_detail = response.text
                        print(f"  ❌ {time_str}: 400 - {error_detail}")
                    else:
                        print(f"  ⚠️ {time_str}: {response.status_code} - {response.text[:50]}")
                        
            except Exception as e:
                print(f"  ❌ {time_str}: Exception - {str(e)}")
        
        print()

async def main():
    await test_therapist_availability()

if __name__ == "__main__":
    asyncio.run(main())