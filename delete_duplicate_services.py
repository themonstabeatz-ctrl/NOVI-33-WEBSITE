#!/usr/bin/env python3
"""
Delete duplicate services WITHOUT [PAROVI] prefix from 'Kartica Masaza za parove' category
Keep only [PAROVI] services with 10% discount
"""
import requests
import json

API = "https://spabooking.emergent.host/api"

print("🗑️  BRISANJE DUPLIKATA IZ KATEGORIJE 'Kartica Masaza za parove'")
print("=" * 80)

# Get all services
print("\n📡 Fetching all services...")
response = requests.get(f"{API}/services", timeout=15)
services = response.json()

# Find duplicates: services WITHOUT [PAROVI] prefix in 'Kartica Masaza za parove'
duplicates = [
    s for s in services 
    if s.get('category') == 'Kartica Masaza za parove' 
    and '[PAROVI]' not in s.get('name', '')
]

print(f"✅ Found {len(duplicates)} duplicate services to delete\n")

if not duplicates:
    print("✅ No duplicates found - all clean!")
    exit(0)

print("🗑️  Deleting duplicate services...\n")

deleted = 0
failed = 0

for service in duplicates:
    name = service['name']
    service_id = service['id']
    
    print(f"🗑️  Deleting: {name}")
    print(f"   ID: {service_id}")
    print(f"   Cena: {service['price']} RSD")
    print(f"   Popust: {service.get('discount_percentage', 0)}%")
    
    try:
        r = requests.delete(f"{API}/services/{service_id}", timeout=10)
        
        if r.status_code in [200, 204]:
            print(f"   ✅ OBRISANO!")
            deleted += 1
        else:
            print(f"   ❌ Failed: HTTP {r.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:60]}")
        failed += 1
    
    print()

# Summary
print("=" * 80)
print("📊 REZULTAT")
print("=" * 80)
print(f"✅ Obrisano: {deleted}/{len(duplicates)}")
print(f"❌ Neuspešno: {failed}/{len(duplicates)}")
print("=" * 80)

if deleted == len(duplicates):
    print("\n🎉 SVI DUPLIKATI USPEŠNO OBRISANI!")
    print("\nSada:")
    print("  • Samo [PAROVI] servisi sa 10% popustom ostaju")
    print("  • Frontend će učitati servise sa 10% popustom")
    print("  • Badge sa -10% će se prikazati!")
elif deleted > 0:
    print(f"\n⚠️ Delimično uspešno: {deleted} od {len(duplicates)}")
else:
    print("\n❌ Brisanje nije uspelo")
