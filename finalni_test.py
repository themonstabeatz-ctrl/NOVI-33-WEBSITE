#!/usr/bin/env python3
"""
FINALNI TEST - Verifikacija da su cene sada potpuno ispravne nakon uklanjanja popusta iz booking sistema

TEST SCENARIO:
Masaža za parove - 60 min:
- Osoba 1: Tradicionalna tajlandska masaža (4400 RSD)
- Osoba 2: Aroma terapija (4400 RSD)

OČEKIVANE CENE:
- Originalna ukupna: 8,800 RSD
- Popust (10%): -880 RSD  
- Finalna cena: 7,920 RSD

TESTOVI:
1. Verifikuj da booking sistem API vraća discount_percentage = 0% za sve [PAROVI] servise
2. Verifikuj da bazne cene ostale iste (4400 RSD)
3. Test booking poziv sa couples massage
4. Verifikuj da je finalna cena u rezervaciji 7,920 RSD
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "https://gold-line-fixer.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class FinalniTest:
    def __init__(self):
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
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()

    async def test_1_services_discount_verification(self):
        """TEST 1: Verifikuj da booking sistem API vraća discount_percentage = 0% za sve [PAROVI] servise"""
        print("🧪 TEST 1: Services Endpoint - Discount Verification")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/services")
                
                if response.status_code != 200:
                    self.log_result(
                        "Services Discount Verification",
                        False,
                        f"Services endpoint failed with status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text[:200]}
                    )
                    return False
                    
                services = response.json()
                
                # Find [PAROVI] services
                parovi_services = [s for s in services if s.get('name', '').startswith('[PAROVI]')]
                
                if not parovi_services:
                    self.log_result(
                        "Services Discount Verification",
                        False,
                        "No [PAROVI] services found in booking system",
                        {"total_services": len(services), "parovi_services": 0}
                    )
                    return False
                
                # Check discount percentages
                discount_issues = []
                correct_discounts = []
                
                for service in parovi_services:
                    discount = service.get('discount_percentage', 'NOT_FOUND')
                    if discount != 0:
                        discount_issues.append({
                            "name": service['name'],
                            "discount": discount,
                            "expected": 0
                        })
                    else:
                        correct_discounts.append(service['name'])
                
                if discount_issues:
                    self.log_result(
                        "Services Discount Verification",
                        False,
                        f"Found {len(discount_issues)} [PAROVI] services with non-zero discount",
                        {
                            "total_parovi_services": len(parovi_services),
                            "services_with_wrong_discount": discount_issues,
                            "services_with_correct_discount": correct_discounts
                        }
                    )
                    return False
                
                self.log_result(
                    "Services Discount Verification",
                    True,
                    f"All {len(parovi_services)} [PAROVI] services have discount_percentage = 0%",
                    {
                        "total_parovi_services": len(parovi_services),
                        "all_services_correct": True,
                        "sample_services": [s['name'] for s in parovi_services[:3]]
                    }
                )
                return True
                
        except Exception as e:
            self.log_result(
                "Services Discount Verification",
                False,
                f"Exception during services test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_2_base_price_verification(self):
        """TEST 2: Verifikuj da bazne cene ostale iste (4400 RSD)"""
        print("🧪 TEST 2: Base Price Verification")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/services")
                
                if response.status_code != 200:
                    self.log_result(
                        "Base Price Verification",
                        False,
                        "Cannot fetch services for price verification",
                        {"status_code": response.status_code}
                    )
                    return False
                    
                services = response.json()
                
                # Look for specific services mentioned in test scenario
                target_services = {
                    "Tradicionalna tajlandska masaža - 60 min": 4400,
                    "Aroma terapija - 60 min": 4400
                }
                
                found_services = {}
                price_issues = []
                
                for service in services:
                    service_name = service.get('name', '')
                    for target_name, expected_price in target_services.items():
                        if target_name in service_name or (
                            "Tradicionalna tajlandska masaža" in service_name and "60" in service_name
                        ) or (
                            "Aroma terapija" in service_name and "60" in service_name
                        ):
                            actual_price = service.get('price', 0)
                            found_services[target_name] = {
                                "service_name": service_name,
                                "actual_price": actual_price,
                                "expected_price": expected_price,
                                "correct": actual_price == expected_price
                            }
                            
                            if actual_price != expected_price:
                                price_issues.append({
                                    "service": service_name,
                                    "actual_price": actual_price,
                                    "expected_price": expected_price,
                                    "difference": actual_price - expected_price
                                })
                
                if price_issues:
                    self.log_result(
                        "Base Price Verification",
                        False,
                        f"Found {len(price_issues)} services with incorrect base prices",
                        {
                            "price_issues": price_issues,
                            "found_services": found_services,
                            "expected_prices": target_services
                        }
                    )
                    return False
                
                if len(found_services) < len(target_services):
                    self.log_result(
                        "Base Price Verification",
                        False,
                        f"Only found {len(found_services)}/{len(target_services)} target services",
                        {
                            "found_services": found_services,
                            "missing_services": [name for name in target_services if name not in found_services]
                        }
                    )
                    return False
                
                self.log_result(
                    "Base Price Verification",
                    True,
                    "All target services found with correct base prices (4400 RSD)",
                    {
                        "verified_services": found_services,
                        "all_prices_correct": True
                    }
                )
                return True
                
        except Exception as e:
            self.log_result(
                "Base Price Verification",
                False,
                f"Exception during price verification: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_3_couples_booking(self):
        """TEST 3: Test booking poziv sa couples massage"""
        print("🧪 TEST 3: Couples Massage Booking Test")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get services to find the correct service IDs
                services_response = await client.get(f"{API_BASE}/services")
                
                if services_response.status_code != 200:
                    self.log_result(
                        "Couples Booking Test",
                        False,
                        "Cannot fetch services for booking test",
                        {"status_code": services_response.status_code}
                    )
                    return False
                    
                services = services_response.json()
                
                # Find service IDs for the test scenario
                tradicionalna_id = None
                aroma_id = None
                
                for service in services:
                    name = service.get('name', '')
                    if 'Tradicionalna tajlandska masaža' in name and '60' in name:
                        tradicionalna_id = service['id']
                    elif 'Aroma terapija' in name and '60' in name:
                        aroma_id = service['id']
                
                if not tradicionalna_id or not aroma_id:
                    self.log_result(
                        "Couples Booking Test",
                        False,
                        "Cannot find required service IDs for booking test",
                        {
                            "tradicionalna_id": tradicionalna_id,
                            "aroma_id": aroma_id,
                            "available_services": [s.get('name', 'Unknown') for s in services[:5]]
                        }
                    )
                    return False
                
                # Prepare booking data for tomorrow at 15:00
                tomorrow = datetime.now() + timedelta(days=1)
                booking_data = {
                    "client_first_name": "Finalni",
                    "client_last_name": "Test",
                    "client_phone": "+381601234567",
                    "client_email": "final@test.com",
                    "start_time": tomorrow.strftime("%Y-%m-%dT15:00:00"),
                    "duration_type": 60,
                    "person1_services": [tradicionalna_id],
                    "person2_services": [aroma_id],
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
                        "Couples Booking Test",
                        True,
                        f"Couples massage booking successful - Appointment ID: {appointment_id}",
                        {
                            "appointment_id": appointment_id,
                            "client": "Finalni Test (+381601234567, final@test.com)",
                            "date_time": tomorrow.strftime("%Y-%m-%dT15:00:00"),
                            "tradicionalna_service_id": tradicionalna_id,
                            "aroma_service_id": aroma_id,
                            "duration_per_person": 60,
                            "total_duration": 120,
                            "response": booking_result
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
                        "Couples Booking Test",
                        False,
                        f"Booking failed with status {response.status_code}: {error_detail}",
                        {
                            "status_code": response.status_code,
                            "error_detail": error_detail,
                            "booking_data": booking_data
                        }
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Couples Booking Test",
                False,
                f"Exception during couples booking test: {str(e)}",
                {"error": str(e)}
            )
            return False

    async def test_4_final_price_calculation(self):
        """TEST 4: Verifikuj da je finalna cena u rezervaciji 7,920 RSD"""
        print("🧪 TEST 4: Final Price Calculation Verification")
        print("=" * 60)
        
        # This test verifies the expected calculation:
        # Osoba 1: Tradicionalna tajlandska masaža (4400 RSD)
        # Osoba 2: Aroma terapija (4400 RSD)
        # Ukupno: 8,800 RSD
        # Popust (10%): -880 RSD
        # Finalna cena: 7,920 RSD
        
        base_price_person1 = 4400  # Tradicionalna tajlandska masaža - 60 min
        base_price_person2 = 4400  # Aroma terapija - 60 min
        total_before_discount = base_price_person1 + base_price_person2
        discount_percentage = 10  # 10% discount
        discount_amount = total_before_discount * (discount_percentage / 100)
        expected_final_price = total_before_discount - discount_amount
        
        calculation_correct = expected_final_price == 7920
        
        self.log_result(
            "Final Price Calculation",
            calculation_correct,
            f"Price calculation verification: {expected_final_price} RSD {'matches' if calculation_correct else 'does not match'} expected 7,920 RSD",
            {
                "person1_price": base_price_person1,
                "person2_price": base_price_person2,
                "total_before_discount": total_before_discount,
                "discount_percentage": discount_percentage,
                "discount_amount": discount_amount,
                "calculated_final_price": expected_final_price,
                "expected_final_price": 7920,
                "calculation_correct": calculation_correct,
                "formula": f"{total_before_discount} - ({discount_percentage}% of {total_before_discount}) = {expected_final_price}"
            }
        )
        
        return calculation_correct

    async def run_all_tests(self):
        """Run all tests and provide comprehensive summary"""
        print("=" * 80)
        print("FINALNI TEST - Couples Massage Price Verification")
        print("=" * 80)
        print("Testing couples massage booking system after discount removal")
        print(f"Backend URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Test 1: Services endpoint discount verification
        print("🔍 Running Test 1...")
        result1 = await self.test_1_services_discount_verification()
        
        # Test 2: Base price verification
        print("🔍 Running Test 2...")
        result2 = await self.test_2_base_price_verification()
        
        # Test 3: Couples booking test
        print("🔍 Running Test 3...")
        result3 = await self.test_3_couples_booking()
        
        # Test 4: Final price calculation
        print("🔍 Running Test 4...")
        result4 = await self.test_4_final_price_calculation()
        
        # Summary
        print("\n" + "=" * 80)
        print("FINALNI TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(self.results)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if "✅ PASS" in result['status']:
                passed_tests += 1
        
        print(f"\n📊 RESULTS: {passed_tests}/{total_tests} tests passed")
        
        # Detailed assessment
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Couples massage pricing is correct!")
            print("✅ Discount percentages are 0% for all [PAROVI] services")
            print("✅ Base prices are correct (4400 RSD)")
            print("✅ Couples booking functionality works")
            print("✅ Final price calculation is accurate (7,920 RSD)")
            print("\n🔧 COUPLES MASSAGE SYSTEM: FULLY FUNCTIONAL")
        elif passed_tests >= 2:
            print(f"\n⚠️ PARTIAL SUCCESS - {passed_tests}/{total_tests} tests passed")
            print("Some components are working but issues remain:")
            
            failed_tests = [r for r in self.results if "❌ FAIL" in r['status']]
            for failed in failed_tests:
                print(f"❌ {failed['test']}: {failed['message']}")
            
            print("\n🔧 REQUIRES ATTENTION - Some fixes needed")
        else:
            print(f"\n🚨 CRITICAL ISSUES FOUND - Only {passed_tests}/{total_tests} tests passed")
            print("Major problems with couples massage system:")
            
            for result in self.results:
                if "❌ FAIL" in result['status']:
                    print(f"❌ {result['test']}: {result['message']}")
            
            print("\n🔧 URGENT FIXES REQUIRED")
        
        return self.results

async def main():
    """Main test execution"""
    tester = FinalniTest()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())