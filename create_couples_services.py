#!/usr/bin/env python3
"""
Script to create all massage services in "Kartica Masaza za parove" category
"""
import httpx
import json
import asyncio

BOOKING_API = "https://pozdrav-kako-si.emergent.host"

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
            print(f"❌ Failed to create {service_data['name']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating {service_data['name']}: {str(e)}")
        return False

async def main():
    # Load existing services
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BOOKING_API}/api/services")
        existing_services = response.json()
    
    # Group services by base name
    services_by_name = {}
    for s in existing_services:
        name = s['name']
        if ' - ' in name:
            base_name = ' - '.join(name.split(' - ')[:-1])
            duration = name.split(' - ')[-1].replace(' min', '').strip()
            
            if base_name not in services_by_name:
                services_by_name[base_name] = {}
            
            services_by_name[base_name][duration] = {
                'price': s['price'],
                'description': s.get('description', ''),
                'duration': int(duration)
            }
    
    # Create services for "Kartica Masaza za parove" category
    services_to_create = []
    
    for base_name, durations in sorted(services_by_name.items()):
        for duration in ['60', '90', '120']:
            if duration in durations:
                service_data = {
                    'name': f"{base_name} - {duration} min",
                    'description': durations[duration]['description'] or f"{base_name} tretman u trajanju od {duration} minuta",
                    'duration': int(duration),
                    'price': durations[duration]['price'],
                    'category': 'Kartica Masaza za parove',
                    'discount_percentage': 0  # Default 0%, can be changed from booking system
                }
                services_to_create.append(service_data)
    
    print(f"\n📋 Creating {len(services_to_create)} services in 'Kartica Masaza za parove' category...\n")
    
    # Create services
    success_count = 0
    fail_count = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for service in services_to_create:
            result = await create_service(client, service)
            if result:
                success_count += 1
            else:
                fail_count += 1
            await asyncio.sleep(0.1)  # Small delay to avoid overwhelming the API
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successfully created: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📋 Total: {len(services_to_create)}")
    print(f"{'='*60}\n")
    
    # Verify by counting services in the category
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BOOKING_API}/api/services")
        all_services = response.json()
        couples_services = [s for s in all_services if s.get('category') == 'Kartica Masaza za parove']
        print(f"✅ Verified: {len(couples_services)} services now exist in 'Kartica Masaza za parove' category")

if __name__ == "__main__":
    asyncio.run(main())
