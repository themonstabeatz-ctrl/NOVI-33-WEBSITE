#!/usr/bin/env python3
"""
Working Version Analysis
Tries to determine what external booking system the working version uses
"""

import requests
import json
from datetime import datetime

def analyze_working_version():
    """Analyze the working version to understand its configuration"""
    
    print("="*80)
    print(" WORKING VERSION DEEP ANALYSIS")
    print("="*80)
    
    working_base = "https://wavy-parallax-hero.preview.emergentagent.com"
    
    # Test various endpoints to understand the working version
    endpoints_to_test = [
        "/api/health",
        "/api/services",
        "/api/discounts",
        "/api/status"
    ]
    
    print("\n1. TESTING WORKING VERSION ENDPOINTS:")
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{working_base}{endpoint}", timeout=10)
            print(f"  {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if endpoint == "/api/health":
                        print(f"    Health: {data.get('status', 'unknown')}")
                    elif endpoint == "/api/services":
                        couples_count = len([s for s in data if s.get('category') == 'Kartica Masaza za parove'])
                        print(f"    Services: {len(data)} total, {couples_count} couples")
                    elif endpoint == "/api/discounts":
                        print(f"    Discounts: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"    Response: {response.text[:100]}...")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {str(e)}")
    
    print("\n2. ANALYZING WORKING VERSION SERVICES:")
    
    try:
        response = requests.get(f"{working_base}/api/services", timeout=10)
        if response.status_code == 200:
            services = response.json()
            couples_services = [s for s in services if s.get('category') == 'Kartica Masaza za parove']
            
            print(f"Total services: {len(services)}")
            print(f"Couples services: {len(couples_services)}")
            
            # Analyze discount patterns
            discounts = [s.get('discount_percentage', 0) for s in couples_services]
            unique_discounts = set(discounts)
            print(f"Unique discount percentages: {sorted(unique_discounts)}")
            
            # Check for specific service
            aroma_60 = next((s for s in couples_services if 'Aroma terapija' in s.get('name', '') and '60 min' in s.get('name', '')), None)
            if aroma_60:
                print(f"\nAroma terapija - 60 min details:")
                print(f"  Name: {aroma_60.get('name')}")
                print(f"  Price: {aroma_60.get('price')} RSD")
                print(f"  Discount: {aroma_60.get('discount_percentage')}%")
                print(f"  ID: {aroma_60.get('id')}")
            
            # Show all couples services with their details
            print(f"\nAll couples services in working version:")
            for i, service in enumerate(couples_services, 1):
                name = service.get('name', 'N/A')
                price = service.get('price', 'N/A')
                discount = service.get('discount_percentage', 'N/A')
                print(f"  {i:2d}. {name}")
                print(f"      Price: {price} RSD, Discount: {discount}%")
    
    except Exception as e:
        print(f"Error analyzing services: {e}")
    
    print("\n3. TESTING POSSIBLE EXTERNAL BOOKING SYSTEMS:")
    
    # Test possible external systems that working version might use
    possible_systems = [
        "https://wavy-parallax-hero.preview.emergentagent.com/api/services",  # Self-hosted
        "https://spabooking.emergent.host/api/services",  # My system
        "https://pozdrav-kako-si.emergent.host/api/services",  # Alternative
        "https://wavy-parallax-hero.preview.emergentagent.com/api/services"  # My version
    ]
    
    for system in possible_systems:
        try:
            response = requests.get(system, timeout=10)
            if response.status_code == 200:
                data = response.json()
                couples_count = len([s for s in data if s.get('category') == 'Kartica Masaza za parove'])
                couples_services = [s for s in data if s.get('category') == 'Kartica Masaza za parove']
                avg_discount = sum(s.get('discount_percentage', 0) for s in couples_services) / len(couples_services) if couples_services else 0
                
                print(f"\n{system}:")
                print(f"  Status: {response.status_code}")
                print(f"  Total services: {len(data)}")
                print(f"  Couples services: {couples_count}")
                print(f"  Average couples discount: {avg_discount:.1f}%")
                
                # Check if this matches working version pattern
                if couples_count == 17 and avg_discount == 0.0:
                    print(f"  🎯 THIS MATCHES WORKING VERSION PATTERN!")
                elif couples_count == 10 and avg_discount == 10.0:
                    print(f"  📍 This matches my version pattern")
            else:
                print(f"\n{system}: {response.status_code}")
        except Exception as e:
            print(f"\n{system}: ERROR - {str(e)}")
    
    print("\n4. CONCLUSION:")
    print("Based on the analysis:")
    print("- Working version has 17 couples services with 0% discount")
    print("- My version has 10 couples services with 10% discount")
    print("- Working version likely uses its own internal booking system")
    print("- My version uses https://spabooking.emergent.host")
    print("\nThe KEY DIFFERENCE is:")
    print("1. Working version: discount_percentage = 0.0% (discount applied in frontend)")
    print("2. My version: discount_percentage = 10.0% (discount in backend data)")

if __name__ == "__main__":
    analyze_working_version()