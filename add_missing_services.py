#!/usr/bin/env python3
"""
Script to add missing services to booking system
"""
import httpx
import asyncio
import json

BOOKING_API_URL = "https://pozdrav-kako-si.emergent.host/api/services"

# Missing services that need to be created
MISSING_SERVICES = [
    # Masaže
    {"name": "Shiatsu masaža", "base_price": 3500, "desc": "Japanska masaža pritiskom prstiju"},
    {"name": "Refleksologija", "base_price": 3000, "desc": "Masaža refleksnih tačaka na stopalima"},
    {"name": "Prenatalna masaža", "base_price": 3500, "desc": "Nežna masaža za trudnice"},
    {"name": "Masaža dubokih tkiva", "base_price": 4000, "desc": "Intenzivna masaža dubokih mišića"},
    {"name": "Bamboo masaža", "base_price": 3500, "desc": "Masaža bambusovim štapovima"},
    {"name": "Limfna drenaža", "base_price": 3500, "desc": "Masaža limfnog sistema"},
    
    # Spa tretmani
    {"name": "Piling tela", "base_price": 3000, "desc": "Eksfolijacija mrtvih ćelija kože"},
    {"name": "Anticelulit tretman", "base_price": 4000, "desc": "Tretman protiv celulita"},
    {"name": "Kolageni tretman lica", "base_price": 4500, "desc": "Tretman lica sa kolagenom"},
    {"name": "Vitamin C tretman lica", "base_price": 4000, "desc": "Tretman lica sa vitaminom C"},
    {"name": "Kombinovani spa dan", "base_price": 8000, "desc": "Celonevni spa paket"},
    {"name": "Čokoladni wrap", "base_price": 5000, "desc": "Obavijanje tela čokoladom"},
]

async def create_service(client, name, duration, price, description):
    """Create a single service"""
    service_data = {
        "name": f"{name} - {duration} min",
        "duration": duration,
        "price": float(price),
        "description": f"{description} u trajanju od {duration} minuta"
    }
    
    try:
        response = await client.post(BOOKING_API_URL, json=service_data)
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Created: {service_data['name']} (ID: {result['id']})")
            return result
        else:
            print(f"❌ Failed to create {service_data['name']}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating {service_data['name']}: {str(e)}")
        return None

async def main():
    """Main function to create all missing services"""
    print("=" * 60)
    print("KREIRANJE NEDOSTAJUĆIH SERVISA U BOOKING SISTEMU")
    print("=" * 60)
    print(f"\nUkupno servisa za kreiranje: {len(MISSING_SERVICES)} x 3 trajanja = {len(MISSING_SERVICES) * 3}")
    print()
    
    created_services = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for service in MISSING_SERVICES:
            print(f"\n📌 Kreiram: {service['name']}")
            print("-" * 60)
            
            # Create for 60, 90, and 120 minutes
            for duration in [60, 90, 120]:
                # Calculate price based on duration
                if duration == 60:
                    price = service['base_price']
                elif duration == 90:
                    price = service['base_price'] + 1000
                else:  # 120 min
                    price = service['base_price'] + 2000
                
                result = await create_service(
                    client,
                    service['name'],
                    duration,
                    price,
                    service['desc']
                )
                
                if result:
                    created_services.append(result)
                
                await asyncio.sleep(0.1)  # Small delay between requests
    
    print("\n" + "=" * 60)
    print(f"✅ ZAVRŠENO! Kreirano {len(created_services)} novih servisa")
    print("=" * 60)
    
    # Print service ID mapping for Contact.js
    print("\n📋 MAPIRANJE ZA CONTACT.JS:")
    print("-" * 60)
    for service in created_services:
        print(f'        "{service["name"]}": "{service["id"]}",')

if __name__ == "__main__":
    asyncio.run(main())
