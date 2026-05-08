#!/usr/bin/env python3
"""
Reception Backend Connection Test
Testing the connection between frontend and reception backend as specified in review request.

Configuration:
- Local backend is at: http://localhost:8001
- Reception backend (external) is at: https://gold-line-fixer.preview.emergentagent.com
- Local backend proxies API calls to reception backend
"""

import requests
import json
import sys
import time

# URLs from review request
LOCAL_BACKEND_URL = "http://localhost:8001"
FRONTEND_PROXY_URL = "http://localhost:3000"
RECEPTION_BACKEND_URL = "https://gold-line-fixer.preview.emergentagent.com"

def test_services_api_sync():
    """
    Test 1: Services API Sync
    Test that local backend correctly fetches and returns services from reception
    """
    print("🔍 TEST 1: Services API Sync")
    print("=" * 50)
    
    results = {}
    
    # Test single services
    print("Testing single services endpoint...")
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/api/services/single/list", timeout=10)
        print(f"Single services - Status: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Single services: {len(services)} services returned")
            
            # Verify response structure
            if services and len(services) > 0:
                sample_service = services[0]
                required_fields = ['name', 'duration', 'price', 'final_price', 'discount_percentage']
                missing_fields = [field for field in required_fields if field not in sample_service]
                
                if not missing_fields:
                    print(f"✅ Service structure valid - all required fields present")
                    results['single_services'] = True
                else:
                    print(f"❌ Missing fields in service: {missing_fields}")
                    results['single_services'] = False
            else:
                print(f"❌ No single services returned")
                results['single_services'] = False
                
            # Show first 500 chars as requested
            response_preview = str(response.text)[:500]
            print(f"Response preview (first 500 chars): {response_preview}")
        else:
            print(f"❌ Single services failed: {response.status_code} - {response.text}")
            results['single_services'] = False
            
    except Exception as e:
        print(f"❌ Single services error: {str(e)}")
        results['single_services'] = False
    
    print()
    
    # Test couples services
    print("Testing couples services endpoint...")
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/api/services/couples/list", timeout=10)
        print(f"Couples services - Status: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Couples services: {len(services)} services returned")
            
            # Verify response structure
            if services and len(services) > 0:
                sample_service = services[0]
                required_fields = ['name', 'duration', 'price', 'final_price', 'discount_percentage']
                missing_fields = [field for field in required_fields if field not in sample_service]
                
                if not missing_fields:
                    print(f"✅ Service structure valid - all required fields present")
                    results['couples_services'] = True
                else:
                    print(f"❌ Missing fields in service: {missing_fields}")
                    results['couples_services'] = False
            else:
                print(f"❌ No couples services returned")
                results['couples_services'] = False
                
            # Show first 500 chars as requested
            response_preview = str(response.text)[:500]
            print(f"Response preview (first 500 chars): {response_preview}")
        else:
            print(f"❌ Couples services failed: {response.status_code} - {response.text}")
            results['couples_services'] = False
            
    except Exception as e:
        print(f"❌ Couples services error: {str(e)}")
        results['couples_services'] = False
    
    return results

def test_frontend_proxy():
    """
    Test 2: Frontend Proxy Test
    Test that frontend proxy correctly routes API calls to local backend
    """
    print("\n🔍 TEST 2: Frontend Proxy Test")
    print("=" * 50)
    
    try:
        # Test frontend proxy routing to backend
        response = requests.get(f"{FRONTEND_PROXY_URL}/api/services/single/list", timeout=10)
        print(f"Frontend proxy - Status: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Frontend proxy working: {len(services)} services returned")
            
            # Show first 500 chars as requested
            response_preview = str(response.text)[:500]
            print(f"Response preview (first 500 chars): {response_preview}")
            
            return True
        else:
            print(f"❌ Frontend proxy failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend proxy error: {str(e)}")
        return False

