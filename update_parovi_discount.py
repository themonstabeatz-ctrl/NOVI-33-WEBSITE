#!/usr/bin/env python3
"""
Script to update discount for [PAROVI] services
Usage: python3 update_parovi_discount.py <discount_percentage>
Example: python3 update_parovi_discount.py 15
"""
import httpx
import asyncio
import sys

BOOKING_API = "https://pozdrav-kako-si.emergent.host"

async def update_discount(discount_percent):
    """Update discount for all [PAROVI] services"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get all services
        response = await client.get(f"{BOOKING_API}/api/services")
        services = response.json()
        
        # Filter [PAROVI] services
        parovi_services = [s for s in services if s['name'].startswith('[PAROVI]')]
        
        print(f"📋 Found {len(parovi_services)} [PAROVI] services")
        print(f"🎯 Setting discount to {discount_percent}%\n")
        
        success = 0
        failed = 0
        
        for service in parovi_services:
            try:
                # Try to update via PATCH/PUT
                service_data = {
                    'name': service['name'],
                    'description': service['description'],
                    'duration': service['duration'],
                    'price': service['price'],
                    'discount_percentage': discount_percent
                }
                
                response = await client.put(
                    f"{BOOKING_API}/api/services/{service['id']}",
                    json=service_data
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Updated: {service['name']}")
                    success += 1
                else:
                    print(f"❌ Failed: {service['name']} - {response.status_code}")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Error: {service['name']} - {str(e)}")
                failed += 1
            
            await asyncio.sleep(0.1)
        
        print(f"\n{'='*60}")
        print(f"📊 SUMMARY:")
        print(f"   ✅ Success: {success}")
        print(f"   ❌ Failed: {failed}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 update_parovi_discount.py <discount_percentage>")
        print("Example: python3 update_parovi_discount.py 15")
        sys.exit(1)
    
    discount = int(sys.argv[1])
    asyncio.run(update_discount(discount))
