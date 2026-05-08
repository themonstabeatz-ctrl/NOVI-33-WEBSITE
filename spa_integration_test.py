#!/usr/bin/env python3
"""
Backend API Test Suite for Review Request
Testing endpoints on https://gold-line-fixer.preview.emergentagent.com

Test Cases:
1. GET /api/health - should return {"status":"healthy"} with 200
2. GET /api/services - should return array of services with 200
3. GET /api/services/single/list - should return array of single massage services
4. GET /api/services/couples/list - should return array of couples massage services
5. GET /api/appointments/list - should return list of appointments
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from review request
BACKEND_URL = "https://gold-line-fixer.preview.emergentagent.com"

def test_health_endpoint():
    """Test GET /api/health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    
    try:
        url = f"{BACKEND_URL}/api/health"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if response contains required status field
            if "status" in data and data["status"] == "healthy":
                print("✅ PASS: Health endpoint returned correct response")
                return True
            else:
                print("❌ FAIL: Health endpoint response missing 'status': 'healthy'")
                return False
        else:
            print(f"❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {str(e)}")
        return False

def test_services_endpoint():
    """Test GET /api/services endpoint"""
    print("\n=== Testing Services Endpoint ===")
    
    try:
        url = f"{BACKEND_URL}/api/services"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"✅ PASS: Services endpoint returned array with {len(data)} services")
                
                # Show sample service if available
                if len(data) > 0:
                    print(f"Sample service: {json.dumps(data[0], indent=2)}")
                
                return True
            else:
                print(f"❌ FAIL: Expected array, got {type(data)}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {str(e)}")
        return False

def test_single_services_endpoint():
    """Test GET /api/services/single/list endpoint"""
    print("\n=== Testing Single Services Endpoint ===")
    
    try:
        url = f"{BACKEND_URL}/api/services/single/list"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"✅ PASS: Single services endpoint returned array with {len(data)} services")
                
                # Show sample service if available
                if len(data) > 0:
                    print(f"Sample single service: {json.dumps(data[0], indent=2)}")
                
                return True
            else:
                print(f"❌ FAIL: Expected array, got {type(data)}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {str(e)}")
        return False

def test_couples_services_endpoint():
    """Test GET /api/services/couples/list endpoint"""
    print("\n=== Testing Couples Services Endpoint ===")
    
    try:
        url = f"{BACKEND_URL}/api/services/couples/list"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"✅ PASS: Couples services endpoint returned array with {len(data)} services")
                
                # Show sample service if available
                if len(data) > 0:
                    print(f"Sample couples service: {json.dumps(data[0], indent=2)}")
                
                return True
            else:
                print(f"❌ FAIL: Expected array, got {type(data)}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {str(e)}")
        return False

def test_appointments_list_endpoint():
    """Test GET /api/appointments/list endpoint"""
    print("\n=== Testing Appointments List Endpoint ===")
    
    try:
        url = f"{BACKEND_URL}/api/appointments/list"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            # Check if response is a list (direct array) or dict with items array
            if isinstance(data, list):
                print(f"✅ PASS: Appointments list endpoint returned array with {len(data)} appointments")
                
                # Show sample appointment if available
                if len(data) > 0:
                    print(f"Sample appointment: {json.dumps(data[0], indent=2)}")
                
                return True
            elif isinstance(data, dict) and "items" in data:
                # Response is a paginated structure with items array
                items = data["items"]
                print(f"✅ PASS: Appointments list endpoint returned paginated response with {len(items)} appointments")
                print(f"Total count: {data.get('total_count', 'N/A')}")
                print(f"Period: {data.get('period', 'N/A')}")
                
                # Show sample appointment if available
                if len(items) > 0:
                    print(f"Sample appointment: {json.dumps(items[0], indent=2)}")
                else:
                    print("No appointments in current period")
                
                return True
            else:
                print(f"❌ FAIL: Expected array or dict with 'items' key, got {type(data)}")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ FAIL: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {str(e)}")
        return False

def main():
    """Run all backend tests"""
    print("=" * 60)
    print("BACKEND API TEST SUITE - Review Request")
    print(f"Testing Backend: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Track test results
    test_results = []
    
    # Run all tests
    test_results.append(("Health Endpoint", test_health_endpoint()))
    test_results.append(("Services Endpoint", test_services_endpoint()))
    test_results.append(("Single Services Endpoint", test_single_services_endpoint()))
    test_results.append(("Couples Services Endpoint", test_couples_services_endpoint()))
    test_results.append(("Appointments List Endpoint", test_appointments_list_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())