#!/usr/bin/env python3
"""
Remove Discounts from Booking System for Couples Massage Services
Sets discount_percentage to 0% for all services in "Kartica Masaza za parove" category
"""

import requests
import json

# Booking system API
API_BASE = "https://gold-line-fixer.preview.emergentagent.com/api"

def fetch_couples_services():
    """Fetch all couples massage services"""
    try:
        response = requests.get(f"{API_BASE}/services", timeout=10)
        response.raise_for_status()
        services = response.json()
        
        # Filter couples services
        couples = [s for s in services if s.get('category') == 'Kartica Masaza za parove']
        return couples
    except Exception as e:
        print(f"❌ Error fetching services: {e}")
        return []

def remove_discount(service):
    """Remove discount from a service (set to 0%)"""
    try:
        service_id = service['id']
        
        # Prepare update with discount removed
        updated_service = {
            'name': service['name'],
            'duration': service['duration'],
            'price': service['price'],  # Keep the same price
            'description': service['description'],
            'category': service['category'],
            'discount_percentage': 0.0  # REMOVE DISCOUNT
        }
        
        # PUT request
        response = requests.put(
            f"{API_BASE}/services/{service_id}",
            json=updated_service,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    print("=" * 80)
    print("🔧 UKLANJANJE POPUSTA IZ BOOKING SISTEMA")
    print("=" * 80)
    print("Kategorija: Kartica Masaza za parove")
    print("Akcija: Postavljanje discount_percentage = 0%")
    print("=" * 80)
    print()
    
    # Fetch couples services
    print("📡 Fetching couples massage services...")
    couples_services = fetch_couples_services()
    
    if not couples_services:
        print("❌ No services found. Exiting.")
        return 1
    
    print(f"✅ Found {len(couples_services)} couples services\n")
    
    # Show current state
    print("📊 TRENUTNO STANJE:")
    print("-" * 80)
    for s in couples_services:
        discount = s.get('discount_percentage', 0)
        print(f"{s['name']}")
        print(f"  Bazna cena: {s['price']} RSD | Popust: {discount}%")
    print("-" * 80)
    print()
    
    # Remove discounts
    print("🔧 Uklanjanje popusta...\n")
    
    success_count = 0
    failed_count = 0
    
    for service in couples_services:
        current_discount = service.get('discount_percentage', 0)
        
        if current_discount == 0:
            print(f"⏭️  SKIP: {service['name']}")
            print(f"   Već nema popust (0%)")
            print()
            success_count += 1
            continue
        
        print(f"🔄 UPDATE: {service['name']}")
        print(f"   Bazna cena: {service['price']} RSD")
        print(f"   Stari popust: {current_discount}% → Novi popust: 0%")
        
        if remove_discount(service):
            print(f"   ✅ Uspešno uklonjendiscount!")
            success_count += 1
        else:
            failed_count += 1
        print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Uspešno: {success_count}")
    print(f"❌ Neuspešno: {failed_count}")
    print(f"📝 Ukupno: {len(couples_services)}")
    print("=" * 80)
    print()
    
    if success_count == len(couples_services):
        print("🎉 SVI POPUSTI USPEŠNO UKLONJENI!")
        print()
        print("ℹ️  Sada:")
        print("   • Booking sistem čuva originalne cene BEZ popusta")
        print("   • Frontend primenjuje 10% popust samo na kartici 'Masaža za parove'")
        print("   • Nema više dvostrukog popusta!")
        return 0
    else:
        print("⚠️  Neki popusti nisu uklonjeni - provera potrebna")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
