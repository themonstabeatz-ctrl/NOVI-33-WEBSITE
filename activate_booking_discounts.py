#!/usr/bin/env python3
"""
Activate 10% discount in booking system for all couples massage services
"""
import requests
import json

API = "https://gold-line-fixer.preview.emergentagent.com/api"

def activate_discount(service):
    """Set discount to 10% for a service"""
    try:
        service_id = service['id']
        
        # Update with 10% discount
        payload = {
            'name': service['name'],
            'duration': service['duration'],
            'price': service['price'],
            'description': service.get('description', ''),
            'category': service.get('category', ''),
            'discount_percentage': 10.0  # ACTIVATE 10% DISCOUNT
        }
        
        r = requests.put(f"{API}/services/{service_id}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Fetch all services
print("📡 Fetching services...")
services = requests.get(f"{API}/services", timeout=15).json()
parovi = [s for s in services if 'PAROVI' in s.get('name', '')]

print(f"✅ Found {len(parovi)} couples services\n")
print("🔧 Activating 10% discount for all couples massages...\n")

success = 0
for service in parovi:
    name = service['name'].replace('[PAROVI] ', '')
    price = service['price']
    
    print(f"🔄 {name}")
    print(f"   Cena: {price} RSD → Sa 10%: {price * 0.9:.0f} RSD")
    
    if activate_discount(service):
        print(f"   ✅ Popust aktiviran!")
        success += 1
    else:
        print(f"   ❌ Failed")
    print()

print("=" * 80)
print(f"✅ Uspešno: {success}/{len(parovi)}")
print("=" * 80)
