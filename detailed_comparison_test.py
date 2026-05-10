#!/usr/bin/env python3
"""
Detailed Backend Comparison Test
Analyzes the exact differences between working and my version
"""

import requests
import json
from datetime import datetime
import sys

def print_header(title):
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

def print_section(title):
    print(f"\n{'-'*50}")
    print(f" {title}")
    print(f"{'-'*50}")

def test_backend_endpoints():
    """Test backend endpoints and configurations"""
    
    print_header("DETAILED BACKEND COMPARISON ANALYSIS")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # URLs to test
    working_base = "https://wavy-parallax-hero.preview.emergentagent.com"
    my_base = "https://wavy-parallax-hero.preview.emergentagent.com"
    
    print_section("1. BACKEND CONFIGURATION ANALYSIS")
    
    # Test my backend configuration
    print("MY VERSION BACKEND CONFIGURATION:")
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    print(f"  {line}")
    except Exception as e:
        print(f"  Error reading backend .env: {e}")
    
    print("\nMY VERSION FRONTEND CONFIGURATION:")
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    print(f"  {line}")
    except Exception as e:
        print(f"  Error reading frontend .env: {e}")
    
    print_section("2. API ENDPOINT COMPARISON")
    
    # Test both APIs
    working_api = f"{working_base}/api/services"
    my_api = f"{my_base}/api/services"
    
    print(f"Working API: {working_api}")
    print(f"My API: {my_api}")
    
    # Get data from both APIs
    working_data = []
    my_data = []
    
    try:
        print("\nTesting WORKING VERSION API...")
        response = requests.get(working_api, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            working_data = response.json()
            print(f"  Total services: {len(working_data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Exception: {str(e)}")
    
    try:
        print("\nTesting MY VERSION API...")
        response = requests.get(my_api, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            my_data = response.json()
            print(f"  Total services: {len(my_data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Exception: {str(e)}")
    
    print_section("3. COUPLES MASSAGE SERVICES DETAILED ANALYSIS")
    
    if working_data and my_data:
        # Filter couples services
        working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
        my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
        
        print(f"Working version couples services: {len(working_couples)}")
        print(f"My version couples services: {len(my_couples)}")
        
        # Analyze service names
        working_names = set(s.get('name', '') for s in working_couples)
        my_names = set(s.get('name', '') for s in my_couples)
        
        print(f"\nWorking version service names ({len(working_names)}):")
        for name in sorted(working_names):
            print(f"  - {name}")
        
        print(f"\nMy version service names ({len(my_names)}):")
        for name in sorted(my_names):
            print(f"  - {name}")
        
        # Find differences
        only_in_working = working_names - my_names
        only_in_my = my_names - working_names
        common_names = working_names & my_names
        
        if only_in_working:
            print(f"\nServices ONLY in working version ({len(only_in_working)}):")
            for name in sorted(only_in_working):
                print(f"  ❌ {name}")
        
        if only_in_my:
            print(f"\nServices ONLY in my version ({len(only_in_my)}):")
            for name in sorted(only_in_my):
                print(f"  ❌ {name}")
        
        if common_names:
            print(f"\nCommon services ({len(common_names)}):")
            for name in sorted(common_names):
                print(f"  ✅ {name}")
        
        print_section("4. PRICE AND DISCOUNT COMPARISON FOR COMMON SERVICES")
        
        # Compare prices and discounts for common services
        for name in sorted(common_names):
            working_service = next((s for s in working_couples if s.get('name') == name), None)
            my_service = next((s for s in my_couples if s.get('name') == name), None)
            
            if working_service and my_service:
                working_price = working_service.get('price', 0)
                my_price = my_service.get('price', 0)
                working_discount = working_service.get('discount_percentage', 0)
                my_discount = my_service.get('discount_percentage', 0)
                
                print(f"\n{name}:")
                print(f"  Working: Price={working_price} RSD, Discount={working_discount}%")
                print(f"  My:      Price={my_price} RSD, Discount={my_discount}%")
                
                if working_price != my_price:
                    print(f"  ❌ PRICE DIFFERENCE: {abs(working_price - my_price)} RSD")
                if working_discount != my_discount:
                    print(f"  ❌ DISCOUNT DIFFERENCE: {abs(working_discount - my_discount)}%")
    
    print_section("5. BACKEND ROUTING ANALYSIS")
    
    # Test backend health endpoints
    endpoints_to_test = [
        "/api/health",
        "/api/services", 
        "/api"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting endpoint: {endpoint}")
        
        # Test working version
        try:
            response = requests.get(f"{working_base}{endpoint}", timeout=10)
            print(f"  Working version: {response.status_code}")
            if response.status_code == 200 and endpoint == "/api/health":
                data = response.json()
                print(f"    Health status: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"  Working version error: {str(e)}")
        
        # Test my version
        try:
            response = requests.get(f"{my_base}{endpoint}", timeout=10)
            print(f"  My version: {response.status_code}")
            if response.status_code == 200 and endpoint == "/api/health":
                data = response.json()
                print(f"    Health status: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"  My version error: {str(e)}")
    
    print_section("6. EXTERNAL BOOKING SYSTEM ANALYSIS")
    
    # Check what external systems are being used
    external_systems = [
        "https://spabooking.emergent.host/api/services",
        "https://pozdrav-kako-si.emergent.host/api/services", 
        "https://wavy-parallax-hero.preview.emergentagent.com/api/services",
        "https://wavy-parallax-hero.preview.emergentagent.com/api/services"
    ]
    
    for system in external_systems:
        print(f"\nTesting external system: {system}")
        try:
            response = requests.get(system, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                couples_count = len([s for s in data if s.get('category') == 'Kartica Masaza za parove'])
                print(f"  Total services: {len(data)}")
                print(f"  Couples services: {couples_count}")
                
                # Check discount percentages
                if couples_count > 0:
                    couples_services = [s for s in data if s.get('category') == 'Kartica Masaza za parove']
                    discounts = [s.get('discount_percentage', 0) for s in couples_services]
                    avg_discount = sum(discounts) / len(discounts) if discounts else 0
                    print(f"  Average couples discount: {avg_discount:.1f}%")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print_section("7. ROOT CAUSE ANALYSIS")
    
    print("IDENTIFIED ISSUES:")
    
    # Issue 1: Different number of services
    if working_data and my_data:
        working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
        my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
        
        if len(working_couples) != len(my_couples):
            print(f"1. ❌ SERVICE COUNT MISMATCH:")
            print(f"   Working version: {len(working_couples)} couples services")
            print(f"   My version: {len(my_couples)} couples services")
            print(f"   Difference: {abs(len(working_couples) - len(my_couples))} services")
        
        # Issue 2: Different discount percentages
        working_discounts = [s.get('discount_percentage', 0) for s in working_couples]
        my_discounts = [s.get('discount_percentage', 0) for s in my_couples]
        
        working_avg = sum(working_discounts) / len(working_discounts) if working_discounts else 0
        my_avg = sum(my_discounts) / len(my_discounts) if my_discounts else 0
        
        if abs(working_avg - my_avg) > 0.1:
            print(f"2. ❌ DISCOUNT PERCENTAGE MISMATCH:")
            print(f"   Working version average: {working_avg:.1f}%")
            print(f"   My version average: {my_avg:.1f}%")
            print(f"   This is the KEY DIFFERENCE!")
        
        # Issue 3: Backend configuration
        print(f"3. ❌ BACKEND CONFIGURATION:")
        print(f"   My backend uses: https://spabooking.emergent.host")
        print(f"   Working version likely uses different external system")
        
        # Issue 4: Service synchronization
        working_names = set(s.get('name', '') for s in working_couples)
        my_names = set(s.get('name', '') for s in my_couples)
        missing_services = working_names - my_names
        
        if missing_services:
            print(f"4. ❌ MISSING SERVICES IN MY VERSION:")
            for service in sorted(missing_services):
                print(f"   - {service}")
    
    print_section("8. RECOMMENDATIONS TO FIX")
    
    print("TO MAKE MY VERSION WORK LIKE WORKING VERSION:")
    print("1. 🔧 Set all couples services discount_percentage to 0.0% (not 10.0%)")
    print("2. 🔧 Add missing services to match working version count")
    print("3. 🔧 Verify external booking system URL matches working version")
    print("4. 🔧 Check if working version applies discount differently (in frontend vs backend)")
    
    print_header("ANALYSIS COMPLETED")

if __name__ == "__main__":
    test_backend_endpoints()