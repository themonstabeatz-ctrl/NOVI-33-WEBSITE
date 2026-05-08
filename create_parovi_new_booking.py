#!/usr/bin/env python3
import httpx
import asyncio

BOOKING_API = "https://spabooking.emergent.host"

MASSAGES = [
    {"name": "Tradicionalna tajlandska masaža", "60": 4400, "90": 5600, "120": 6800},
    {"name": "Aroma terapija", "60": 4400, "90": 5600, "120": 6800},
    {"name": "Masaža toplim uljem", "60": 4600, "90": 5800},
    {"name": "Glava, vrat, ramena i leđa", "60": 3900},
    {"name": "Masaža stopala", "60": 3500}
]

async def main():
    print("📋 Creating [PAROVI] services in NEW booking system...\n")
    
    success = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        for massage in MASSAGES:
            name = massage['name']
            for duration in ['60', '90', '120']:
                if duration in massage:
                    price = massage[duration]
                    service_data = {
                        "name": f"[PAROVI] {name} - {duration} min",
                        "description": f"{name} u trajanju od {duration} minuta",
                        "duration": int(duration),
                        "price": price,
                        "discount_percentage": 0
                    }
                    
                    response = await client.post(f"{BOOKING_API}/api/services", json=service_data)
                    if response.status_code in [200, 201]:
                        print(f"✅ {service_data['name']}")
                        success += 1
                    else:
                        print(f"❌ Failed: {service_data['name']}")
                    
                    await asyncio.sleep(0.1)
    
    print(f"\n✅ Created {success} [PAROVI] services!")

if __name__ == "__main__":
    asyncio.run(main())
