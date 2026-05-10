#!/usr/bin/env python3
"""
Activate 10% discount for all PAROVI services via production booking API
"""
import requests
import json

# Use our backend as proxy to booking system
API = "https://wavy-parallax-hero.preview.emergentagent.com/api"
BOOKING_API = "https://spabooking.emergent.host/api"

print("🔧 ACTIVATING 10% DISCOUNT FOR ALL PAROVI SERVICES")
print("=" * 80)

# Step 1: Get all services
print("\n📡 Fetching services...")
try:
    response = requests.get(f"{API}/services", timeout=15)
    services = response.json()
    parovi = [s for s in services if 'PAROVI' in s.get('name', '')]
    print(f"✅ Found {len(parovi)} PAROVI services\n")
except Exception as e:
    print(f"❌ Error fetching services: {e}")
    exit(1)

# Step 2: Activate 10% discount for each
print("🔧 Activating 10% discount...\n")

success = 0
failed = 0

for service in parovi:
    name = service['name'].replace('[PAROVI] ', '')
    current_price = service['price']
    current_discount = service.get('discount_percentage', 0)
    
    print(f"🔄 {name}")
    print(f"   Trenutno: {current_price} RSD (popust: {current_discount}%)")
    
    # Prepare payload with 10% discount
    payload = {
        'name': service['name'],
        'duration': service['duration'],
        'price': current_price,
        'description': service.get('description', ''),
        'category': service.get('category', ''),
        'discount_percentage': 10.0
    }
    
    try:
        # Use PUT to update service
        r = requests.put(
            f"{BOOKING_API}/services/{service['id']}", 
            json=payload, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if r.status_code in [200, 201]:
            discounted_price = current_price * 0.9
            print(f"   ✅ Aktiviran 10% popust!")
            print(f"   Nova akcijska cena: {discounted_price:.0f} RSD")
            success += 1
        else:
            print(f"   ❌ Failed: HTTP {r.status_code}")
            print(f"   Response: {r.text[:100]}")
            failed += 1
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:80]}")
        failed += 1
    
    print()

# Summary
print("=" * 80)
print("📊 REZULTAT")
print("=" * 80)
print(f"✅ Uspešno aktivirano: {success}/{len(parovi)}")
print(f"❌ Neuspešno: {failed}/{len(parovi)}")
print("=" * 80)

if success == len(parovi):
    print("\n🎉 SVI POPUSTI USPEŠNO AKTIVIRANI!")
    print("\nSada:")
    print("  • Booking sistem: Vraća cene SA 10% popustom (npr. 3,960 RSD)")
    print("  • Frontend: Prikazuje tu cenu direktno BEZ dodatnog popusta")
    print("  • Korisnik vidi: 3,960 RSD (finalno)")
elif success > 0:
    print(f"\n⚠️ Delimično uspešno: {success} od {len(parovi)} servisa")
else:
    print("\n❌ Nijedan popust nije aktiviran - proverite API pristup")
