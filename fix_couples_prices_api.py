#!/usr/bin/env python3
"""
API-based Price Correction Script for Couples Massage Services
Updates prices directly via API PUT requests
"""

import requests
import json
from typing import Dict, List

# Booking system API base URL - PRODUCTION
API_BASE = "https://wavy-parallax-hero.preview.emergentagent.com/api"

# Correct price mapping from /app/frontend/src/pages/Massage.js
# Note: Services have [PAROVI] prefix in the booking system
CORRECT_PRICES = {
    # Tradicionalna tajlandska masaža
    "Tradicionalna tajlandska masaža - 60 min": 4400,
    "Tradicionalna tajlandska masaža - 90 min": 5600,
    "Tradicionalna tajlandska masaža - 120 min": 6800,
    
    # Aroma terapija
    "Aroma terapija - 60 min": 4400,
    "Aroma terapija - 90 min": 5600,
    "Aroma terapija - 120 min": 6800,
    
    # Masaža toplim uljem
    "Masaža toplim uljem - 60 min": 4600,
    "Masaža toplim uljem - 90 min": 5800,
    
    # Glava, vrat, ramena i leđa
    "Glava, vrat, ramena i leđa - 30 min": 2400,
    "Glava, vrat, ramena i leđa - 45 min": 3200,
    "Glava, vrat, ramena i leđa - 60 min": 3900,
    
    # Masaža stopala
    "Masaža stopala - 30 min": 2400,
    "Masaža stopala - 45 min": 2900,
    "Masaža stopala - 60 min": 3500,
    
    # Aroma duboko tkivo
    "Aroma duboko tkivo - 60 min": 4900,
    "Aroma duboko tkivo - 90 min": 6000,
    
    # Aromaterapija & topli kamen
    "Aromaterapija & topli kamen - 90 min": 6200,
    "Aromaterapija & topli kamen - 120 min": 7200,
    
    # Aroma sa toplim biljnim kompresama
    "Aroma sa toplim biljnim kompresama - 90 min": 6200,
    "Aroma sa toplim biljnim kompresama - 120 min": 7200,
    
    # Thai masaža sa toplim biljnim kompresama
    "Thai masaža sa toplim biljnim kompresama - 90 min": 6200,
    "Thai masaža sa toplim biljnim kompresama - 120 min": 7200
}

def fetch_all_services() -> List[Dict]:
    """Fetch all services from booking system API"""
    try:
        response = requests.get(f"{API_BASE}/services", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching services: {e}")
        return []

def update_service_price(service: Dict, new_price: float) -> bool:
    """Update service price via PUT request"""
    try:
        service_id = service['id']
        
        # Prepare full service data with updated price
        updated_service = {
            'name': service['name'],
            'duration': service['duration'],
            'price': new_price,
            'description': service['description'],
            'category': service['category'],
            'discount_percentage': service.get('discount_percentage', 10.0)
        }
        
        # PUT request to update service
        response = requests.put(
            f"{API_BASE}/services/{service_id}",
            json=updated_service,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        
        return True
    except Exception as e:
        print(f"   ❌ Update failed: {e}")
        return False

def main():
    print("=" * 70)
    print("🏥 COUPLES MASSAGE PRICE CORRECTION - API METHOD")
    print("=" * 70)
    print(f"Target API: {API_BASE}")
    print(f"Services to update: {len(CORRECT_PRICES)}")
    print("=" * 70)
    print()
    
    # Step 1: Fetch all services
    print("📡 Fetching all services from booking system...")
    all_services = fetch_all_services()
    
    if not all_services:
        print("❌ Failed to fetch services. Exiting.")
        return 1
    
    print(f"✅ Found {len(all_services)} total services\n")
    
    # Step 2: Filter couples massage services
    print("🔍 Filtering 'Kartica Masaza za parove' services...")
    couples_services = [
        s for s in all_services 
        if s.get('category') == 'Kartica Masaza za parove'
    ]
    print(f"✅ Found {len(couples_services)} couples massage services\n")
    
    # Step 3: Update each service with correct price
    print("🔧 Updating service prices...\n")
    
    updates_successful = 0
    updates_failed = 0
    updates_skipped = 0
    
    for service in couples_services:
        service_name = service['name']
        current_price = service['price']
        
        # Remove [PAROVI] prefix to match with CORRECT_PRICES dict
        clean_name = service_name.replace('[PAROVI] ', '')
        
        if clean_name not in CORRECT_PRICES:
            print(f"⚠️  SKIP: {service_name}")
            print(f"   Reason: Not in price correction mapping")
            print()
            updates_skipped += 1
            continue
        
        correct_price = CORRECT_PRICES[clean_name]
        
        # Check if update is needed
        if abs(current_price - correct_price) < 1:  # Within 1 RSD tolerance
            print(f"✓  SKIP: {service_name}")
            print(f"   Current price {current_price} RSD is already correct")
            print()
            updates_skipped += 1
            continue
        
        # Update needed
        print(f"🔄 UPDATE: {service_name}")
        print(f"   Current: {current_price} RSD → Correct: {correct_price} RSD (Δ {correct_price - current_price:+.0f} RSD)")
        
        if update_service_price(service, correct_price):
            print(f"   ✅ Successfully updated to {correct_price} RSD")
            updates_successful += 1
        else:
            print(f"   ❌ Update failed")
            updates_failed += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 UPDATE SUMMARY")
    print("=" * 70)
    print(f"✅ Successful updates: {updates_successful}")
    print(f"⏭️  Skipped (already correct): {updates_skipped}")
    print(f"❌ Failed updates: {updates_failed}")
    print(f"📝 Total couples services: {len(couples_services)}")
    print("=" * 70)
    print()
    
    if updates_successful > 0:
        print("🎉 PRICE CORRECTIONS APPLIED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Verify prices in frontend: https://wavy-parallax-hero.preview.emergentagent.com/massage")
        print("2. Test booking flow with corrected prices")
        print("3. Check that 10% discount is applied correctly (not double discount)")
        return 0
    elif updates_skipped == len(couples_services):
        print("✨ ALL PRICES ALREADY CORRECT - No updates needed!")
        return 0
    else:
        print("⚠️  SOME UPDATES FAILED - Manual intervention may be needed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
