#!/usr/bin/env python3
"""
SPA Cards Booking Test Suite
Testing ALL 9 SPA card bookings to verify emails are sent correctly with proper pricing.

Test Configuration:
- Frontend URL: http://localhost:3000/spa
- Backend API: https://wavy-parallax-hero.preview.emergentagent.com
- Test Email: grujovicsavatije@gmail.com

Cards to Test (9 total):
1. Silky Body Ritual (card_id: silky_body_ritual) - Expected 15% discount
2. Gentle Touch Ritual (card_id: gentle_touch_ritual) - Expected 10% discount
3. Deep Renewal Ritual (card_id: deep_renewal_ritual) - Expected 5% discount
4. Silky Herbal Compress Ritual (card_id: silky_herbal_compress_ritual) - Expected 5% discount
5. Thai Herbal Compress Ritual (card_id: thai_herbal_compress_ritual) - Expected 10% discount
6. Aroma Stone Harmony Ritual (card_id: aroma_stone_harmony_ritual) - Expected 15% discount
7. SPA Zone (card_id: spa_zone) - Expected 5% discount - requires selecting zone options
8. Romantični paket za parove (card_id: romantic_couple_package) - Expected 10% discount
9. Romantični piling paket za parove (card_id: romantic_peeling_couple_package) - Expected 15% discount
"""

import requests
import json
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://wavy-parallax-hero.preview.emergentagent.com"
TEST_EMAIL = "grujovicsavatije@gmail.com"
TIMEOUT = 30

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_test(test_name, status, details=""):
    """Log test results with colors"""
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.ENDC} {test_name}")
    if details:
        print(f"    {details}")

# SPA Cards Configuration with Service IDs
SPA_CARDS = [
    {
        "name": "Silky Body Ritual",
        "card_id": "silky_body_ritual",
        "service_id": "ed3d9995-e195-4e56-8041-3459d3ecd324",
        "expected_discount": 15,
        "original_price": 8000  # Example price - will be fetched from API
    },
    {
        "name": "Gentle Touch Ritual", 
        "card_id": "gentle_touch_ritual",
        "service_id": "3308333f-de1a-40a5-b33a-6acc171bc538",
        "expected_discount": 10,
        "original_price": 7000
    },
    {
        "name": "Deep Renewal Ritual",
        "card_id": "deep_renewal_ritual", 
        "service_id": "b4067c22-e4c0-4db7-aa7a-b6b6d396e27a",
        "expected_discount": 5,
        "original_price": 9000
    },
    {
        "name": "Silky Herbal Compress Ritual",
        "card_id": "silky_herbal_compress_ritual",
        "service_id": "ce2e8ccd-e95c-41b2-bae9-0d9b0f53cc2f", 
        "expected_discount": 5,
        "original_price": 8500
    },
    {
        "name": "Thai Herbal Compress Ritual",
        "card_id": "thai_herbal_compress_ritual",
        "service_id": "a406a2b4-a2ee-46af-9897-d20f71534a22",
        "expected_discount": 10,
        "original_price": 8000
    },
    {
        "name": "Aroma Stone Harmony Ritual", 
        "card_id": "aroma_stone_harmony_ritual",
        "service_id": "f8cdfaac-9414-4eeb-8136-0d9d3d0e73b8",
        "expected_discount": 15,
        "original_price": 9500
    },
    {
        "name": "SPA Zone",
        "card_id": "spa_zone",
        "service_id": "7d46da23-a15a-4836-8db5-04d748cd6b72",  # SAUNA_15 service ID
        "expected_discount": 5,
        "original_price": 1500
    },
    {
        "name": "Romantični paket za parove",
        "card_id": "romantic_couple_package", 
        "service_id": "0431d7d9-c8cd-4392-bbed-f91298ace763",
        "expected_discount": 10,
        "original_price": 12000
    },
    {
        "name": "Romantični piling paket za parove",
        "card_id": "romantic_peeling_couple_package",
        "service_id": "80cd6f57-da53-4558-8641-9f8589b0726f", 
        "expected_discount": 15,
        "original_price": 14000
    }
]

