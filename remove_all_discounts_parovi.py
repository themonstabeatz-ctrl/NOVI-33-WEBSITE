#!/usr/bin/env python3
"""
Remove ALL discounts from [PAROVI] services - set to 0%
"""
import requests
import json

API = "https://spabooking.emergent.host/api"

print("🔧 UKLANJANJE SVIH POPUSTA SA [PAROVI] SERVISA")
print("=" * 80)

# Get all services
response = requests.get(f"{API}/services", timeout=15)
services = response.json()

# Find [PAROVI] services with discount > 0
parovi_with_discount = [
    s for s in services 
    if '[PAROVI]' in s.get('name', '') and s.get('discount_percentage', 0) > 0
]

print(f"✅ Found {len(parovi_with_discount)} [PAROVI] services with discount\n")

success = 0
for service in parovi_with_discount:
    name = service['name']
    
    print(f"🔄 {name}")
    print(f"   Trenutni popust: {service.get('discount_percentage', 0)}%")
    
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': service['price'],
        'description': service.get('description', ''),
        'category': service.get('category', ''),
        'discount_percentage': 0.0  # UKLONI POPUST
    }
    
    try:
        r = requests.put(f"{API}/services/{service['id']}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            print(f"   ✅ Popust uklonjen (0%)")
            success += 1
        else:
            print(f"   ❌ Failed")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
    print()

print("=" * 80)
print(f"✅ Uklonjeno: {success}/{len(parovi_with_discount)}")
print("=" * 80)
print("\nSada:")
print("  • [PAROVI] servisi: discount_percentage = 0%")
print("  • Badge sa -10% NEĆE se prikazivati")
