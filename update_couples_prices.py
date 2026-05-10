#!/usr/bin/env python3
"""
Automated Price Correction Script for Couples Massage Services
Updates prices in the booking system admin panel using Playwright automation
"""

import asyncio
from playwright.async_api import async_playwright
import sys

# Correct price mapping from /app/frontend/src/pages/Massage.js
CORRECT_PRICES = {
    # Tradicionalna tajlandska masaža
    "Tradicionalna tajlandska masaža - 60 min": 4400,
    "Tradicionalna tajlandska masaža - 90 min": 5600,
    "Tradicionalna tajlandska masaža - 120 min": 6800,
    
    # Aroma terapija
    "Aroma terapija - 60 min": 4400,
    "Aroma terapija - 90 min": 5600,
    "Aroma terapija - 120 min": 6800,
    
    # Masaža toplim uljem
    "Masaža toplim uljem - 60 min": 4600,
    "Masaža toplim uljem - 90 min": 5800,
    
    # Glava, vrat, ramena i leđa
    "Glava, vrat, ramena i leđa - 30 min": 2400,
    "Glava, vrat, ramena i leđa - 45 min": 3200,
    "Glava, vrat, ramena i leđa - 60 min": 3900,
    
    # Masaža stopala
    "Masaža stopala - 30 min": 2400,
    "Masaža stopala - 45 min": 2900,
    "Masaža stopala - 60 min": 3500,
    
    # Aroma duboko tkivo
    "Aroma duboko tkivo - 60 min": 4900,
    "Aroma duboko tkivo - 90 min": 6000,
    
    # Aromaterapija & topli kamen
    "Aromaterapija & topli kamen - 90 min": 6200,
    "Aromaterapija & topli kamen - 120 min": 7200,
    
    # Aroma sa toplim biljnim kompresama
    "Aroma sa toplim biljnim kompresama - 90 min": 6200,
    "Aroma sa toplim biljnim kompresama - 120 min": 7200,
    
    # Thai masaža sa toplim biljnim kompresama
    "Thai masaža sa toplim biljnim kompresama - 90 min": 6200,
    "Thai masaža sa toplim biljnim kompresama - 120 min": 7200
}

async def update_couples_prices():
    """Main function to update all couples massage prices"""
    
    async with async_playwright() as p:
        print("🚀 Starting browser automation...")
        
        # Launch browser (headless mode for server environment)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to admin panel
            print("📍 Navigating to https://wavy-parallax-hero.preview.emergentagent.com/")
            await page.goto("https://wavy-parallax-hero.preview.emergentagent.com/", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Step 2: Login with password
            print("🔐 Attempting to login with password...")
            
            # Wait for password input field
            password_input = page.locator('input[type="password"]').first
            await password_input.wait_for(state="visible", timeout=10000)
            
            # Fill password
            await password_input.fill("studio149")
            await asyncio.sleep(500)
            
            # Click Potvrdi button
            potvrdi_button = page.locator('button:has-text("Potvrdi")')
            await potvrdi_button.click()
            
            print("⏳ Waiting for dashboard to load...")
            await asyncio.sleep(4)
            
            # Step 3: Navigate to Usluge (Services)
            print("📂 Navigating to Usluge section...")
            usluge_link = page.locator('a:has-text("Usluge"), button:has-text("Usluge")').first
            await usluge_link.click()
            await asyncio.sleep(2)
            
            # Step 4: Click on "Kartica Masaza za parove" tab
            print("📋 Opening 'Kartica Masaza za parove' tab...")
            parove_tab = page.locator('button:has-text("Kartica Masaza za parove"), div:has-text("Kartica Masaza za parove")').first
            await parove_tab.click()
            await asyncio.sleep(2)
            
            # Step 5: Get all service rows
            print("🔍 Finding all services in the category...")
            
            # Take screenshot to see current state
            await page.screenshot(path="/tmp/couples_services_list.png")
            print("📸 Screenshot saved: /tmp/couples_services_list.png")
            
            # Step 6: Update each service
            updates_successful = 0
            updates_failed = 0
            
            for service_name, correct_price in CORRECT_PRICES.items():
                try:
                    print(f"\n🔧 Processing: {service_name} → {correct_price} RSD")
                    
                    # Find the row for this service
                    # Try different locator strategies
                    service_row = page.locator(f'tr:has-text("{service_name}"), div:has-text("{service_name}")').first
                    
                    # Check if service exists
                    if not await service_row.is_visible(timeout=2000):
                        print(f"   ⚠️  Service not found in UI: {service_name}")
                        updates_failed += 1
                        continue
                    
                    # Find and click edit button (pencil icon)
                    edit_button = service_row.locator('button[aria-label*="edit"], button:has(svg), [role="button"]:has(svg)').first
                    await edit_button.click()
                    await asyncio.sleep(1500)
                    
                    # Find price input field in the modal/form
                    # Try various selectors for price field
                    price_field = page.locator(
                        'input[name="price"], input[name="cena"], input[label*="Cena"], '
                        'input[placeholder*="Cena"], input[placeholder*="Price"]'
                    ).first
                    
                    await price_field.wait_for(state="visible", timeout=5000)
                    
                    # Clear and fill with correct price
                    await price_field.clear()
                    await price_field.fill(str(correct_price))
                    await asyncio.sleep(500)
                    
                    # Find and click Save button
                    save_button = page.locator(
                        'button:has-text("Sačuvaj"), button:has-text("Save"), '
                        'button[type="submit"]'
                    ).first
                    await save_button.click()
                    await asyncio.sleep(1500)
                    
                    print(f"   ✅ Successfully updated to {correct_price} RSD")
                    updates_successful += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to update: {str(e)}")
                    updates_failed += 1
                    
                    # Take screenshot of error state
                    await page.screenshot(path=f"/tmp/error_{service_name.replace(' ', '_')}.png")
            
            # Final screenshot
            print("\n📸 Taking final screenshot...")
            await page.screenshot(path="/tmp/couples_prices_after_update.png")
            
            # Summary
            print("\n" + "="*60)
            print("📊 UPDATE SUMMARY")
            print("="*60)
            print(f"✅ Successful updates: {updates_successful}")
            print(f"❌ Failed updates: {updates_failed}")
            print(f"📝 Total services: {len(CORRECT_PRICES)}")
            print("="*60)
            
            if updates_successful == len(CORRECT_PRICES):
                print("\n🎉 ALL PRICES SUCCESSFULLY UPDATED!")
                return 0
            else:
                print("\n⚠️  SOME UPDATES FAILED - Manual intervention may be needed")
                return 1
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            await page.screenshot(path="/tmp/critical_error.png")
            print("📸 Error screenshot saved: /tmp/critical_error.png")
            return 1
            
        finally:
            await browser.close()
            print("\n🔒 Browser closed")

if __name__ == "__main__":
    print("="*60)
    print("🏥 COUPLES MASSAGE PRICE CORRECTION SCRIPT")
    print("="*60)
    print(f"Target: https://wavy-parallax-hero.preview.emergentagent.com/")
    print(f"Services to update: {len(CORRECT_PRICES)}")
    print("="*60)
    print()
    
    exit_code = asyncio.run(update_couples_prices())
    sys.exit(exit_code)
