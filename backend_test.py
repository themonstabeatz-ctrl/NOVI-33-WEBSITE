#!/usr/bin/env python3
"""
Backend Test Suite for Hard Lock API Configuration
Testing the Bua Luang Thai Spa booking website backend integration

Test Cases:
1. Backend Health Check
2. SPA Services Endpoint  
3. Massage Appointments List
4. SPA Appointments List
5. Verify Hard Lock in Frontend Code
6. Verify .env Configuration
"""

import requests
import json
import subprocess
import os
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://gold-line-fixer.preview.emergentagent.com"
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

def test_backend_health_check():
    """Test Case 1: Backend Health Check - /api/services"""
    try:
        print(f"\n{Colors.BLUE}=== Test 1: Backend Health Check ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/services"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                log_test("Backend Health Check", "PASS", f"Returned {len(data)} services")
                return True
            else:
                log_test("Backend Health Check", "FAIL", "Empty or invalid response format")
                return False
        else:
            log_test("Backend Health Check", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("Backend Health Check", "FAIL", f"Exception: {str(e)}")
        return False

def test_spa_services_endpoint():
    """Test Case 2: SPA Services Endpoint - /api/spa/services"""
    try:
        print(f"\n{Colors.BLUE}=== Test 2: SPA Services Endpoint ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/spa/services"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            # Check for SPA zone prices (Sauna, Jacuzzi, Parno kupatilo)
            spa_services = ["Sauna", "Jacuzzi", "Parno kupatilo"]
            found_services = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'name' in item:
                        for spa_service in spa_services:
                            if spa_service.lower() in item['name'].lower():
                                found_services.append(spa_service)
            
            if found_services:
                log_test("SPA Services Endpoint", "PASS", f"Found SPA services: {', '.join(found_services)}")
                return True
            else:
                log_test("SPA Services Endpoint", "FAIL", "No SPA zone services found (Sauna, Jacuzzi, Parno kupatilo)")
                return False
        else:
            log_test("SPA Services Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("SPA Services Endpoint", "FAIL", f"Exception: {str(e)}")
        return False

def test_massage_appointments():
    """Test Case 3: Massage Appointments List - /api/appointments?limit=5"""
    try:
        print(f"\n{Colors.BLUE}=== Test 3: Massage Appointments List ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/appointments?limit=5"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("Massage Appointments List", "PASS", f"Returned {len(data)} appointments")
                
                # Check for client info and pricing in first appointment if available
                if len(data) > 0 and isinstance(data[0], dict):
                    first_appointment = data[0]
                    has_client_info = any(key in first_appointment for key in ['client_name', 'client_first_name', 'client_last_name'])
                    has_pricing = any(key in first_appointment for key in ['price', 'total_price', 'final_price'])
                    
                    if has_client_info:
                        print(f"    ✓ Client info found in appointments")
                    if has_pricing:
                        print(f"    ✓ Pricing info found in appointments")
                
                return True
            else:
                log_test("Massage Appointments List", "FAIL", "Invalid response format - expected list")
                return False
        else:
            log_test("Massage Appointments List", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("Massage Appointments List", "FAIL", f"Exception: {str(e)}")
        return False

def test_spa_appointments():
    """Test Case 4: SPA Appointments List - /api/spa/appointments"""
    try:
        print(f"\n{Colors.BLUE}=== Test 4: SPA Appointments List ==={Colors.ENDC}")
        
        url = f"{BACKEND_URL}/api/spa/appointments"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("SPA Appointments List", "PASS", f"Returned {len(data)} SPA appointments")
                
                # Check for services_snapshot with ritual names
                ritual_names = ["Silky Body Ritual", "Deep Renewal Ritual"]
                found_rituals = []
                
                for appointment in data:
                    if isinstance(appointment, dict) and 'services_snapshot' in appointment:
                        services_snapshot = appointment['services_snapshot']
                        if isinstance(services_snapshot, (list, dict)):
                            snapshot_str = str(services_snapshot).lower()
                            for ritual in ritual_names:
                                if ritual.lower() in snapshot_str:
                                    found_rituals.append(ritual)
                
                if found_rituals:
                    print(f"    ✓ Found ritual names: {', '.join(set(found_rituals))}")
                
                return True
            else:
                log_test("SPA Appointments List", "FAIL", "Invalid response format - expected list")
                return False
        else:
            log_test("SPA Appointments List", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("SPA Appointments List", "FAIL", f"Exception: {str(e)}")
        return False

def test_hard_lock_frontend():
    """Test Case 5: Verify Hard Lock in Frontend Code"""
    try:
        print(f"\n{Colors.BLUE}=== Test 5: Verify Hard Lock in Frontend Code ==={Colors.ENDC}")
        
        # Check for spa-dashboard-2 in api.js
        try:
            result = subprocess.run(
                ["grep", "-RIn", "spa-dashboard-2", "/app/frontend/src/config/api.js"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and "spa-dashboard-2" in result.stdout:
                log_test("Hard Lock Configuration", "PASS", "spa-dashboard-2 found in api.js")
                spa_dashboard_found = True
            else:
                log_test("Hard Lock Configuration", "FAIL", "spa-dashboard-2 NOT found in api.js")
                spa_dashboard_found = False
        except Exception as e:
            log_test("Hard Lock Configuration", "FAIL", f"Error checking api.js: {str(e)}")
            spa_dashboard_found = False
        
        # Check for forbidden backends
        try:
            result = subprocess.run(
                ["grep", "-RIn", "massage-scheduler\\|massage-app-4", "/app/frontend/src", "--include=*.js"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:  # No matches found (good)
                log_test("Forbidden Backend Check", "PASS", "No forbidden backends found")
                no_forbidden_backends = True
            else:
                log_test("Forbidden Backend Check", "FAIL", f"Forbidden backends found: {result.stdout[:200]}")
                no_forbidden_backends = False
        except Exception as e:
            log_test("Forbidden Backend Check", "FAIL", f"Error checking forbidden backends: {str(e)}")
            no_forbidden_backends = False
        
        return spa_dashboard_found and no_forbidden_backends
        
    except Exception as e:
        log_test("Hard Lock Frontend Check", "FAIL", f"Exception: {str(e)}")
        return False

def test_env_configuration():
    """Test Case 6: Verify .env Configuration"""
    try:
        print(f"\n{Colors.BLUE}=== Test 6: Verify .env Configuration ==={Colors.ENDC}")
        
        env_file = "/app/frontend/.env"
        
        if not os.path.exists(env_file):
            log_test("Environment Configuration", "FAIL", f".env file not found at {env_file}")
            return False
        
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        expected_url = "https://gold-line-fixer.preview.emergentagent.com"
        
        if f"REACT_APP_BACKEND_URL={expected_url}" in env_content:
            log_test("Environment Configuration", "PASS", f"Correct REACT_APP_BACKEND_URL found")
            return True
        else:
            log_test("Environment Configuration", "FAIL", f"Expected REACT_APP_BACKEND_URL={expected_url} not found")
            print(f"    Current .env content:")
            for line in env_content.split('\n'):
                if 'BACKEND_URL' in line:
                    print(f"    {line}")
            return False
            
    except Exception as e:
        log_test("Environment Configuration", "FAIL", f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases and provide summary"""
    print(f"{Colors.BOLD}🔒 Hard Lock API Configuration Test Suite{Colors.ENDC}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Backend Health Check", test_backend_health_check()))
    test_results.append(("SPA Services Endpoint", test_spa_services_endpoint()))
    test_results.append(("Massage Appointments List", test_massage_appointments()))
    test_results.append(("SPA Appointments List", test_spa_appointments()))
    test_results.append(("Hard Lock Frontend", test_hard_lock_frontend()))
    test_results.append(("Environment Configuration", test_env_configuration()))
    
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
        print(f"{Colors.GREEN}✅ All tests passed! Hard Lock implementation is working correctly.{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}❌ {total - passed} test(s) failed. Hard Lock implementation needs attention.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)