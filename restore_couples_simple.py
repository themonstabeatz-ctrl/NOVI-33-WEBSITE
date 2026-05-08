#!/usr/bin/env python3
"""
Script to restore the simple couples massage services (60, 90, 120 min).
These are used as service_ids in Contact.js for the CouplesMassageCard bookings.
The actual total duration (180 or 240 min) is passed via duration_type parameter.
"""

import httpx
import asyncio

BOOKING_API_BASE = 'https://pozdrav-kako-si.emergent.host/api'

# Service IDs expected by Contact.js (currently pointing to Sportska masaža IDs)
# We need to create proper "Masaža za parove" services
COUPLES_60_EXPECTED = "3fe475c2-19be-48f6-bebc-0144feecaf94"
COUPLES_90_EXPECTED = "2c389b61-b655-4d74-a254-469a28d3f32a"
COUPLES_120_EXPECTED = "d3e8684a-2bbc-4a15-835e-8e43d231074a"

# These are "base" prices for reference - actual price calculated by frontend with 15% discount
# For 60 min mode: Each person picks 60 min massage
# For 90 min mode: Each person picks 90 min massage (total 180 min)
# For 120 min mode: Each person picks 2x60 min OR 1x120 min massage (total 240 min)

# Approximate prices (will vary based on actual massage selections)
COUPLES_60_PRICE = 8330   # ~2 * 4900 * 0.85 (60 min each)
COUPLES_90_PRICE = 9520   # ~2 * 5600 * 0.85 (90 min each)
COUPLES_120_PRICE = 11560 # ~2 * 6800 * 0.85 (120 min each)


async def create_service(name: str, duration: int, price: int):
    """Create a new service in the booking system"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "name": name,
                "duration": duration,
                "price": float(price),
                "description": "Masaža za parove - dve osobe sa popustom od 15%"
            }
            
            response = await client.post(
                f'{BOOKING_API_BASE}/services',
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            actual_id = result.get('id')
            print(f"✓ Created: {name}")
            print(f"  ID: {actual_id}")
            print(f"  Price: {price} RSD")
            return actual_id
        except httpx.HTTPStatusError as e:
            print(f"✗ Error creating {name}: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"  Detail: {error_detail}")
            except:
                print(f"  Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"✗ Error creating {name}: {e}")
            return None


async def main():
    print("=" * 80)
    print("RESTORING COUPLES MASSAGE SERVICES (SIMPLE 60/90/120 MIN)")
    print("=" * 80)
    print("\nThese services are used by CouplesMassageCard.")
    print("The actual total duration (180/240 min) is sent via duration_type parameter.\n")
    
    service_ids = {}
    
    # Create 60 min service
    print("\n[1/3] Creating 'Masaža za parove - 60 min'...")
    service_ids['60'] = await create_service(
        name="Masaža za parove - 60 min",
        duration=60,
        price=COUPLES_60_PRICE
    )
    
    # Create 90 min service
    print("\n[2/3] Creating 'Masaža za parove - 90 min'...")
    service_ids['90'] = await create_service(
        name="Masaža za parove - 90 min",
        duration=90,
        price=COUPLES_90_PRICE
    )
    
    # Create 120 min service
    print("\n[3/3] Creating 'Masaža za parove - 120 min'...")
    service_ids['120'] = await create_service(
        name="Masaža za parove - 120 min",
        duration=120,
        price=COUPLES_120_PRICE
    )
    
    print("\n" + "=" * 80)
    print("COUPLES MASSAGE SERVICES RESTORED")
    print("=" * 80)
    
    # Show serviceMapping updates
    print("\n📋 UPDATE Contact.js serviceMapping:")
    print("-" * 80)
    if service_ids.get('60'):
        print(f'  "Masaža za parove - 60 min": "{service_ids["60"]}",')
    if service_ids.get('90'):
        print(f'  "Masaža za parove - 90 min": "{service_ids["90"]}",')
    if service_ids.get('120'):
        print(f'  "Masaža za parove - 120 min": "{service_ids["120"]}",')
    print("-" * 80)
    
    print("\n⚠️ IMPORTANT:")
    print("  Update Contact.js serviceMapping with the new IDs above.")
    print("  Also DELETE these entries (they were for 180/240 min):")
    print('    - "Masaža za parove - 180 min"')
    print('    - "Masaža za parove - 240 min"')


if __name__ == "__main__":
    asyncio.run(main())
