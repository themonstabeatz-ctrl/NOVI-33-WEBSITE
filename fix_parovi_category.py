#!/usr/bin/env python3
"""
Change category for all [PAROVI] services from 'regular' to 'Kartica Masaza za parove'
"""
import requests
import json

API = "https://spabooking.emergent.host/api"

print("🔧 FIXING [PAROVI] SERVICES CATEGORY")
print("=" * 80)

# Step 1: Get all services
print("\n📡 Fetching all services...")
try:
    response = requests.get(f"{API}/services", timeout=15)
    services = response.json()
    
    # Find [PAROVI] services with category 'regular'
    parovi_regular = [
        s for s in services 
        if '[PAROVI]' in s.get('name', '') and s.get('category') == 'regular'
    ]
    
    print(f"✅ Found {len(parovi_regular)} [PAROVI] services with 'regular' category\n")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Update each service
print("🔧 Updating category to 'Kartica Masaza za parove'...\n")

success = 0
failed = 0

for service in parovi_regular:
    name = service['name']
    
    print(f"🔄 {name}")
    print(f"   Stara kategorija: {service['category']}")
    print(f"   Popust: {service.get('discount_percentage', 0)}%")
    
    # Prepare update payload
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': service['price'],
        'description': service.get('description', ''),
        'category': 'Kartica Masaza za parove',  # CHANGE CATEGORY
        'discount_percentage': service.get('discount_percentage', 10.0)
    }
    
    try:
        r = requests.put(
            f"{API}/services/{service['id']}", 
            json=payload, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if r.status_code in [200, 201]:
            print(f"   ✅ Kategorija promenjena u 'Kartica Masaza za parove'")
            success += 1
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
print(f"✅ Uspešno ažurirano: {success}/{len(parovi_regular)}")
print(f"❌ Neuspešno: {failed}/{len(parovi_regular)}")
print("=" * 80)

if success == len(parovi_regular):
    print("\n🎉 SVE KATEGORIJE USPEŠNO AŽURIRANE!")
    print("\nSada:")
    print("  • [PAROVI] servisi imaju kategoriju: 'Kartica Masaza za parove'")
    print("  • [PAROVI] servisi imaju 10% popust")
    print("  • Frontend će učitati ove servise")
    print("  • Badge sa -10% će se prikazati!")
elif success > 0:
    print(f"\n⚠️ Delimično uspešno: {success} od {len(parovi_regular)}")
else:
    print("\n❌ Ažuriranje nije uspelo")
