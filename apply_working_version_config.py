#!/usr/bin/env python3
"""
Apply WORKING version configuration - set 10% discount for all [PAROVI] services
"""
import requests
import json

API = "https://spabooking.emergent.host/api"

print("🔧 PRIMENJUJEM RADNU KONFIGURACIJU")
print("=" * 80)
print("Postavljam 10% popust na sve [PAROVI] servise")
print("=" * 80)
print()

# Get all services
response = requests.get(f"{API}/services", timeout=15)
services = response.json()

# Find [PAROVI] services
parovi = [s for s in services if '[PAROVI]' in s.get('name', '')]

print(f"✅ Found {len(parovi)} [PAROVI] services\n")

success = 0
for service in parovi:
    name = service['name']
    
    print(f"🔄 {name}")
    print(f"   Cena: {service['price']} RSD")
    
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': service['price'],
        'description': service.get('description', ''),
        'category': service.get('category', ''),
        'discount_percentage': 10.0  # 10% POPUST
    }
    
    try:
        r = requests.put(f"{API}/services/{service['id']}", json=payload, timeout=10)
        if r.status_code in [200, 201]:
            print(f"   ✅ Popust aktiviran: 10%")
            success += 1
        else:
            print(f"   ❌ Failed")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
    print()

print("=" * 80)
print(f"✅ Aktivirano: {success}/{len(parovi)}")
print("=" * 80)
print("\nSada:")
print("  • [PAROVI] servisi: discount_percentage = 10%")
print("  • Badge sa -10% će se prikazati!")
print("  • Identično kao radna verzija!")
