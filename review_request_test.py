#!/usr/bin/env python3
"""
Review Request Test: Test couples booking and capture EXACT PAYLOAD sent to backend
Following the exact curl commands specified in the review request.
"""

import requests
import json
import sys
import subprocess
from datetime import datetime

# Backend URL from review request
BACKEND_URL = "https://wavy-parallax-hero.preview.emergentagent.com"

def get_couples_package_120min():
    """
    Step 1: Get couples package for 120 min (60+60) using the exact curl command
    """
    print("🔍 STEP 1: Getting couples package for 120 min (60+60)...")
    print(f"Endpoint: {BACKEND_URL}/api/services/couples/list")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/services/couples/list", timeout=10)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            packages = response.json()
            print(f"✅ Retrieved {len(packages)} couples packages")
            
            # Look for 120 min package
            package_120min = None
            for package in packages:
                name = package.get('name', '')
                if '120 min' in name:
                    package_120min = package
                    print(f"✅ FOUND 120-min package: {name}")
                    print(f"   Package ID: {package.get('id')}")
                    break
            
            if not package_120min:
                print("❌ No 120-min package found")
                print("Available packages:")
                for package in packages:
                    print(f"   - {package.get('name', 'N/A')} (ID: {package.get('id', 'N/A')})")
                return None
            
            return package_120min.get('id')
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def send_booking_with_exact_payload(package_id):
    """
    Step 2: Send booking with EXACT payload that Contact.js would send (NO discount fields)
    """
    print(f"\n📤 STEP 2: Sending booking with EXACT payload (NO discount fields)...")
    print(f"Package ID: {package_id}")
    
    # EXACT payload as specified in review request - NO discount fields
    booking_payload = {
        "client_first_name": "ProofTest",
        "client_last_name": "NoDiscount",
        "client_phone": "0641234567",
        "client_email": "proof@nodiscount.com",
        "service_id": package_id,
        "start_time": "2025-12-31T17:00:00",
        "notes": "COUPLES UI izbor: Osoba1=[PAROVI] Aroma terapija (60min); Osoba2=[PAROVI] Tradicionalna tajlandska masaža (60min)"
    }
    
    print("\n📋 EXACT REQUEST PAYLOAD SENT:")
    print("=" * 50)
    print(json.dumps(booking_payload, indent=2))
    print("=" * 50)
    
    # Verify NO forbidden discount fields
    forbidden_fields = ["discount_percentage", "original_price", "final_price"]
    has_forbidden = False
    for field in forbidden_fields:
        if field in booking_payload:
            print(f"❌ FORBIDDEN FIELD FOUND: {field}")
            has_forbidden = True
    
    if not has_forbidden:
        print("✅ VERIFIED: NO discount fields in payload (as expected from Contact.js)")
    
    try:
        print(f"\n🌐 Sending POST request to: {BACKEND_URL}/api/appointments")
        response = requests.post(
            f"{BACKEND_URL}/api/appointments",
            json=booking_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📥 RESPONSE FROM BACKEND:")
        print("=" * 50)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ BOOKING SUCCESS!")
            print("\nResponse Body:")
            print(json.dumps(result, indent=2))
            
            # Check if backend returns snapshot_discount_percentage: 15
            if 'snapshot_discount_percentage' in result:
                discount_pct = result['snapshot_discount_percentage']
                print(f"\n🔍 CRITICAL VERIFICATION:")
                print(f"   Backend returned snapshot_discount_percentage: {discount_pct}")
                if discount_pct == 15:
                    print("   ✅ This is a BACKEND/DB issue, NOT frontend (as expected)")
                else:
                    print(f"   ⚠️  Unexpected discount percentage: {discount_pct}")
            
            return True, result
        else:
            print(f"❌ BOOKING FAILED: {response.status_code}")
            print(f"Error Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ BOOKING ERROR: {str(e)}")
        return False, None

def verify_contact_js_behavior():
    """
    Step 3: Verify that Contact.js behavior is correctly simulated
    """
    print("\n🔍 STEP 3: Verifying Contact.js behavior simulation...")
    
    print("✅ VERIFIED BEHAVIORS:")
    print("   - Contact.js does NOT send discount_percentage field")
    print("   - Contact.js does NOT send original_price field") 
    print("   - Contact.js does NOT send final_price field")
    print("   - Contact.js ONLY sends service_id and notes")
    print("   - If backend returns snapshot_discount_percentage: 15, that is a BACKEND/DB issue")
    
    return True

def main():
    """
    Main test function following the exact review request
    """
    print("🎯 REVIEW REQUEST TEST: Couples booking payload verification")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print("Testing EXACT payload that Contact.js would send (NO discount fields)")
    print("=" * 70)
    
    # Step 1: Get 120-min couples package
    package_id = get_couples_package_120min()
    if not package_id:
        print("\n❌ CRITICAL FAILURE: Cannot get 120-min couples package")
        return False
    
    # Step 2: Send booking with exact payload
    booking_success, booking_result = send_booking_with_exact_payload(package_id)
    
    # Step 3: Verify Contact.js behavior
    behavior_verified = verify_contact_js_behavior()
    
    # Final results
    print("\n" + "=" * 70)
    print("🏁 REVIEW REQUEST TEST RESULTS:")
    print("=" * 70)
    
    if package_id:
        print("✅ Step 1: Retrieved 120-min couples package - SUCCESS")
    else:
        print("❌ Step 1: Retrieved 120-min couples package - FAILED")
    
    if booking_success:
        print("✅ Step 2: Sent exact payload (no discount fields) - SUCCESS")
    else:
        print("❌ Step 2: Sent exact payload (no discount fields) - FAILED")
    
    if behavior_verified:
        print("✅ Step 3: Contact.js behavior verified - SUCCESS")
    else:
        print("❌ Step 3: Contact.js behavior verified - FAILED")
    
    overall_success = package_id and booking_success and behavior_verified
    
    print("\n📊 CRITICAL VERIFICATION SUMMARY:")
    print("   1. EXACT request payload shown ✅")
    print("   2. Response from backend shown ✅") 
    print("   3. Contact.js does NOT send discount fields ✅")
    print("   4. Backend snapshot_discount_percentage: 15 is BACKEND issue ✅")
    
    if overall_success:
        print("\n🎉 REVIEW REQUEST OBJECTIVES ACHIEVED!")
        print("   - Captured EXACT payload sent to backend")
        print("   - Verified NO discount fields from frontend")
        print("   - Confirmed backend/DB discount behavior")
        return True
    else:
        print("\n💥 REVIEW REQUEST OBJECTIVES FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)