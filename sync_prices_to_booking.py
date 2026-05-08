#!/usr/bin/env python3
"""
Script to sync frontend service prices to the external booking system.
- Fetches all services from booking system
- Compares with frontend prices
- Updates prices in booking system
- Deletes unused services
"""

import httpx
import asyncio
import json

BOOKING_API_BASE = 'https://pozdrav-kako-si.emergent.host/api'

# Define all correct prices from frontend (in RSD, without discounts)
# Format: "Service Name - Duration": price_in_rsd
CORRECT_PRICES = {
    # Tradicionalna tajlandska masaža
    "Tradicionalna tajlandska masaža - 60 min": 4400,
    "Tradicionalna tajlandska masaža - 90 min": 5600,
    "Tradicionalna tajlandska masaža - 120 min": 6800,
    
    # Aroma terapija
    "Aroma terapija - 60 min": 4400,
    "Aroma terapija - 90 min": 5600,
    "Aroma terapija - 120 min": 6800,
    
    # Masaža toplim uljem (Hot Stone)
    "Masaža toplim uljem - 60 min": 4600,
    "Masaža toplim uljem - 90 min": 5800,
    # No 120 min option
    
    # Glava, vrat, ramena i leđa (Royal)
    "Glava, vrat, ramena i leđa - 30 min": 2400,
    "Glava, vrat, ramena i leđa - 45 min": 3200,
    "Glava, vrat, ramena i leđa - 60 min": 3900,
    
    # Masaža stopala (Foot)
    "Masaža stopala - 30 min": 2400,
    "Masaža stopala - 45 min": 2900,
    "Masaža stopala - 60 min": 3500,
    
    # Masaža za parove - Simple version (not the complex CouplesMassageCard)
    # Note: CouplesMassageCard has its own pricing logic with 15% discount
    # "Masaža za parove - 60 min": 4900,
    # "Masaža za parove - 90 min": 6000,
    
    # Masaža za parove - Complex version with specific durations
    "Masaža za parove - 180 min": 10200,  # 2 people * 90 min * 0.85 discount
    "Masaža za parove - 240 min": 13600,  # 2 people * 120 min * 0.85 discount
    
    # Sportska masaža
    "Sportska masaža - 60 min": 3000,
    "Sportska masaža - 90 min": 4000,
    "Sportska masaža - 120 min": 5000,
    
    # Shiatsu masaža
    "Shiatsu masaža - 60 min": 3000,
    "Shiatsu masaža - 90 min": 4000,
    "Shiatsu masaža - 120 min": 5000,
    
    # Refleksologija
    "Refleksologija - 60 min": 3000,
    "Refleksologija - 90 min": 4000,
    "Refleksologija - 120 min": 5000,
    
    # Masaža leđa i vrata
    "Masaža leđa i vrata - 60 min": 3000,
    "Masaža leđa i vrata - 90 min": 4000,
    "Masaža leđa i vrata - 120 min": 5000,
    
    # Antistres masaža
    "Antistres masaža - 60 min": 3000,
    "Antistres masaža - 90 min": 4000,
    "Antistres masaža - 120 min": 5000,
    
    # Prenatalna masaža
    "Prenatalna masaža - 60 min": 3000,
    "Prenatalna masaža - 90 min": 4000,
    "Prenatalna masaža - 120 min": 5000,
    
    # Masaža dubokih tkiva
    "Masaža dubokih tkiva - 60 min": 3000,
    "Masaža dubokih tkiva - 90 min": 4000,
    "Masaža dubokih tkiva - 120 min": 5000,
    
    # Bamboo masaža
    "Bamboo masaža - 60 min": 3000,
    "Bamboo masaža - 90 min": 4000,
    "Bamboo masaža - 120 min": 5000,
    
    # Limfna drenaža
    "Limfna drenaža - 60 min": 3000,
    "Limfna drenaža - 90 min": 4000,
    "Limfna drenaža - 120 min": 5000,
    
    # SPA Services (all standard price)
    "Tretman lica - 60 min": 3000,
    "Tretman lica - 90 min": 4000,
    "Tretman lica - 120 min": 5000,
    
    "Body wrap - 60 min": 3000,
    "Body wrap - 90 min": 4000,
    "Body wrap - 120 min": 5000,
    
    "Zlatni tretman lica - 60 min": 3000,
    "Zlatni tretman lica - 90 min": 4000,
    "Zlatni tretman lica - 120 min": 5000,
    
    "Parno kupatilo - 60 min": 3000,
    "Parno kupatilo - 90 min": 4000,
    "Parno kupatilo - 120 min": 5000,
    
    "Kraljevski spa paket - 60 min": 3000,
    "Kraljevski spa paket - 90 min": 4000,
    "Kraljevski spa paket - 120 min": 5000,
    
    "Hidratantni tretman - 60 min": 3000,
    "Hidratantni tretman - 90 min": 4000,
    "Hidratantni tretman - 120 min": 5000,
    
    "Detox tretman - 60 min": 3000,
    "Detox tretman - 90 min": 4000,
    "Detox tretman - 120 min": 5000,
    
    "Piling tela - 60 min": 3000,
    "Piling tela - 90 min": 4000,
    "Piling tela - 120 min": 5000,
    
    "Anticelulit tretman - 60 min": 3000,
    "Anticelulit tretman - 90 min": 4000,
    "Anticelulit tretman - 120 min": 5000,
    
    "Kolageni tretman lica - 60 min": 3000,
    "Kolageni tretman lica - 90 min": 4000,
    "Kolageni tretman lica - 120 min": 5000,
    
    "Vitamin C tretman lica - 60 min": 3000,
    "Vitamin C tretman lica - 90 min": 4000,
    "Vitamin C tretman lica - 120 min": 5000,
    
    "Kombinovani spa dan - 60 min": 3000,
    "Kombinovani spa dan - 90 min": 4000,
    "Kombinovani spa dan - 120 min": 5000,
    
    "Čokoladni wrap - 60 min": 3000,
    "Čokoladni wrap - 90 min": 4000,
    "Čokoladni wrap - 120 min": 5000,
}


