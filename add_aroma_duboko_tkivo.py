import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def add_aroma_duboko_tkivo():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['spa_booking']
    services_collection = db['services']
    
    # New massage data
    new_services = [
        # Obične masaže - 60 min
        {
            "name": "Aroma duboko tkivo - 60 min",
            "price": 4900,
            "duration": 60,
            "category": "Obične masaže",
            "discount_percentage": 0
        },
        # Obične masaže - 90 min
        {
            "name": "Aroma duboko tkivo - 90 min",
            "price": 6000,
            "duration": 90,
            "category": "Obične masaže",
            "discount_percentage": 0
        },
        # Kartica Masaza za parove - 60 min (sa popustom 15%)
        {
            "name": "Aroma duboko tkivo - 60 min",
            "price": 4900,
            "duration": 60,
            "category": "Kartica Masaza za parove",
            "discount_percentage": 15
        },
        # Kartica Masaza za parove - 90 min (sa popustom 15%)
        {
            "name": "Aroma duboko tkivo - 90 min",
            "price": 6000,
            "duration": 90,
            "category": "Kartica Masaza za parove",
            "discount_percentage": 15
        }
    ]
    
    print("🔍 Adding 'Aroma duboko tkivo' services...")
    
    for service in new_services:
        # Check if already exists
        existing = await services_collection.find_one({
            "name": service["name"],
            "category": service["category"]
        })
        
        if existing:
            print(f"⚠️  Service already exists: {service['name']} in {service['category']}")
        else:
            result = await services_collection.insert_one(service)
            print(f"✅ Added: {service['name']} in {service['category']} (ID: {result.inserted_id})")
    
    # Count total services
    total_obicne = await services_collection.count_documents({"category": "Obične masaže"})
    total_kartica = await services_collection.count_documents({"category": "Kartica Masaza za parove"})
    
    print(f"\n📊 Total services:")
    print(f"   - Obične masaže: {total_obicne}")
    print(f"   - Kartica Masaza za parove: {total_kartica}")
    
    client.close()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(add_aroma_duboko_tkivo())
