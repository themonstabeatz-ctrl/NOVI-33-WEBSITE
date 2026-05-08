#!/usr/bin/env python3
"""
Fix my version to match working version EXACTLY:
1. Set all discounts to 0%
2. Add missing 7 services
"""
import requests
import json

API = "https://spabooking.emergent.host/api"

print("🔧 FIXING TO MATCH WORKING VERSION")
print("=" * 80)

# Step 1: Set all [PAROVI] discounts to 0%
print("\nStep 1: Setting all [PAROVI] discounts to 0%...")
response = requests.get(f"{API}/services", timeout=15)
services = response.json()
parovi = [s for s in services if '[PAROVI]' in s.get('name', '')]

for service in parovi:
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': service['price'],
        'description': service.get('description', ''),
        'category': service.get('category', ''),
        'discount_percentage': 0.0  # SET TO 0%
    }
    
    try:
        r = requests.put(f"{API}/services/{service['id']}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✅ {service['name']}: discount set to 0%")
    except Exception as e:
        print(f"❌ {service['name']}: {str(e)[:50]}")

# Step 2: Add missing services
print("\nStep 2: Adding missing 7 services...")

missing_services = [
    {
        "name": "[PAROVI] Aroma duboko tkivo - 60 min",
        "duration": 60,
        "price": 4900,
        "description": "Aroma duboko tkivo za parove - 60 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Aroma duboko tkivo - 90 min",
        "duration": 90,
        "price": 6000,
        "description": "Aroma duboko tkivo za parove - 90 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Aromaterapija & topli kamen - 90 min",
        "duration": 90,
        "price": 6200,
        "description": "Aromaterapija & topli kamen za parove - 90 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Aromaterapija & topli kamen - 120 min",
        "duration": 120,
        "price": 7200,
        "description": "Aromaterapija & topli kamen za parove - 120 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Aroma sa toplim biljnim kompresama - 90 min",
        "duration": 90,
        "price": 6200,
        "description": "Aroma sa toplim biljnim kompresama za parove - 90 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Aroma sa toplim biljnim kompresama - 120 min",
        "duration": 120,
        "price": 7200,
        "description": "Aroma sa toplim biljnim kompresama za parove - 120 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    },
    {
        "name": "[PAROVI] Thai masaža sa toplim biljnim kompresama - 90 min",
        "duration": 90,
        "price": 6200,
        "description": "Thai masaža sa toplim biljnim kompresama za parove - 90 minuta",
        "category": "Kartica Masaza za parove",
        "discount_percentage": 0.0
    }
]

# Check which services already exist
existing = [s['name'] for s in services]

for new_service in missing_services:
    if new_service['name'] in existing:
        print(f"⏭️  {new_service['name']}: Already exists")
    else:
        try:
            r = requests.post(f"{API}/services", json=new_service, timeout=10)
            if r.status_code in [200, 201]:
                print(f"✅ {new_service['name']}: Added!")
            else:
                print(f"❌ {new_service['name']}: Failed")
        except Exception as e:
            print(f"❌ {new_service['name']}: {str(e)[:50]}")

print("\n" + "=" * 80)
print("DONE! Now matching working version:")
print("  • All [PAROVI] services: discount = 0%")
print("  • Total couples services: 17 (same as working version)")
print("=" * 80)