def test_health_check():
    """
    Test 3: Health Check
    Test basic health endpoint
    """
    print("\n🔍 TEST 3: Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/api/health", timeout=5)
        print(f"Health check - Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"Response: {json.dumps(health_data, indent=2)}")
            
            # Verify expected response structure
            if health_data.get('status') == 'healthy':
                print("✅ Health status is 'healthy'")
                return True
            else:
                print(f"❌ Unexpected health status: {health_data.get('status')}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_service_count_verification(services_results):
    """
    Test 4: Service Count Verification
    Count number of services returned and verify > 0
    """
    print("\n🔍 TEST 4: Service Count Verification")
    print("=" * 50)
    
    results = {}
    
    # Test single services count
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/api/services/single/list", timeout=10)
        if response.status_code == 200:
            single_services = response.json()
            single_count = len(single_services)
            print(f"Single services count: {single_count}")
            
            if single_count > 0:
                print("✅ Single services count > 0")
                results['single_count_valid'] = True
            else:
                print("❌ Single services count = 0")
                results['single_count_valid'] = False
        else:
            print(f"❌ Could not get single services count: {response.status_code}")
            results['single_count_valid'] = False
    except Exception as e:
        print(f"❌ Single services count error: {str(e)}")
        results['single_count_valid'] = False
    
    # Test couples services count
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/api/services/couples/list", timeout=10)
        if response.status_code == 200:
            couples_services = response.json()
            couples_count = len(couples_services)
            print(f"Couples services count: {couples_count}")
            
            if couples_count > 0:
                print("✅ Couples services count > 0")
                results['couples_count_valid'] = True
            else:
                print("❌ Couples services count = 0")
                results['couples_count_valid'] = False
        else:
            print(f"❌ Could not get couples services count: {response.status_code}")
            results['couples_count_valid'] = False
    except Exception as e:
        print(f"❌ Couples services count error: {str(e)}")
        results['couples_count_valid'] = False
    
    return results

def test_reception_backend_direct():
    """
    Additional Test: Direct Reception Backend Test
    Test direct connection to reception backend to verify it's accessible
    """
    print("\n🔍 ADDITIONAL TEST: Direct Reception Backend Connection")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RECEPTION_BACKEND_URL}/api/services", timeout=10)
        print(f"Direct reception backend - Status: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Reception backend accessible: {len(services)} services returned")
            return True
        else:
            print(f"❌ Reception backend failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Reception backend error: {str(e)}")
        return False

def main():
    """
    Main test function following the review request requirements
    """
    print("🎯 RECEPTION BACKEND CONNECTION TEST")
    print("=" * 60)
    print(f"Local Backend: {LOCAL_BACKEND_URL}")
    print(f"Frontend Proxy: {FRONTEND_PROXY_URL}")
    print(f"Reception Backend: {RECEPTION_BACKEND_URL}")
    print("=" * 60)
    
    # Run all tests
    services_results = test_services_api_sync()
    proxy_result = test_frontend_proxy()
    health_result = test_health_check()
    count_results = test_service_count_verification(services_results)
    reception_direct = test_reception_backend_direct()
    
    # Final results summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS:")
    print("=" * 60)
    
    # Services API Sync
    single_services_ok = services_results.get('single_services', False)
    couples_services_ok = services_results.get('couples_services', False)
    
    print(f"✅ Single services API: {'PASS' if single_services_ok else 'FAIL'}")
    print(f"✅ Couples services API: {'PASS' if couples_services_ok else 'FAIL'}")
    print(f"✅ Frontend proxy: {'PASS' if proxy_result else 'FAIL'}")
    print(f"✅ Health check: {'PASS' if health_result else 'FAIL'}")
    
    # Service counts
    single_count_ok = count_results.get('single_count_valid', False)
    couples_count_ok = count_results.get('couples_count_valid', False)
    
    print(f"✅ Single services count > 0: {'PASS' if single_count_ok else 'FAIL'}")
    print(f"✅ Couples services count > 0: {'PASS' if couples_count_ok else 'FAIL'}")
    print(f"✅ Reception backend direct: {'PASS' if reception_direct else 'FAIL'}")
    
    # Overall result
    all_tests_passed = (
        single_services_ok and 
        couples_services_ok and 
        proxy_result and 
        health_result and 
        single_count_ok and 
        couples_count_ok
    )
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 OVERALL RESULT: ALL TESTS PASSED!")
        print("✅ Frontend is successfully synchronized with reception backend")
    else:
        print("💥 OVERALL RESULT: SOME TESTS FAILED!")
        print("❌ Issues detected in frontend-reception backend connection")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)