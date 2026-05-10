#!/usr/bin/env python3
"""
SPA Booking Flow Test Suite
Testing the SPA booking flow for Bua Luang Thai Spa website

Test Cases from Review Request:
1. SPA Booking - Success Case
2. Verify response structure
3. Verify frontend hard lock
4. Verify Contact.js handles notify_status

Backend URL: https://wavy-parallax-hero.preview.emergentagent.com
"""

import requests
import json
import subprocess
import os
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://wavy-parallax-hero.preview.emergentagent.com"
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

def test_spa_booking_success():
    """Test Case 1: SPA Booking - Success Case"""
    try:
        print(f"\n{Colors.BLUE}=== Test 1: SPA Booking Success Case ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/spa/appointments"
        print(f"Testing: {url}")
        
        # Exact payload from review request
        payload = {
            "client_first_name": "Test",
            "client_last_name": "User",
            "client_phone": "0612345678",
            "client_email": "test@example.com",
            "appointment_date": "2025-12-26",
            "start_time": "2025-12-26T14:00:00",
            "category": "SPA",
            "service_id": "silky-body-ritual",
            "duration": 150,
            "notes": "SPA paket: Silky Body Ritual\nVarijanta: Bez masaze lica\n\nUkupno trajanje: 150 min\nUkupna cena: 9.200 RSD",
            "service_name": "SPA: Silky Body Ritual",
            "final_price": 9200,
            "original_price": 9200
        }
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Check required fields from review request
                required_fields = ['id', 'notify_status', 'status']
                missing_fields = []
                
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    log_test("SPA Booking Success", "FAIL", f"Missing required fields: {missing_fields}")
                    return False
                
                # Validate field values
                if not isinstance(data.get('id'), str):
                    log_test("SPA Booking Success", "FAIL", f"ID is not a string: {data.get('id')}")
                    return False
                
                if data.get('notify_status') not in ['sent', 'failed']:
                    log_test("SPA Booking Success", "FAIL", f"Invalid notify_status: {data.get('notify_status')}")
                    return False
                
                if data.get('status') != 'scheduled':
                    log_test("SPA Booking Success", "FAIL", f"Invalid status: {data.get('status')}")
                    return False
                
                log_test("SPA Booking Success", "PASS", f"ID: {data['id'][:8]}..., notify_status: {data['notify_status']}, status: {data['status']}")
                return True
                
            except json.JSONDecodeError as e:
                log_test("SPA Booking Success", "FAIL", f"Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                return False
        else:
            log_test("SPA Booking Success", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("SPA Booking Success", "FAIL", f"Exception: {str(e)}")
        return False

def test_response_structure():
    """Test Case 2: Verify response structure"""
    try:
        print(f"\n{Colors.BLUE}=== Test 2: Verify Response Structure ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/spa/appointments"
        
        # Test payload
        payload = {
            "client_first_name": "Structure",
            "client_last_name": "Test",
            "client_phone": "0612345679",
            "client_email": "structure@example.com",
            "appointment_date": "2025-12-27",
            "start_time": "2025-12-27T15:00:00",
            "category": "SPA",
            "service_id": "silky-body-ritual",
            "duration": 150,
            "notes": "Structure test",
            "service_name": "SPA: Silky Body Ritual",
            "final_price": 9200,
            "original_price": 9200
        }
        
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check structure requirements from review request
                structure_checks = {
                    'id': (str, 'UUID string'),
                    'notify_status': (str, 'sent or failed'),
                    'status': (str, 'status string'),
                    'client_first_name': (str, 'string'),
                    'client_last_name': (str, 'string')
                }
                
                # Check for final_total or final_price
                has_price_field = 'final_total' in data or 'final_price' in data
                if not has_price_field:
                    log_test("Response Structure", "FAIL", "Missing final_total or final_price field")
                    return False
                
                failed_checks = []
                for field, (expected_type, description) in structure_checks.items():
                    if field not in data:
                        failed_checks.append(f"{field} (missing)")
                    elif not isinstance(data[field], expected_type):
                        failed_checks.append(f"{field} (wrong type: {type(data[field]).__name__})")
                
                if failed_checks:
                    log_test("Response Structure", "FAIL", f"Structure issues: {', '.join(failed_checks)}")
                    return False
                
                log_test("Response Structure", "PASS", "All required fields present with correct types")
                return True
                
            except json.JSONDecodeError as e:
                log_test("Response Structure", "FAIL", f"Invalid JSON response: {e}")
                return False
        else:
            log_test("Response Structure", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("Response Structure", "FAIL", f"Exception: {str(e)}")
        return False

def test_frontend_hard_lock():
    """Test Case 3: Verify frontend hard lock"""
    try:
        print(f"\n{Colors.BLUE}=== Test 3: Verify Frontend Hard Lock ==={Colors.ENDC}")
        
        # Check for spa-dashboard-2.preview.emergentagent.com in api.js
        try:
            result = subprocess.run(
                ["grep", "-c", "spa-dashboard-2.preview.emergentagent.com", "/app/frontend/src/config/api.js"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                if count >= 1:
                    log_test("Frontend Hard Lock", "PASS", f"Found {count} occurrence(s) of spa-dashboard-2.preview.emergentagent.com")
                    return True
                else:
                    log_test("Frontend Hard Lock", "FAIL", "spa-dashboard-2.preview.emergentagent.com not found")
                    return False
            else:
                log_test("Frontend Hard Lock", "FAIL", "spa-dashboard-2.preview.emergentagent.com not found in api.js")
                return False
                
        except subprocess.TimeoutExpired:
            log_test("Frontend Hard Lock", "FAIL", "Grep command timed out")
            return False
        except Exception as e:
            log_test("Frontend Hard Lock", "FAIL", f"Error checking api.js: {str(e)}")
            return False
            
    except Exception as e:
        log_test("Frontend Hard Lock", "FAIL", f"Exception: {str(e)}")
        return False

def test_contact_notify_status():
    """Test Case 4: Verify Contact.js handles notify_status"""
    try:
        print(f"\n{Colors.BLUE}=== Test 4: Verify Contact.js handles notify_status ==={Colors.ENDC}")
        
        # Check for notify_status handling in Contact.js
        try:
            result = subprocess.run(
                ["grep", "-c", "notify_status", "/app/frontend/src/pages/Contact.js"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                if count >= 1:
                    # Get actual lines to verify proper handling
                    lines_result = subprocess.run(
                        ["grep", "-n", "notify_status", "/app/frontend/src/pages/Contact.js"],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if lines_result.returncode == 0:
                        lines = lines_result.stdout.strip().split('\n')
                        log_test("Contact.js notify_status", "PASS", f"Found {count} occurrence(s) of notify_status handling")
                        for line in lines[:3]:  # Show first 3 matches
                            print(f"    {line}")
                        return True
                    else:
                        log_test("Contact.js notify_status", "FAIL", "Could not retrieve notify_status lines")
                        return False
                else:
                    log_test("Contact.js notify_status", "FAIL", "notify_status not found in Contact.js")
                    return False
            else:
                log_test("Contact.js notify_status", "FAIL", "notify_status not found in Contact.js")
                return False
                
        except subprocess.TimeoutExpired:
            log_test("Contact.js notify_status", "FAIL", "Grep command timed out")
            return False
        except Exception as e:
            log_test("Contact.js notify_status", "FAIL", f"Error checking Contact.js: {str(e)}")
            return False
            
    except Exception as e:
        log_test("Contact.js notify_status", "FAIL", f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases and provide summary"""
    print(f"{Colors.BOLD}🏥 SPA Booking Flow Test Suite{Colors.ENDC}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("SPA Booking Success", test_spa_booking_success()))
    test_results.append(("Response Structure", test_response_structure()))
    test_results.append(("Frontend Hard Lock", test_frontend_hard_lock()))
    test_results.append(("Contact.js notify_status", test_contact_notify_status()))
    
    # Summary
    print(f"\n{Colors.BOLD}=== TEST SUMMARY ==={Colors.ENDC}")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}[{status}]{Colors.ENDC} {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.GREEN}✅ All SPA booking flow tests passed!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}❌ {total - passed} test(s) failed. SPA booking flow needs attention.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)