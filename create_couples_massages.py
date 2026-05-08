#!/usr/bin/env python3
"""
Create massage services with [PAROVI] prefix for couples massage card
"""
import httpx
import asyncio

BOOKING_API = "https://pozdrav-kako-si.emergent.host"

# Exact massages as provided by user
MASSAGES = [
    {
        "name": "Tradicionalna tajlandska masaža",
        "durations": {
            "60": {"price": 4400, "desc": "Tradicionalna tajlandska masaža u trajanju od 60 minuta"},
            "90": {"price": 5600, "desc": "Tradicionalna tajlandska masaža u trajanju od 90 minuta"},
            "120": {"price": 6800, "desc": "Tradicionalna tajlandska masaža u trajanju od 120 minuta"}
        }
    },
    {
        "name": "Aroma terapija",
        "durations": {
            "60": {"price": 4400, "desc": "Aroma terapija u trajanju od 60 minuta"},
            "90": {"price": 5600, "desc": "Aroma terapija u trajanju od 90 minuta"},
            "120": {"price": 6800, "desc": "Aroma terapija u trajanju od 120 minuta"}
        }
    },
    {
        "name": "Masaža toplim uljem",
        "durations": {
            "60": {"price": 4600, "desc": "Masaža toplim uljem u trajanju od 60 minuta"},
            "90": {"price": 5800, "desc": "Masaža toplim uljem u trajanju od 90 minuta"}
        }
    },
    {
        "name": "Glava, vrat, ramena i leđa",
        "durations": {
            "60": {"price": 3900, "desc": "Masaža glave, vrata, ramena i leđa u trajanju od 60 minuta"}
        }
    },
    {
        "name": "Masaža stopala",
        "durations": {
            "60": {"price": 3500, "desc": "Masaža stopala u trajanju od 60 minuta"}
        }
    }
]

async def create_service(client, service_data):
    """Create a single service"""
    try:
        response = await client.post(
            f"{BOOKING_API}/api/services",
            json=service_data
        )
        if response.status_code in [200, 201]:
            print(f"✅ Created: {service_data['name']}")
            return True
        else:
            print(f"❌ Failed: {service_data['name']} - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {service_data['name']} - {str(e)}")
        return False

async def main():
    print("📋 Creating massage services with [PAROVI] prefix...\n")
    
    services_to_create = []
    
    for massage in MASSAGES:
        for duration, info in massage["durations"].items():
            service_data = {
                "name": f"[PAROVI] {massage['name']} - {duration} min",
                "description": info["desc"],
                "duration": int(duration),
                "price": info["price"],
                "discount_percentage": 0
            }
            services_to_create.append(service_data)
    
    print(f"Total services to create: {len(services_to_create)}\n")
    
    # Create services
    success = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for service in services_to_create:
            result = await create_service(client, service)
            if result:
                success += 1
            else:
                failed += 1
            await asyncio.sleep(0.2)
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   ✅ Success: {success}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📋 Total: {len(services_to_create)}")
    print(f"{'='*60}\n")
    
    # Verify
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BOOKING_API}/api/services")
        all_services = response.json()
        parovi_services = [s for s in all_services if s['name'].startswith('[PAROVI]')]
        print(f"✅ Verified: {len(parovi_services)} services with [PAROVI] prefix exist\n")
        
        # Show them
        if parovi_services:
            print("📋 Created services:")
            for s in parovi_services:
                print(f"   - {s['name']} ({s['price']} RSD)")

if __name__ == "__main__":
    asyncio.run(main())