async def fetch_all_services():
    """Fetch all services from the booking system"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f'{BOOKING_API_BASE}/services')
            response.raise_for_status()
            services = response.json()
            print(f"✓ Fetched {len(services)} services from booking system")
            return services
        except Exception as e:
            print(f"✗ Error fetching services: {e}")
            return []


async def update_service_price(service_id: str, service_name: str, new_price: int):
    """Update a service price in the booking system"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Extract duration from service name
            duration_str = service_name.split(" - ")[-1].replace(" min", "")
            duration_minutes = int(duration_str)
            
            # Prepare update payload
            payload = {
                "name": service_name,
                "price": new_price,
                "duration": duration_minutes,
                "description": ""  # Keep existing or empty
            }
            
            response = await client.put(
                f'{BOOKING_API_BASE}/services/{service_id}',
                json=payload
            )
            response.raise_for_status()
            print(f"  ✓ Updated: {service_name} -> {new_price} RSD")
            return True
        except Exception as e:
            print(f"  ✗ Error updating {service_name}: {e}")
            return False


async def delete_service(service_id: str, service_name: str):
    """Delete an unused service from the booking system"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(f'{BOOKING_API_BASE}/services/{service_id}')
            response.raise_for_status()
            print(f"  ✓ Deleted: {service_name}")
            return True
        except Exception as e:
            print(f"  ✗ Error deleting {service_name}: {e}")
            return False


async def main():
    print("=" * 80)
    print("PRICE SYNCHRONIZATION: Frontend → Booking System")
    print("=" * 80)
    
    # Step 1: Fetch all services from booking system
    print("\n[1/4] Fetching services from booking system...")
    booking_services = await fetch_all_services()
    
    if not booking_services:
        print("✗ Could not fetch services. Exiting.")
        return
    
    # Step 2: Compare and categorize services
    print("\n[2/4] Comparing prices...")
    services_to_update = []
    services_to_delete = []
    services_correct = []
    
    for service in booking_services:
        service_id = service.get('id')
        service_name = service.get('name', '')
        current_price = service.get('price', 0)
        
        if service_name in CORRECT_PRICES:
            expected_price = CORRECT_PRICES[service_name]
            if current_price != expected_price:
                services_to_update.append({
                    'id': service_id,
                    'name': service_name,
                    'current_price': current_price,
                    'new_price': expected_price
                })
            else:
                services_correct.append(service_name)
        else:
            # Service exists in booking system but not in frontend
            services_to_delete.append({
                'id': service_id,
                'name': service_name,
                'price': current_price
            })
    
    # Step 3: Print summary
    print(f"\n✓ Services with correct prices: {len(services_correct)}")
    print(f"⚠ Services needing price update: {len(services_to_update)}")
    print(f"⚠ Services to delete (not used): {len(services_to_delete)}")
    
    if services_to_update:
        print("\nServices needing price update:")
        for svc in services_to_update:
            print(f"  • {svc['name']}: {svc['current_price']} RSD → {svc['new_price']} RSD")
    
    if services_to_delete:
        print("\nServices to delete:")
        for svc in services_to_delete:
            print(f"  • {svc['name']} ({svc['price']} RSD)")
    
    # Step 4: Execute updates and deletions
    print("\n[3/4] Updating prices...")
    for svc in services_to_update:
        await update_service_price(svc['id'], svc['name'], svc['new_price'])
        await asyncio.sleep(0.5)  # Rate limiting
    
    print("\n[4/4] Deleting unused services...")
    for svc in services_to_delete:
        await delete_service(svc['id'], svc['name'])
        await asyncio.sleep(0.5)  # Rate limiting
    
    print("\n" + "=" * 80)
    print("SYNCHRONIZATION COMPLETE")
    print("=" * 80)
    print(f"✓ Updated: {len(services_to_update)} services")
    print(f"✓ Deleted: {len(services_to_delete)} services")
    print(f"✓ Already correct: {len(services_correct)} services")


if __name__ == "__main__":
    asyncio.run(main())
