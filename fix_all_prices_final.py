#!/usr/bin/env python3
"""
FINALNO ISPRAVLJANJE - Sve cene na okrugle brojeve + uklanjanje popusta
"""
import requests
import json

API = "https://wavy-parallax-hero.preview.emergentagent.com/api"

# ISPRAVNE OKRUGLE CENE
CORRECT_PRICES = {
    "Tradicionalna tajlandska masaža - 60 min": 4400,
    "Tradicionalna tajlandska masaža - 90 min": 5600,
    "Tradicionalna tajlandska masaža - 120 min": 6800,
    "Aroma terapija - 60 min": 4400,
    "Aroma terapija - 90 min": 5600,
    "Aroma terapija - 120 min": 6800,
    "Masaža toplim uljem - 60 min": 4600,
    "Masaža toplim uljem - 90 min": 5800,
    "Aroma duboko tkivo - 60 min": 4900,
    "Aroma duboko tkivo - 90 min": 6000,
    "Aromaterapija & topli kamen - 90 min": 6200,
    "Aromaterapija & topli kamen - 120 min": 7200,
    "Aroma sa toplim biljnim kompresama - 90 min": 6200,
    "Aroma sa toplim biljnim kompresama - 120 min": 7200,
    "Thai masaža sa toplim biljnim kompresama - 90 min": 6200,
    "Thai masaža sa toplim biljnim kompresama - 120 min": 7200,
    "Glava, vrat, ramena i leđa - 60 min": 3900,
    "Masaža stopala - 60 min": 3500,
}

def fix_service(service):
    """Fix single service - set correct price and remove discount"""
    name = service['name'].replace('[PAROVI] ', '')
    
    if name not in CORRECT_PRICES:
        return False
    
    correct_price = CORRECT_PRICES[name]
    service_id = service['id']
    
    # Prepare update payload
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': correct_price,
        'description': service.get('description', ''),
        'category': service.get('category', ''),
        'discount_percentage': 0.0  # REMOVE ALL DISCOUNTS
    }
    
    try:
        # Try PUT
        r = requests.put(f"{API}/services/{service_id}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            return True
        
        # Try PATCH
        r = requests.patch(f"{API}/services/{service_id}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            return True
            
        print(f"  ❌ Failed: {r.status_code} - {r.text[:100]}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Fetch all services
print("📡 Fetching services...")
services = requests.get(f"{API}/services", timeout=15).json()

# Find services with non-round prices
print(f"\n🔧 Fixing services with non-round prices...")
print("=" * 80)

fixed = 0
failed = 0

for service in services:
    price = service.get('price', 0)
    
    # Check if price is not round (doesn't end with 00)
    if int(price) % 100 != 0 or service.get('discount_percentage', 0) > 0:
        name = service['name'].replace('[PAROVI] ', '')
        
        if name in CORRECT_PRICES:
            print(f"\n🔄 {service['name']}")
            print(f"   Stara cena: {price} RSD, Popust: {service.get('discount_percentage', 0)}%")
            print(f"   Nova cena: {CORRECT_PRICES[name]} RSD, Popust: 0%")
            
            if fix_service(service):
                print(f"   ✅ FIXED!")
                fixed += 1
            else:
                failed += 1

print("\n" + "=" * 80)
print(f"✅ Fixed: {fixed}")
print(f"❌ Failed: {failed}")
print("=" * 80)
