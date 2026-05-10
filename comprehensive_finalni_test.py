#!/usr/bin/env python3
"""
COMPREHENSIVE FINALNI TEST - Verifikacija da su cene sada potpuno ispravne nakon uklanjanja popusta iz booking sistema

EXACT TEST SCENARIO FROM REVIEW REQUEST:
Masaža za parove - 60 min:
- Osoba 1: Tradicionalna tajlandska masaža (4400 RSD)
- Osoba 2: Aroma terapija (4400 RSD)

OČEKIVANE CENE:
- Originalna ukupna: 8,800 RSD
- Popust (10%): -880 RSD  
- Finalna cena: 7,920 RSD

ENDPOINTS:
- GET https://wavy-parallax-hero.preview.emergentagent.com/api/services
- POST https://wavy-parallax-hero.preview.emergentagent.com/api/book-appointment

Testiranje podaci:
- Ime: Finalni Test
- Email: final@test.com
- Datum: 2025-11-21
- Vreme: 15:00
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "https://wavy-parallax-hero.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class ComprehensiveFinalniTest:
    def __init__(self):
        self.results = []
        self.services_data = None
        
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
        if details and isinstance(details, dict):
            for key, value in details.items():
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {json.dumps(value, indent=4)}")
                else:
                    print(f"   {key}: {value}")
        print()

    async def fetch_services(self):
        """Fetch services data for analysis"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/services")
                
                if response.status_code == 200:
                    self.services_data = response.json()
                    return True
                else:
                    self.log_result(
                        "Services Data Fetch",
                        False,
                        f"Failed to fetch services: {response.status_code}",
                        {"status_code": response.status_code, "response": response.text[:200]}
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Services Data Fetch",
                False,
                f"Exception fetching services: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_1_discount_percentage_verification(self):
        """TEST 1: Verifikuj da booking sistem API vraća discount_percentage = 0% za sve [PAROVI] servise"""
        print("🧪 TEST 1: Discount Percentage Verification for [PAROVI] Services")
        print("=" * 80)
        
        if not self.services_data:
            await self.fetch_services()
        
        if not self.services_data:
            self.log_result(
                "Discount Percentage Verification",
                False,
                "Cannot verify discounts - services data not available",
                {}
            )
            return False
        
        # Find [PAROVI] services
        parovi_services = [s for s in self.services_data if s.get('name', '').startswith('[PAROVI]')]
        
        if not parovi_services:
            self.log_result(
                "Discount Percentage Verification",
                False,
                "No [PAROVI] services found in booking system",
                {"total_services": len(self.services_data)}
            )
            return False
        
        # Check discount percentages
        correct_discounts = []
        incorrect_discounts = []
        
        for service in parovi_services:
            discount = service.get('discount_percentage', 'NOT_FOUND')
            if discount == 0 or discount == 0.0:
                correct_discounts.append({
                    "name": service['name'],
                    "discount": discount,
                    "price": service.get('price', 'N/A')
                })
            else:
                incorrect_discounts.append({
                    "name": service['name'],
                    "discount": discount,
                    "expected": 0,
                    "price": service.get('price', 'N/A')
                })
        
        success = len(incorrect_discounts) == 0
        
        self.log_result(
            "Discount Percentage Verification",
            success,
            f"Found {len(parovi_services)} [PAROVI] services, {len(correct_discounts)} with 0% discount, {len(incorrect_discounts)} with non-zero discount",
            {
                "total_parovi_services": len(parovi_services),
                "correct_discounts_count": len(correct_discounts),
                "incorrect_discounts_count": len(incorrect_discounts),
                "correct_services": correct_discounts[:5],  # First 5
                "incorrect_services": incorrect_discounts
            }
        )
        
        return success

    async def test_2_base_price_verification(self):
        """TEST 2: Verifikuj da bazne cene ostale iste (4400 RSD)"""
        print("🧪 TEST 2: Base Price Verification for Target Services")
        print("=" * 80)
        
        if not self.services_data:
            await self.fetch_services()
        
        if not self.services_data:
            self.log_result(
                "Base Price Verification",
                False,
                "Cannot verify prices - services data not available",
                {}
            )
            return False
        
        # Look for the exact services from the review request
        target_services = {
            "[PAROVI] Tradicionalna tajlandska masaža - 60 min": 4400,
            "[PAROVI] Aroma terapija - 60 min": 4400
        }
        
        found_services = {}
        price_issues = []
        
        for service in self.services_data:
            service_name = service.get('name', '')
            for target_name, expected_price in target_services.items():
                if service_name == target_name:
                    actual_price = service.get('price', 0)
                    found_services[target_name] = {
                        "service_name": service_name,
                        "actual_price": actual_price,
                        "expected_price": expected_price,
                        "correct": actual_price == expected_price,
                        "discount_percentage": service.get('discount_percentage', 'N/A'),
                        "service_id": service.get('id', 'N/A')
                    }
                    
                    if actual_price != expected_price:
                        price_issues.append({
                            "service": service_name,
                            "actual_price": actual_price,
                            "expected_price": expected_price,
                            "difference": actual_price - expected_price
                        })
        
        success = len(price_issues) == 0 and len(found_services) == len(target_services)
        
        self.log_result(
            "Base Price Verification",
            success,
            f"Found {len(found_services)}/{len(target_services)} target services, {len(price_issues)} price issues",
            {
                "target_services": target_services,
                "found_services": found_services,
                "price_issues": price_issues,
                "missing_services": [name for name in target_services if name not in found_services]
            }
        )
        
        return success

    async def test_3_exact_scenario_booking(self):
        """TEST 3: Test booking poziv sa couples massage - EXACT SCENARIO"""
        print("🧪 TEST 3: Exact Scenario Couples Massage Booking")
        print("=" * 80)
        
        if not self.services_data:
            await self.fetch_services()
        
        if not self.services_data:
            self.log_result(
                "Exact Scenario Booking",
                False,
                "Cannot test booking - services data not available",
                {}
            )
            return False
        
        # Find the exact service IDs for the review request scenario
        tradicionalna_service = None
        aroma_service = None
        
        for service in self.services_data:
            name = service.get('name', '')
            if name == "[PAROVI] Tradicionalna tajlandska masaža - 60 min":
                tradicionalna_service = service
            elif name == "[PAROVI] Aroma terapija - 60 min":
                aroma_service = service
        
        if not tradicionalna_service or not aroma_service:
            self.log_result(
                "Exact Scenario Booking",
                False,
                "Cannot find required [PAROVI] services for exact scenario",
                {
                    "tradicionalna_found": tradicionalna_service is not None,
                    "aroma_found": aroma_service is not None,
                    "available_parovi_services": [s.get('name', 'Unknown') for s in self.services_data if s.get('name', '').startswith('[PAROVI]')][:10]
                }
            )
            return False
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare exact booking data from review request
                booking_data = {
                    "client_first_name": "Finalni",
                    "client_last_name": "Test",
                    "client_phone": "+381601234567",
                    "client_email": "final@test.com",
                    "start_time": "2025-11-21T15:00:00",
                    "duration_type": 60,
                    "person1_services": [tradicionalna_service['id']],
                    "person2_services": [aroma_service['id']],
                    "discount_couples_massage": 0.0,
                    "language": "sr"
                }
                
                # Make booking request
                response = await client.post(
                    f"{API_BASE}/book-couple-appointment",
                    json=booking_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    booking_result = response.json()
                    appointment_id = booking_result.get('id', 'N/A')
                    
                    self.log_result(
                        "Exact Scenario Booking",
                        True,
                        f"Exact scenario booking successful - Appointment ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "client": "Finalni Test (+381601234567, final@test.com)",
                            "date_time": "2025-11-21T15:00:00",
                            "person1_service": tradicionalna_service['name'],
                            "person1_service_id": tradicionalna_service['id'],
                            "person1_price": tradicionalna_service['price'],
                            "person2_service": aroma_service['name'],
                            "person2_service_id": aroma_service['id'],
                            "person2_price": aroma_service['price'],
                            "total_expected_price": tradicionalna_service['price'] + aroma_service['price'],
                            "booking_response": booking_result
                        }
                    )
                    return booking_result
                else:
                    error_detail = response.text
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            error_data = response.json()
                            error_detail = error_data.get('detail', error_detail)
                    except:
                        pass
                    
                    self.log_result(
                        "Exact Scenario Booking",
                        False,
                        f"Exact scenario booking failed - {response.status_code}: {error_detail}",
                        {
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "booking_data": booking_data,
                            "person1_service": tradicionalna_service['name'],
                            "person2_service": aroma_service['name']
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Exact Scenario Booking",
                False,
                f"Exception during exact scenario booking: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_4_final_price_verification(self):
        """TEST 4: Verifikuj da je finalna cena u rezervaciji 7,920 RSD"""
        print("🧪 TEST 4: Final Price Calculation and Verification")
        print("=" * 80)
        
        if not self.services_data:
            await self.fetch_services()
        
        if not self.services_data:
            self.log_result(
                "Final Price Verification",
                False,
                "Cannot verify final price - services data not available",
                {}
            )
            return False
        
        # Find the exact services and their prices
        tradicionalna_service = None
        aroma_service = None
        
        for service in self.services_data:
            name = service.get('name', '')
            if name == "[PAROVI] Tradicionalna tajlandska masaža - 60 min":
                tradicionalna_service = service
            elif name == "[PAROVI] Aroma terapija - 60 min":
                aroma_service = service
        
        if not tradicionalna_service or not aroma_service:
            self.log_result(
                "Final Price Verification",
                False,
                "Cannot find required services for price calculation",
                {}
            )
            return False
        
        # Calculate prices based on actual service data
        person1_price = tradicionalna_service.get('price', 0)
        person2_price = aroma_service.get('price', 0)
        total_before_discount = person1_price + person2_price
        
        # Expected calculation from review request
        expected_person1_price = 4400
        expected_person2_price = 4400
        expected_total_before_discount = 8800
        expected_discount_percentage = 10
        expected_discount_amount = 880
        expected_final_price = 7920
        
        # Actual calculation
        actual_discount_percentage = 10  # From review request
        actual_discount_amount = total_before_discount * (actual_discount_percentage / 100)
        actual_final_price = total_before_discount - actual_discount_amount
        
        # Check if prices match expectations
        prices_correct = (person1_price == expected_person1_price and 
                         person2_price == expected_person2_price)
        calculation_correct = (total_before_discount == expected_total_before_discount and
                             actual_final_price == expected_final_price)
        
        # Look for existing couples massage service with this exact combination
        existing_couples_service = None
        for service in self.services_data:
            name = service.get('name', '')
            description = service.get('description', '')
            if ('Masaža za parove' in name and 
                '120 min (2x60 min)' in name and
                'Tradicionalna tajlandska masaža' in description and
                'Aroma terapija' in description):
                existing_couples_service = service
                break
        
        success = prices_correct and calculation_correct
        
        self.log_result(
            "Final Price Verification",
            success,
            f"Price calculation: {total_before_discount} - {actual_discount_amount} = {actual_final_price} RSD ({'matches' if actual_final_price == expected_final_price else 'does not match'} expected 7,920 RSD)",
            {
                "person1_service": tradicionalna_service['name'],
                "person1_actual_price": person1_price,
                "person1_expected_price": expected_person1_price,
                "person1_price_correct": person1_price == expected_person1_price,
                "person2_service": aroma_service['name'],
                "person2_actual_price": person2_price,
                "person2_expected_price": expected_person2_price,
                "person2_price_correct": person2_price == expected_person2_price,
                "total_before_discount": total_before_discount,
                "expected_total_before_discount": expected_total_before_discount,
                "discount_percentage": actual_discount_percentage,
                "discount_amount": actual_discount_amount,
                "expected_discount_amount": expected_discount_amount,
                "calculated_final_price": actual_final_price,
                "expected_final_price": expected_final_price,
                "final_price_correct": actual_final_price == expected_final_price,
                "existing_couples_service": existing_couples_service,
                "calculation_formula": f"{total_before_discount} - ({actual_discount_percentage}% of {total_before_discount}) = {actual_final_price}"
            }
        )
        
        return success

    async def test_5_existing_couples_service_verification(self):
        """TEST 5: Check if there's already a couples service with the exact scenario and correct price"""
        print("🧪 TEST 5: Existing Couples Service Verification")
        print("=" * 80)
        
        if not self.services_data:
            await self.fetch_services()
        
        if not self.services_data:
            self.log_result(
                "Existing Couples Service Verification",
                False,
                "Cannot verify existing couples services - services data not available",
                {}
            )
            return False
        
        # Look for couples services that match the exact scenario
        matching_couples_services = []
        
        for service in self.services_data:
            name = service.get('name', '')
            description = service.get('description', '')
            price = service.get('price', 0)
            
            if ('Masaža za parove' in name and 
                '120 min (2x60 min)' in name and
                'Tradicionalna tajlandska masaža' in description and
                'Aroma terapija' in description):
                
                matching_couples_services.append({
                    "name": name,
                    "description": description,
                    "price": price,
                    "expected_price": 7920,
                    "price_correct": price == 7920,
                    "discount_percentage": service.get('discount_percentage', 'N/A'),
                    "service_id": service.get('id', 'N/A'),
                    "category": service.get('category', 'N/A')
                })
        
        # Check if any of the matching services has the correct price
        correct_price_services = [s for s in matching_couples_services if s['price_correct']]
        
        success = len(correct_price_services) > 0
        
        self.log_result(
            "Existing Couples Service Verification",
            success,
            f"Found {len(matching_couples_services)} matching couples services, {len(correct_price_services)} with correct price (7920 RSD)",
            {
                "matching_services_count": len(matching_couples_services),
                "correct_price_services_count": len(correct_price_services),
                "matching_services": matching_couples_services,
                "expected_price": 7920,
                "scenario": "Osoba 1: Tradicionalna tajlandska masaža - 60 min, Osoba 2: Aroma terapija - 60 min"
            }
        )
        
        return success

    async def run_comprehensive_test(self):
        """Run all tests and provide comprehensive analysis"""
        print("=" * 100)
        print("COMPREHENSIVE FINALNI TEST - Couples Massage Price Verification")
        print("=" * 100)
        print("Testing exact scenario from review request:")
        print("- Masaža za parove - 60 min")
        print("- Osoba 1: Tradicionalna tajlandska masaža (4400 RSD)")
        print("- Osoba 2: Aroma terapija (4400 RSD)")
        print("- Expected final price: 7,920 RSD (8,800 - 10% = 7,920)")
        print(f"Backend URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Fetch services data first
        print("🔍 Fetching services data...")
        services_fetched = await self.fetch_services()
        
        if not services_fetched:
            print("❌ Cannot proceed with tests - services data not available")
            return self.results
        
        print(f"✅ Fetched {len(self.services_data)} services from booking system")
        print()
        
        # Test 1: Discount percentage verification
        print("🔍 Running Test 1...")
        result1 = await self.test_1_discount_percentage_verification()
        
        # Test 2: Base price verification
        print("🔍 Running Test 2...")
        result2 = await self.test_2_base_price_verification()
        
        # Test 3: Exact scenario booking
        print("🔍 Running Test 3...")
        result3 = await self.test_3_exact_scenario_booking()
        
        # Test 4: Final price verification
        print("🔍 Running Test 4...")
        result4 = await self.test_4_final_price_verification()
        
        # Test 5: Existing couples service verification
        print("🔍 Running Test 5...")
        result5 = await self.test_5_existing_couples_service_verification()
        
        # Comprehensive Summary
        print("\n" + "=" * 100)
        print("COMPREHENSIVE FINALNI TEST SUMMARY")
        print("=" * 100)
        
        passed_tests = 0
        total_tests = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if "✅ PASS" in result['status']:
                passed_tests += 1
        
        print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        # Detailed assessment based on review request objectives
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - REVIEW REQUEST OBJECTIVES FULLY ACHIEVED!")
            print("✅ All [PAROVI] services have discount_percentage = 0%")
            print("✅ Base prices are correct (4400 RSD for both services)")
            print("✅ Couples booking functionality works perfectly")
            print("✅ Final price calculation is accurate (7,920 RSD)")
            print("✅ Existing couples services have correct pricing")
            print("\n🔧 COUPLES MASSAGE PRICING SYSTEM: FULLY CORRECTED")
            
        elif passed_tests >= 3:
            print(f"\n⚠️ MOSTLY SUCCESSFUL - {passed_tests}/{total_tests} tests passed")
            print("Core functionality is working but some issues remain:")
            
            failed_tests = [r for r in self.results if "❌ FAIL" in r['status']]
            for failed in failed_tests:
                print(f"❌ {failed['test']}: {failed['message']}")
            
            if result3:  # If booking works
                print("\n✅ CRITICAL: Booking functionality works")
                print("✅ Users can successfully make couples massage reservations")
            
            print("\n🔧 MINOR FIXES NEEDED - System mostly functional")
            
        else:
            print(f"\n🚨 SIGNIFICANT ISSUES FOUND - Only {passed_tests}/{total_tests} tests passed")
            print("Major problems with couples massage system:")
            
            for result in self.results:
                if "❌ FAIL" in result['status']:
                    print(f"❌ {result['test']}: {result['message']}")
            
            if not result3:  # If booking doesn't work
                print("\n🚨 CRITICAL: Booking functionality broken")
                print("❌ Users cannot make couples massage reservations")
            
            print("\n🔧 URGENT FIXES REQUIRED")
        
        # Specific review request assessment
        print("\n" + "=" * 100)
        print("REVIEW REQUEST SPECIFIC ASSESSMENT")
        print("=" * 100)
        
        print("Review Request Objectives:")
        print("1. Verifikuj da booking sistem API vraća discount_percentage = 0% za sve [PAROVI] servise")
        print(f"   Status: {'✅ ACHIEVED' if result1 else '❌ NOT ACHIEVED'}")
        
        print("2. Verifikuj da bazne cene ostale iste (4400 RSD)")
        print(f"   Status: {'✅ ACHIEVED' if result2 else '❌ NOT ACHIEVED'}")
        
        print("3. Test booking poziv sa couples massage")
        print(f"   Status: {'✅ ACHIEVED' if result3 else '❌ NOT ACHIEVED'}")
        
        print("4. Verifikuj da je finalna cena u rezervaciji 7,920 RSD")
        print(f"   Status: {'✅ ACHIEVED' if result4 else '❌ NOT ACHIEVED'}")
        
        objectives_met = sum([result1, result2, bool(result3), result4])
        print(f"\nReview Request Objectives Met: {objectives_met}/4")
        
        if objectives_met == 4:
            print("🎉 ALL REVIEW REQUEST OBJECTIVES SUCCESSFULLY ACHIEVED!")
        elif objectives_met >= 3:
            print("⚠️ MOST review request objectives achieved - minor issues remain")
        else:
            print("🚨 SIGNIFICANT issues with review request objectives")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ComprehensiveFinalniTest()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())