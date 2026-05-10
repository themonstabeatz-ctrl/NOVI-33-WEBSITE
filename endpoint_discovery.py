#!/usr/bin/env python3
"""
Endpoint Discovery for Thai Massage Booking System
"""

import asyncio
import httpx
import json

async def test_endpoints():
    """Test various possible endpoints"""
    base_url = "https://wavy-parallax-hero.preview.emergentagent.com"
    
    endpoints_to_test = [
        "/api",
        "/api/",
        "/api/appointments",
        "/api/bookings", 
        "/api/book",
        "/api/reservation",
        "/api/reservations",
        "/appointments",
        "/bookings",
        "/book",
        "/health",
        "/status"
    ]
    
    print("Testing endpoints on:", base_url)
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                # Test GET first
                response = await client.get(url)
                print(f"GET {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"   Response: {response.text[:100]}...")
                elif response.status_code == 405:  # Method not allowed, try POST
                    try:
                        post_response = await client.post(url, json={})
                        print(f"POST {endpoint}: {post_response.status_code}")
                        if post_response.status_code != 404:
                            print(f"   Response: {post_response.text[:100]}...")
                    except:
                        pass
                        
            except Exception as e:
                print(f"GET {endpoint}: ERROR - {str(e)}")
            
            print()

if __name__ == "__main__":
    asyncio.run(test_endpoints())