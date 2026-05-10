import httpx
import asyncio

async def add_aroma_duboko_tkivo_to_spabooking():
    booking_api = "https://wavy-parallax-hero.preview.emergentagent.com"
    
    # New services to add
    new_services = [
        {
            "name": "Aroma duboko tkivo - 60 min",
            "duration": 60,
            "price": 4900,
            "category": "Obične masaže",
            "description": "Kombinacija duboke masaže i aromaterapije za intenzivno opuštanje mišića i uma.",
            "discount_percentage": 0
        },
        {
            "name": "Aroma duboko tkivo - 90 min",
            "duration": 90,
            "price": 6000,
            "category": "Obične masaže",
            "description": "Kombinacija duboke masaže i aromaterapije za intenzivno opuštanje mišića i uma.",
            "discount_percentage": 0
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"🔍 Adding services to {booking_api}...")
        
        for service in new_services:
            try:
                # Try to add service
                response = await client.post(
                    f"{booking_api}/api/services",
                    json=service
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    print(f"✅ Added: {service['name']} - {service['price']} RSD")
                else:
                    print(f"⚠️  Failed to add {service['name']}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error adding {service['name']}: {str(e)}")
        
        # Verify services were added
        print("\n🔍 Verifying services...")
        try:
            response = await client.get(f"{booking_api}/api/services")
            if response.status_code == 200:
                services = response.json()
                aroma_services = [s for s in services if "Aroma duboko tkivo" in s.get("name", "")]
                print(f"✅ Found {len(aroma_services)} 'Aroma duboko tkivo' services in system")
                for s in aroma_services:
                    print(f"   - {s['name']} ({s['category']}) - {s['price']} RSD")
            else:
                print(f"⚠️  Could not verify: {response.status_code}")
        except Exception as e:
            print(f"❌ Error verifying: {str(e)}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(add_aroma_duboko_tkivo_to_spabooking())
