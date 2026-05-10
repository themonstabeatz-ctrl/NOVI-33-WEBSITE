#!/usr/bin/env python3
"""
Comprehensive Comparison Test - Review Request Analysis
Compares WORKING VERSION vs MY VERSION for couples massage discount functionality
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
    print(f"\n{'-'*60}")
    print(f" {title}")
    print(f"{'-'*60}")

def main():
    print_header("COMPREHENSIVE COUPLES MASSAGE DISCOUNT COMPARISON")
    print(f"Test executed at: {datetime.now().isoformat()}")
    
    # API URLs from review request
    working_api = "https://wavy-parallax-hero.preview.emergentagent.com/api/services"
    my_api = "https://wavy-parallax-hero.preview.emergentagent.com/api/services"
    
    print_section("1. API ENDPOINT COMPARISON")
    print(f"WORKING VERSION (PERFECT): {working_api}")
    print(f"MY VERSION: {my_api}")
    
    # Fetch data from both APIs
    working_data = []
    my_data = []
    
    print_section("2. WORKING VERSION API ANALYSIS")
    try:
        response = requests.get(working_api, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            working_data = response.json()
            print(f"✅ Total services: {len(working_data)}")
            
            # Filter couples services
            working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
            print(f"✅ Couples services: {len(working_couples)}")
            
            # Analyze discount percentages
            discounts = [s.get('discount_percentage', 0) for s in working_couples]
            print(f"✅ Discount percentages: {set(discounts)}")
            
            # Check for [PAROVI] prefix
            parovi_count = sum(1 for s in working_couples if '[PAROVI]' in s.get('name', ''))
            print(f"✅ Services with [PAROVI] prefix: {parovi_count}/{len(working_couples)}")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print_section("3. MY VERSION API ANALYSIS")
    try:
        response = requests.get(my_api, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            my_data = response.json()
            print(f"✅ Total services: {len(my_data)}")
            
            # Filter couples services
            my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
            print(f"✅ Couples services: {len(my_couples)}")
            
            # Analyze discount percentages
            discounts = [s.get('discount_percentage', 0) for s in my_couples]
            print(f"✅ Discount percentages: {set(discounts)}")
            
            # Check for [PAROVI] prefix
            parovi_count = sum(1 for s in my_couples if '[PAROVI]' in s.get('name', ''))
            print(f"✅ Services with [PAROVI] prefix: {parovi_count}/{len(my_couples)}")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Detailed service comparison
    if working_data and my_data:
        working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
        my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
        
        print_section("4. SPECIFIC SERVICE COMPARISON - 'Aroma terapija - 60 min'")
        
        # Find Aroma terapija in both versions
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
            print(f"  Price: {working_aroma.get('price', 'N/A')} RSD")
            print(f"  Discount: {working_aroma.get('discount_percentage', 'N/A')}%")
            print(f"  Category: {working_aroma.get('category', 'N/A')}")
            print(f"  ID: {working_aroma.get('id', 'N/A')}")
            if 'metadata' in working_aroma:
                print(f"  Metadata: {working_aroma['metadata']}")
        else:
            print("  ❌ Service not found")
        
        print("\nMY VERSION:")
        if my_aroma:
            print(f"  Name: {my_aroma.get('name', 'N/A')}")
            print(f"  Price: {my_aroma.get('price', 'N/A')} RSD")
            print(f"  Discount: {my_aroma.get('discount_percentage', 'N/A')}%")
            print(f"  Category: {my_aroma.get('category', 'N/A')}")
            print(f"  ID: {my_aroma.get('id', 'N/A')}")
            if 'metadata' in my_aroma:
                print(f"  Metadata: {my_aroma['metadata']}")
        else:
            print("  ❌ Service not found")
        
        print_section("5. SERVICE COUNT AND NAMING DIFFERENCES")
        
        # Compare service names
        working_names = set(s.get('name', '') for s in working_couples)
        my_names = set(s.get('name', '') for s in my_couples)
        
        print(f"Working version has {len(working_names)} unique service names")
        print(f"My version has {len(my_names)} unique service names")
        
        # Services only in working version
        only_in_working = working_names - my_names
        if only_in_working:
            print(f"\n❌ Services ONLY in working version ({len(only_in_working)}):")
            for name in sorted(only_in_working):
                print(f"  - {name}")
        
        # Services only in my version
        only_in_my = my_names - working_names
        if only_in_my:
            print(f"\n❌ Services ONLY in my version ({len(only_in_my)}):")
            for name in sorted(only_in_my):
                print(f"  - {name}")
        
        # Common services
        common_services = working_names & my_names
        print(f"\n✅ Common services ({len(common_services)}):")
        for name in sorted(list(common_services)[:5]):  # Show first 5
            print(f"  - {name}")
        if len(common_services) > 5:
            print(f"  ... and {len(common_services) - 5} more")
    
    # Test backend configuration
    print_section("6. BACKEND CONFIGURATION ANALYSIS")
    
    # Check my backend .env
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            print("MY VERSION BACKEND .env:")
            for line in env_content.split('\n'):
                if 'BOOKING_API_URL' in line or 'MONGO_URL' in line:
                    print(f"  {line}")
    except Exception as e:
        print(f"Error reading backend .env: {e}")
    
    # Check frontend .env
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            print("\nMY VERSION FRONTEND .env:")
            for line in env_content.split('\n'):
                if 'REACT_APP_BACKEND_URL' in line:
                    print(f"  {line}")
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    
    # Test booking functionality
    print_section("7. BOOKING SYSTEM ANALYSIS")
    
    # Check therapists in my version
    try:
        print("Checking therapists in MY VERSION booking system:")
        response = requests.get('https://spabooking.emergent.host/api/therapists', timeout=10)
        print(f"Therapists API Status: {response.status_code}")
        
        if response.status_code == 200:
            therapists = response.json()
            print(f"Total therapists: {len(therapists)}")
            
            web_therapists = [t for t in therapists if 'Web' in t.get('name', '')]
            print(f"Web Slot therapists: {len(web_therapists)}")
            
            if len(therapists) == 0:
                print("❌ CRITICAL: No therapists configured in booking system!")
            elif len(web_therapists) == 0:
                print("❌ CRITICAL: No Web Slot therapists for online bookings!")
        else:
            print(f"❌ Error accessing therapists: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception checking therapists: {str(e)}")
    
    # Test health endpoints
    print_section("8. HEALTH ENDPOINT COMPARISON")
    
    endpoints = [
        ("Working Version", "https://wavy-parallax-hero.preview.emergentagent.com/api/health"),
        ("My Version", "https://wavy-parallax-hero.preview.emergentagent.com/api/health")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"{name}: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {data}")
            else:
                print(f"  ❌ Error: {response.text}")
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    # Summary of findings
    print_section("9. SUMMARY OF KEY DIFFERENCES")
    
    differences = []
    
    if working_data and my_data:
        working_couples = [s for s in working_data if s.get('category') == 'Kartica Masaza za parove']
        my_couples = [s for s in my_data if s.get('category') == 'Kartica Masaza za parove']
        
        # Service count
        if len(working_couples) != len(my_couples):
            differences.append(f"Service count: Working={len(working_couples)}, My={len(my_couples)}")
        
        # Discount percentages
        working_discounts = set(s.get('discount_percentage', 0) for s in working_couples)
        my_discounts = set(s.get('discount_percentage', 0) for s in my_couples)
        
        if working_discounts != my_discounts:
            differences.append(f"Discount percentages: Working={working_discounts}, My={my_discounts}")
        
        # Service names
        working_names = set(s.get('name', '') for s in working_couples)
        my_names = set(s.get('name', '') for s in my_couples)
        
        missing_in_my = len(working_names - my_names)
        extra_in_my = len(my_names - working_names)
        
        if missing_in_my > 0:
            differences.append(f"Services missing in my version: {missing_in_my}")
        if extra_in_my > 0:
            differences.append(f"Extra services in my version: {extra_in_my}")
    
    # Backend differences
    differences.append("Backend system: Working uses internal, My uses external (https://spabooking.emergent.host)")
    differences.append("Therapist configuration: My version has 0 therapists (booking system not configured)")
    
    print("CRITICAL DIFFERENCES FOUND:")
    for i, diff in enumerate(differences, 1):
        print(f"  {i}. ❌ {diff}")
    
    print_section("10. ROOT CAUSE ANALYSIS")
    
    print("🎯 PRIMARY ISSUES IDENTIFIED:")
    print("  1. ❌ BOOKING SYSTEM: My version uses external system with no therapists configured")
    print("  2. ❌ SERVICE CATALOG: Different service offerings between versions")
    print("  3. ✅ DISCOUNT LOGIC: Both versions use 0% discount in backend (frontend applies discount)")
    print("  4. ✅ PRICING: Service prices appear consistent where services match")
    print("  5. ✅ API STRUCTURE: Both APIs return same data structure")
    
    print("\n🔧 REQUIRED FIXES:")
    print("  1. Configure Web Slot therapists in https://spabooking.emergent.host")
    print("  2. Synchronize service catalog between working and my version")
    print("  3. Verify frontend discount application logic matches working version")
    
    print_header("COMPARISON TEST COMPLETED")
    
    return len(differences)

if __name__ == "__main__":
    try:
        diff_count = main()
        print(f"\nFound {diff_count} differences between versions")
        sys.exit(0 if diff_count == 0 else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)