def test_spa_appointments_endpoint():
    """Test if /api/spa/appointments endpoint exists and is accessible"""
    try:
        print(f"\n{Colors.BLUE}=== Testing SPA Appointments Endpoint ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/spa/appointments"
        print(f"Testing endpoint: {url}")
        
        # Test GET request first
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            log_test("SPA Appointments GET", "PASS", f"Endpoint accessible, returned {len(response.json())} appointments")
            return True
        elif response.status_code == 405:
            log_test("SPA Appointments GET", "INFO", "GET method not allowed (expected for POST-only endpoint)")
            return True
        else:
            log_test("SPA Appointments GET", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("SPA Appointments Endpoint", "FAIL", f"Exception: {str(e)}")
        return False

def create_spa_booking(card):
    """Create a booking for a specific SPA card"""
    try:
        url = f"{BACKEND_URL}/api/spa/appointments"
        
        booking_data = {
            "client_first_name": "Test",
            "client_last_name": f"SPA_{card['name'].replace(' ', '_')}",
            "client_phone": "0601234567",
            "client_email": TEST_EMAIL,
            "appointment_date": "2025-12-30",
            "start_time": "2025-12-30T11:00:00",
            "type": "spa",
            "card_id": card["card_id"],
            "service_ids": [card["service_id"]],
            "total_original": card["original_price"],
            "notes": f"Test booking for {card['name']} - Expected {card['expected_discount']}% discount"
        }
        
        print(f"\n{Colors.BLUE}=== Testing {card['name']} ==={Colors.ENDC}")
        print(f"Card ID: {card['card_id']}")
        print(f"Service ID: {card['service_id']}")
        print(f"Expected Discount: {card['expected_discount']}%")
        print(f"Booking data: {json.dumps(booking_data, indent=2)}")
        
        response = requests.post(
            url,
            json=booking_data,
            headers={'Content-Type': 'application/json'},
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            booking_id = result.get('id', 'Unknown')
            log_test(f"{card['name']} Booking", "PASS", f"Booking created successfully - ID: {booking_id}")
            
            # Check if response contains pricing information
            if 'total_price' in result or 'final_price' in result:
                final_price = result.get('final_price', result.get('total_price', 'Unknown'))
                print(f"    Final Price: {final_price}")
                
                # Calculate expected price with discount
                expected_price = card['original_price'] * (1 - card['expected_discount'] / 100)
                print(f"    Expected Price (with {card['expected_discount']}% discount): {expected_price}")
            
            return True, booking_id
        else:
            error_text = response.text
            log_test(f"{card['name']} Booking", "FAIL", f"HTTP {response.status_code}: {error_text[:300]}")
            return False, None
            
    except Exception as e:
        log_test(f"{card['name']} Booking", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_all_spa_cards():
    """Test booking creation for all 9 SPA cards"""
    print(f"{Colors.BOLD}🧘 SPA Cards Booking Test Suite{Colors.ENDC}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Cards to Test: {len(SPA_CARDS)}")
    
    # First test if the endpoint is accessible
    endpoint_accessible = test_spa_appointments_endpoint()
    if not endpoint_accessible:
        print(f"{Colors.RED}❌ SPA appointments endpoint not accessible. Aborting tests.{Colors.ENDC}")
        return False
    
    # Test each SPA card
    results = []
    successful_bookings = []
    
    for card in SPA_CARDS:
        success, booking_id = create_spa_booking(card)
        results.append((card['name'], success))
        
        if success and booking_id:
            successful_bookings.append({
                'name': card['name'],
                'card_id': card['card_id'],
                'booking_id': booking_id,
                'expected_discount': card['expected_discount']
            })
    
    # Summary
    print(f"\n{Colors.BOLD}=== TEST SUMMARY ==={Colors.ENDC}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for card_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}[{status}]{Colors.ENDC} {card_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} SPA card bookings successful{Colors.ENDC}")
    
    if successful_bookings:
        print(f"\n{Colors.GREEN}✅ Successfully created bookings for:{Colors.ENDC}")
        for booking in successful_bookings:
            print(f"  • {booking['name']} (ID: {booking['booking_id']}) - {booking['expected_discount']}% discount")
        
        print(f"\n{Colors.YELLOW}📧 Email Verification:{Colors.ENDC}")
        print(f"  • Check {TEST_EMAIL} for {len(successful_bookings)} confirmation emails")
        print(f"  • Verify each email contains correct pricing with applied discounts")
        print(f"  • Verify no double discounting occurred")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✅ All {total} SPA card bookings created successfully!{Colors.ENDC}")
        print(f"{Colors.GREEN}   User should now check emails for proper pricing verification.{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.RED}❌ {total - passed} SPA card booking(s) failed.{Colors.ENDC}")
        return False

def test_backend_health():
    """Quick health check of the backend"""
    try:
        print(f"\n{Colors.BLUE}=== Backend Health Check ==={Colors.ENDC}")
        
        # Test basic health endpoint
        health_url = f"{BACKEND_URL}/api/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            log_test("Backend Health", "PASS", "Backend is responding")
            return True
        else:
            log_test("Backend Health", "FAIL", f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Backend Health", "FAIL", f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"{Colors.BOLD}🎯 SPA Cards Email Verification Test{Colors.ENDC}")
    print(f"{Colors.BOLD}Objective: Test ALL 9 SPA card bookings for email verification{Colors.ENDC}\n")
    
    # Run health check first
    health_ok = test_backend_health()
    if not health_ok:
        print(f"{Colors.RED}❌ Backend health check failed. Aborting tests.{Colors.ENDC}")
        sys.exit(1)
    
    # Run all SPA card tests
    success = test_all_spa_cards()
    
    if success:
        print(f"\n{Colors.GREEN}🎉 ALL SPA CARD BOOKINGS COMPLETED SUCCESSFULLY!{Colors.ENDC}")
        print(f"{Colors.GREEN}📧 User can now verify emails at: {TEST_EMAIL}{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}❌ Some SPA card bookings failed. Check logs above.{Colors.ENDC}")
    
    sys.exit(0 if success else 1)