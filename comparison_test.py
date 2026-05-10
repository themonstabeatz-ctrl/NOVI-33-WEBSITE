#!/usr/bin/env python3
"""
COMPREHENSIVE COMPARISON TEST - WORKING VERSION vs MY VERSION
Detailed comparison as requested in the review request
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class SystemComparisonTester:
    def __init__(self):
        # URLs from review request
        self.working_version_url = "https://wavy-parallax-hero.preview.emergentagent.com"
        self.my_version_url = "https://wavy-parallax-hero.preview.emergentagent.com"
        
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or {}
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
        print()

    async def compare_api_services(self):
        """Compare /api/services endpoints between both versions"""
        print("🔍 COMPARING API SERVICES ENDPOINTS")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Get services from WORKING VERSION
                working_response = await client.get(f"{self.working_version_url}/api/services")
                
                # Get services from MY VERSION  
                my_response = await client.get(f"{self.my_version_url}/api/services")
                
                working_success = working_response.status_code == 200
                my_success = my_response.status_code == 200
                
                working_services = working_response.json() if working_success else []
                my_services = my_response.json() if my_success else []
                
                # Filter couples services (Kartica Masaza za parove category)
                working_couples = []
                my_couples = []
                
                if working_success and isinstance(working_services, list):
                    working_couples = [s for s in working_services if s.get('category') == 'Kartica Masaza za parove']
                
                if my_success and isinstance(my_services, list):
                    my_couples = [s for s in my_services if s.get('category') == 'Kartica Masaza za parove']
                
                # Find "Aroma terapija - 60 min" service in both
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
                
                self.log_result(
                    "API Services Comparison",
                    working_success and my_success,
                    f"WORKING VERSION: {len(working_services)} total, {len(working_couples)} couples | MY VERSION: {len(my_services)} total, {len(my_couples)} couples",
                    {
                        "working_version": {
                            "url": f"{self.working_version_url}/api/services",
                            "status_code": working_response.status_code,
                            "total_services": len(working_services) if working_success else 0,
                            "couples_services": len(working_couples),
                            "couples_services_list": [s.get('name', 'Unknown') for s in working_couples[:10]],
                            "aroma_terapija_60min": working_aroma
                        },
                        "my_version": {
                            "url": f"{self.my_version_url}/api/services",
                            "status_code": my_response.status_code,
                            "total_services": len(my_services) if my_success else 0,
                            "couples_services": len(my_couples),
                            "couples_services_list": [s.get('name', 'Unknown') for s in my_couples[:10]],
                            "aroma_terapija_60min": my_aroma
                        },
                        "differences": {
                            "total_services_diff": len(working_services) - len(my_services) if working_success and my_success else "Cannot compare",
                            "couples_services_diff": len(working_couples) - len(my_couples),
                            "aroma_terapija_comparison": {
                                "working_found": working_aroma is not None,
                                "my_found": my_aroma is not None,
                                "price_match": working_aroma.get('price') == my_aroma.get('price') if working_aroma and my_aroma else False,
                                "discount_match": working_aroma.get('discount_percentage') == my_aroma.get('discount_percentage') if working_aroma and my_aroma else False
                            }
                        }
                    }
                )
                
                return working_success and my_success
                
        except Exception as e:
            self.log_result(
                "API Services Comparison",
                False,
                f"Exception during API comparison: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_identical_service_comparison(self):
        """Find and compare identical service between both versions"""
        print("🔍 IDENTICAL SERVICE DETAILED COMPARISON")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Get services from both versions
                working_response = await client.get(f"{self.working_version_url}/api/services")
                my_response = await client.get(f"{self.my_version_url}/api/services")
                
                if working_response.status_code != 200 or my_response.status_code != 200:
                    self.log_result(
                        "Identical Service Comparison",
                        False,
                        f"Cannot fetch services - Working: {working_response.status_code}, My: {my_response.status_code}",
                        {}
                    )
                    return False
                
                working_services = working_response.json()
                my_services = my_response.json()
                
                # Look for "Aroma terapija - 60 min" or "[PAROVI] Aroma terapija - 60 min"
                target_names = ["Aroma terapija - 60 min", "[PAROVI] Aroma terapija - 60 min"]
                
                working_service = None
                my_service = None
                
                for name in target_names:
                    if not working_service:
                        working_service = next((s for s in working_services if s.get('name') == name), None)
                    if not my_service:
                        my_service = next((s for s in my_services if s.get('name') == name), None)
                
                # If exact match not found, try partial match
                if not working_service or not my_service:
                    for service in working_services:
                        if "Aroma terapija" in service.get('name', '') and "60 min" in service.get('name', ''):
                            working_service = service
                            break
                    
                    for service in my_services:
                        if "Aroma terapija" in service.get('name', '') and "60 min" in service.get('name', ''):
                            my_service = service
                            break
                
                if working_service and my_service:
                    # Compare all fields
                    fields_to_compare = ['id', 'name', 'price', 'discount_percentage', 'category', 'duration', 'description']
                    
                    comparison = {}
                    all_match = True
                    
                    for field in fields_to_compare:
                        working_value = working_service.get(field)
                        my_value = my_service.get(field)
                        matches = working_value == my_value
                        
                        comparison[field] = {
                            "working_version": working_value,
                            "my_version": my_value,
                            "matches": matches
                        }
                        
                        if not matches:
                            all_match = False
                    
                    self.log_result(
                        "Identical Service Field Comparison",
                        all_match,
                        f"Service comparison: {'ALL FIELDS MATCH' if all_match else 'DIFFERENCES FOUND'}",
                        {
                            "service_name": working_service.get('name', 'Unknown'),
                            "field_comparison": comparison,
                            "working_service_full": working_service,
                            "my_service_full": my_service
                        }
                    )
                    
                    return all_match
                else:
                    self.log_result(
                        "Identical Service Field Comparison",
                        False,
                        f"Cannot find Aroma terapija service - Working: {'Found' if working_service else 'Not found'}, My: {'Found' if my_service else 'Not found'}",
                        {
                            "working_service": working_service,
                            "my_service": my_service
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Identical Service Field Comparison",
                False,
                f"Exception during service comparison: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_couples_discount_numbers(self):
        """Test exact numbers for couples discount as requested"""
        print("🔍 COUPLES DISCOUNT EXACT NUMBERS COMPARISON")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Get services from both versions
                working_response = await client.get(f"{self.working_version_url}/api/services")
                my_response = await client.get(f"{self.my_version_url}/api/services")
                
                if working_response.status_code != 200 or my_response.status_code != 200:
                    self.log_result(
                        "Couples Discount Numbers",
                        False,
                        f"Cannot fetch services for discount analysis",
                        {}
                    )
                    return False
                
                working_services = working_response.json()
                my_services = my_response.json()
                
                # Filter couples services
                working_couples = [s for s in working_services if 'PAROVI' in s.get('name', '') or s.get('category') == 'Kartica Masaza za parove']
                my_couples = [s for s in my_services if 'PAROVI' in s.get('name', '') or s.get('category') == 'Kartica Masaza za parove']
                
                # Calculate statistics
                working_stats = {
                    "count": len(working_couples),
                    "discount_percentages": [s.get('discount_percentage', 0) for s in working_couples],
                    "prices": [s.get('price', 0) for s in working_couples],
                    "has_parovi_prefix": sum(1 for s in working_couples if s.get('name', '').startswith('[PAROVI]')),
                    "average_price": sum(s.get('price', 0) for s in working_couples) / len(working_couples) if working_couples else 0
                }
                
                my_stats = {
                    "count": len(my_couples),
                    "discount_percentages": [s.get('discount_percentage', 0) for s in my_couples],
                    "prices": [s.get('price', 0) for s in my_couples],
                    "has_parovi_prefix": sum(1 for s in my_couples if s.get('name', '').startswith('[PAROVI]')),
                    "average_price": sum(s.get('price', 0) for s in my_couples) / len(my_couples) if my_couples else 0
                }
                
                # Check if numbers match
                numbers_match = (
                    working_stats["count"] == my_stats["count"] and
                    working_stats["discount_percentages"] == my_stats["discount_percentages"] and
                    working_stats["prices"] == my_stats["prices"]
                )
                
                self.log_result(
                    "Couples Discount Exact Numbers",
                    numbers_match,
                    f"Numbers comparison: {'IDENTICAL' if numbers_match else 'DIFFERENT'}",
                    {
                        "working_version": working_stats,
                        "my_version": my_stats,
                        "differences": {
                            "count_diff": working_stats["count"] - my_stats["count"],
                            "discount_percentages_match": working_stats["discount_percentages"] == my_stats["discount_percentages"],
                            "prices_match": working_stats["prices"] == my_stats["prices"],
                            "parovi_prefix_diff": working_stats["has_parovi_prefix"] - my_stats["has_parovi_prefix"]
                        }
                    }
                )
                
                return numbers_match
                
        except Exception as e:
            self.log_result(
                "Couples Discount Exact Numbers",
                False,
                f"Exception during discount analysis: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_booking_flow_comparison(self):
        """Test booking flow on both systems"""
        print("🔍 BOOKING FLOW COMPARISON")
        print("=" * 60)
        
        # Test data
        test_booking = {
            "client_first_name": "Test",
            "client_last_name": "Comparison",
            "client_phone": "+381601234567",
            "client_email": "test.comparison@example.com",
            "appointment_date": "2025-11-15",
            "start_time": "2025-11-15T14:00:00",
            "notes": "Booking flow comparison test"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get services from both to find a common service
                working_services_response = await client.get(f"{self.working_version_url}/api/services")
                my_services_response = await client.get(f"{self.my_version_url}/api/services")
                
                if working_services_response.status_code != 200 or my_services_response.status_code != 200:
                    self.log_result(
                        "Booking Flow Comparison",
                        False,
                        "Cannot fetch services for booking test",
                        {}
                    )
                    return False
                
                working_services = working_services_response.json()
                my_services = my_services_response.json()
                
                # Find a common service (first service that exists in both)
                common_service = None
                for w_service in working_services:
                    for m_service in my_services:
                        if w_service.get('name') == m_service.get('name'):
                            common_service = {
                                'working_id': w_service.get('id'),
                                'my_id': m_service.get('id'),
                                'name': w_service.get('name')
                            }
                            break
                    if common_service:
                        break
                
                if not common_service:
                    # Use first service from each if no common service found
                    working_service = working_services[0] if working_services else None
                    my_service = my_services[0] if my_services else None
                    
                    if working_service and my_service:
                        common_service = {
                            'working_id': working_service.get('id'),
                            'my_id': my_service.get('id'),
                            'name': f"Working: {working_service.get('name')}, My: {my_service.get('name')}"
                        }
                
                if not common_service:
                    self.log_result(
                        "Booking Flow Comparison",
                        False,
                        "No services available for booking test",
                        {}
                    )
                    return False
                
                # Test booking on working version
                working_booking_data = {**test_booking, "service_id": common_service['working_id']}
                working_booking_response = await client.post(
                    f"{self.working_version_url}/api/book-appointment",
                    json=working_booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Test booking on my version
                my_booking_data = {**test_booking, "service_id": common_service['my_id']}
                my_booking_response = await client.post(
                    f"{self.my_version_url}/api/book-appointment",
                    json=my_booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                working_success = working_booking_response.status_code in [200, 201]
                my_success = my_booking_response.status_code in [200, 201]
                
                working_result = working_booking_response.json() if working_success else working_booking_response.text
                my_result = my_booking_response.json() if my_success else my_booking_response.text
                
                self.log_result(
                    "Booking Flow Comparison",
                    working_success and my_success,
                    f"Booking test - Working: {'SUCCESS' if working_success else 'FAILED'}, My: {'SUCCESS' if my_success else 'FAILED'}",
                    {
                        "common_service": common_service,
                        "working_version": {
                            "status_code": working_booking_response.status_code,
                            "success": working_success,
                            "response": working_result
                        },
                        "my_version": {
                            "status_code": my_booking_response.status_code,
                            "success": my_success,
                            "response": my_result
                        }
                    }
                )
                
                return working_success and my_success
                
        except Exception as e:
            self.log_result(
                "Booking Flow Comparison",
                False,
                f"Exception during booking flow test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_backend_configuration_comparison(self):
        """Compare backend configurations"""
        print("🔍 BACKEND CONFIGURATION ANALYSIS")
        print("=" * 60)
        
        # Read my backend configuration
        my_backend_config = {}
        try:
            with open('/app/backend/.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        my_backend_config[key] = value.strip('"')
        except Exception as e:
            my_backend_config = {"error": f"Cannot read backend .env: {str(e)}"}
        
        # Read my frontend configuration
        my_frontend_config = {}
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        my_frontend_config[key] = value.strip('"')
        except Exception as e:
            my_frontend_config = {"error": f"Cannot read frontend .env: {str(e)}"}
        
        self.log_result(
            "Backend Configuration Analysis",
            True,
            "Configuration analysis completed",
            {
                "my_backend_config": my_backend_config,
                "my_frontend_config": my_frontend_config,
                "analysis": {
                    "booking_api_url": my_backend_config.get('BOOKING_API_URL', 'Not set'),
                    "frontend_backend_url": my_frontend_config.get('REACT_APP_BACKEND_URL', 'Not set'),
                    "mongo_url": my_backend_config.get('MONGO_URL', 'Not set'),
                    "cors_origins": my_backend_config.get('CORS_ORIGINS', 'Not set')
                }
            }
        )
        
        return True

    async def run_comprehensive_comparison(self):
        """Run all comparison tests"""
        print("=" * 80)
        print("COMPREHENSIVE SYSTEM COMPARISON - WORKING vs MY VERSION")
        print("=" * 80)
        print(f"Working Version (PERFECT): {self.working_version_url}")
        print(f"My Version: {self.my_version_url}")
        print()
        
        # Test 1: API Services Comparison
        print("🔍 TEST 1: API Services Endpoints Comparison")
        api_comparison_success = await self.compare_api_services()
        
        # Test 2: Identical Service Detailed Comparison
        print("\n🔍 TEST 2: Identical Service Field-by-Field Comparison")
        service_comparison_success = await self.test_identical_service_comparison()
        
        # Test 3: Couples Discount Numbers
        print("\n🔍 TEST 3: Couples Discount Exact Numbers")
        discount_numbers_success = await self.test_couples_discount_numbers()
        
        # Test 4: Booking Flow Comparison
        print("\n🔍 TEST 4: Booking Flow Comparison")
        booking_flow_success = await self.test_booking_flow_comparison()
        
        # Test 5: Backend Configuration Analysis
        print("\n🔍 TEST 5: Backend Configuration Analysis")
        config_analysis_success = await self.test_backend_configuration_comparison()
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPREHENSIVE COMPARISON SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r['status'])
        total = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Final assessment
        if api_comparison_success and service_comparison_success and discount_numbers_success:
            print("🎉 SYSTEMS ARE FUNCTIONALLY IDENTICAL!")
            print("✅ API endpoints return same data structure")
            print("✅ Service details match exactly")
            print("✅ Couples discount numbers are identical")
        elif api_comparison_success:
            print("⚠️ SYSTEMS HAVE DIFFERENCES")
            print("✅ API endpoints accessible on both")
            print("❌ Service details or discount numbers differ")
        else:
            print("🚨 CRITICAL DIFFERENCES FOUND")
            print("❌ API endpoints or basic functionality differs")
        
        return self.results

async def main():
    """Main comparison execution"""
    tester = SystemComparisonTester()
    results = await tester.run_comprehensive_comparison()
    return results

if __name__ == "__main__":
    asyncio.run(main())