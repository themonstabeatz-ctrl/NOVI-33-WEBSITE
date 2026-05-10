#!/usr/bin/env python3
"""
Backend API Comparison Test
Compares discount functionality between working version and my version
"""

import requests
import json
from datetime import datetime
import sys

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def compare_apis():
    """Compare APIs between working version and my version"""
    
    print_header("BACKEND API COMPARISON TEST")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # API URLs
    working_api = "https://wavy-parallax-hero.preview.emergentagent.com/api/services"
    my_api = "https://wavy-parallax-hero.preview.emergentagent.com/api/services"
    
    print_section("1. API ENDPOINTS COMPARISON")
    print(f"Working version API: {working_api}")
    print(f"My version API: {my_api}")
    
    # Test working version API
    print_section("2. WORKING VERSION API RESPONSE")
    try:
        working_response = requests.get(working_api, timeout=10)
        print(f"Status Code: {working_response.status_code}")
        
        if working_response.status_code == 200:
            working_data = working_response.json()
            print(f"Total services: {len(working_data)}")
            
            # Filter for "Kartica Masaza za parove" category
            working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
            print(f"Couples massage services: {len(working_couples)}")
            
            if working_couples:
                print("\nFirst couples service example:")
                example = working_couples[0]
                print(f"  Name: {example.get('name', 'N/A')}")
                print(f"  Price: {example.get('price', 'N/A')}")
                print(f"  Discount %: {example.get('discount_percentage', 'N/A')}")
                print(f"  Category: {example.get('category', 'N/A')}")
        else:
            print(f"ERROR: {working_response.text}")
            working_data = []
            working_couples = []
            
    except Exception as e:
        print(f"ERROR accessing working version: {str(e)}")
        working_data = []
        working_couples = []
    
    # Test my version API
    print_section("3. MY VERSION API RESPONSE")
    try:
        my_response = requests.get(my_api, timeout=10)
        print(f"Status Code: {my_response.status_code}")
        
        if my_response.status_code == 200:
            my_data = my_response.json()
            print(f"Total services: {len(my_data)}")
            
            # Filter for "Kartica Masaza za parove" category
            my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
            print(f"Couples massage services: {len(my_couples)}")
            
            if my_couples:
                print("\nFirst couples service example:")
                example = my_couples[0]
                print(f"  Name: {example.get('name', 'N/A')}")
                print(f"  Price: {example.get('price', 'N/A')}")
                print(f"  Discount %: {example.get('discount_percentage', 'N/A')}")
                print(f"  Category: {example.get('category', 'N/A')}")
        else:
            print(f"ERROR: {my_response.text}")
            my_data = []
            my_couples = []
            
    except Exception as e:
        print(f"ERROR accessing my version: {str(e)}")
        my_data = []
        my_couples = []
    
    # Detailed comparison of couples services
    print_section("4. DETAILED COUPLES SERVICES COMPARISON")
    
    if working_couples and my_couples:
        print(f"Working version couples services: {len(working_couples)}")
        print(f"My version couples services: {len(my_couples)}")
        
        # Compare specific service: "Aroma terapija - 60 min"
        print_section("5. SPECIFIC SERVICE COMPARISON: 'Aroma terapija - 60 min'")
        
        working_aroma = None
        my_aroma = None
        
        for service in working_couples:
            if "Aroma terapija" in service.get('name', '') and "60 min" in service.get('name', ''):
                working_aroma = service
                break
        
        for service in my_couples:
            if "Aroma terapija" in service.get('name', '') and "60 min" in service.get('name', ''):
                my_aroma = service
                break
        
        print("WORKING VERSION:")
        if working_aroma:
            print(f"  Name: {working_aroma.get('name', 'N/A')}")
            print(f"  Price: {working_aroma.get('price', 'N/A')}")
            print(f"  Discount %: {working_aroma.get('discount_percentage', 'N/A')}")
            print(f"  Category: {working_aroma.get('category', 'N/A')}")
            print(f"  ID: {working_aroma.get('id', 'N/A')}")
        else:
            print("  Service not found!")
        
        print("\nMY VERSION:")
        if my_aroma:
            print(f"  Name: {my_aroma.get('name', 'N/A')}")
            print(f"  Price: {my_aroma.get('price', 'N/A')}")
            print(f"  Discount %: {my_aroma.get('discount_percentage', 'N/A')}")
            print(f"  Category: {my_aroma.get('category', 'N/A')}")
            print(f"  ID: {my_aroma.get('id', 'N/A')}")
        else:
            print("  Service not found!")
        
        # Compare all couples services
        print_section("6. ALL COUPLES SERVICES COMPARISON")
        
        print("WORKING VERSION SERVICES:")
        for i, service in enumerate(working_couples[:10], 1):  # Show first 10
            name = service.get('name', 'N/A')
            price = service.get('price', 'N/A')
            discount = service.get('discount_percentage', 'N/A')
            has_parovi = '[PAROVI]' in name
            print(f"  {i}. {name}")
            print(f"     Price: {price}, Discount: {discount}%, [PAROVI]: {has_parovi}")
        
        print(f"\nMY VERSION SERVICES:")
        for i, service in enumerate(my_couples[:10], 1):  # Show first 10
            name = service.get('name', 'N/A')
            price = service.get('price', 'N/A')
            discount = service.get('discount_percentage', 'N/A')
            has_parovi = '[PAROVI]' in name
            print(f"  {i}. {name}")
            print(f"     Price: {price}, Discount: {discount}%, [PAROVI]: {has_parovi}")
    
    # Check backend configuration
    print_section("7. BACKEND CONFIGURATION CHECK")
    
    # Check my backend .env
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            print("MY VERSION BACKEND .env:")
            for line in env_content.split('\n'):
                if 'BOOKING_API_URL' in line:
                    print(f"  {line}")
    except Exception as e:
        print(f"Error reading backend .env: {e}")
    
    # Check frontend .env
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            print("\nMY VERSION FRONTEND .env:")
            for line in env_content.split('\n'):
                if 'REACT_APP_BACKEND_URL' in line or 'REACT_APP_BOOKING_API_URL' in line:
                    print(f"  {line}")
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    
    # Summary of differences
    print_section("8. SUMMARY OF DIFFERENCES")
    
    differences = []
    
    if working_couples and my_couples:
        if len(working_couples) != len(my_couples):
            differences.append(f"Number of couples services: Working={len(working_couples)}, My={len(my_couples)}")
        
        # Check if services have [PAROVI] prefix
        working_parovi = sum(1 for s in working_couples if '[PAROVI]' in s.get('name', ''))
        my_parovi = sum(1 for s in my_couples if '[PAROVI]' in s.get('name', ''))
        
        if working_parovi != my_parovi:
            differences.append(f"Services with [PAROVI] prefix: Working={working_parovi}, My={my_parovi}")
        
        # Check discount percentages
        working_discounts = [s.get('discount_percentage', 0) for s in working_couples]
        my_discounts = [s.get('discount_percentage', 0) for s in my_couples]
        
        working_avg_discount = sum(working_discounts) / len(working_discounts) if working_discounts else 0
        my_avg_discount = sum(my_discounts) / len(my_discounts) if my_discounts else 0
        
        if abs(working_avg_discount - my_avg_discount) > 0.1:
            differences.append(f"Average discount: Working={working_avg_discount:.1f}%, My={my_avg_discount:.1f}%")
        
        # Check prices
        working_prices = [s.get('price', 0) for s in working_couples if isinstance(s.get('price'), (int, float))]
        my_prices = [s.get('price', 0) for s in my_couples if isinstance(s.get('price'), (int, float))]
        
        if working_prices and my_prices:
            working_avg_price = sum(working_prices) / len(working_prices)
            my_avg_price = sum(my_prices) / len(my_prices)
            
            if abs(working_avg_price - my_avg_price) > 100:
                differences.append(f"Average price: Working={working_avg_price:.0f} RSD, My={my_avg_price:.0f} RSD")
    
    if differences:
        print("FOUND DIFFERENCES:")
        for diff in differences:
            print(f"  ❌ {diff}")
    else:
        print("✅ No major differences found in couples services")
    
    print_section("9. RECOMMENDATIONS")
    
    if not working_couples:
        print("⚠️  Cannot access working version API - check network connectivity")
    elif not my_couples:
        print("⚠️  Cannot access my version API - check backend service")
    elif len(working_couples) != len(my_couples):
        print("🔧 Service count mismatch - check service synchronization")
    elif working_parovi == 0 and my_parovi > 0:
        print("🔧 Working version has no [PAROVI] prefix - this might be the difference")
    elif working_parovi > 0 and my_parovi == 0:
        print("🔧 My version missing [PAROVI] prefix - add prefix to service names")
    else:
        print("✅ Services appear to be synchronized")
    
    print_header("TEST COMPLETED")
    return differences

if __name__ == "__main__":
    try:
        differences = compare_apis()
        if differences:
            sys.exit(1)  # Exit with error if differences found
        else:
            sys.exit(0)  # Exit successfully if no differences
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)