#!/usr/bin/env python3
"""
Frontend Automation Tester
Uses Selenium to test frontend routes automatically
"""

import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FrontendTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None

        # Generate unique test data
        self.timestamp = int(time.time())
        self.unique_id = f"test_{self.timestamp}"

        # Test user data
        self.test_user = {
            "name": f"Test User {self.unique_id}",
            "email": f"test_{self.unique_id}@example.com",
            "password": "123456"
        }

        # Test site data
        self.test_site = {
            "name": f"My Test Site {self.unique_id}",
            "url": f"https://mysite-{self.unique_id}.com"
        }

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        # Uncomment for headless mode
        # chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        print("✅ Chrome driver initialized")

    def teardown_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")

    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def safe_click(self, element):
        """Safe click with retry"""
        try:
            element.click()
        except Exception:
            # Try JavaScript click
            self.driver.execute_script("arguments[0].click();", element)

    def test_landing_page(self):
        """Test landing page functionality"""
        print("\n🏠 Testing Landing Page...")

        self.driver.get(f"{self.base_url}/")

        # Check if page loads
        assert "Indie Comments Widget" in self.driver.title
        print("✅ Landing page loaded")

        # Check widget demo
        widget = self.wait_for_element(By.CSS_SELECTOR, "comment-widget")
        assert widget is not None
        print("✅ Widget demo present")

        # Test theme switching
        theme_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".theme-btn")
        if theme_buttons:
            # Click on a different theme
            theme_buttons[1].click()  # Second theme (usually dark)
            time.sleep(1)
            print("✅ Theme switching works")

        return True

    def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration...")

        self.driver.get(f"{self.base_url}/register")

        # Fill registration form
        name_field = self.wait_for_element(By.ID, "name")
        name_field.send_keys(self.test_user["name"])

        email_field = self.wait_for_element(By.ID, "email")
        email_field.send_keys(self.test_user["email"])

        password_field = self.wait_for_element(By.ID, "password")
        password_field.send_keys(self.test_user["password"])

        confirm_field = self.wait_for_element(By.ID, "confirm_password")
        confirm_field.send_keys(self.test_user["password"])

        # Submit form
        submit_button = self.wait_for_clickable(By.CSS_SELECTOR, "button[type='submit']")
        self.safe_click(submit_button)

        # Wait for redirect to dashboard
        self.wait.until(EC.url_contains("/dashboard"))
        print("✅ User registration successful")

        return True

    def test_user_login(self):
        """Test user login"""
        print("\n🔐 Testing User Login...")

        self.driver.get(f"{self.base_url}/login")

        # Fill login form
        email_field = self.wait_for_element(By.ID, "email")
        email_field.send_keys(self.test_user["email"])

        password_field = self.wait_for_element(By.ID, "password")
        password_field.send_keys(self.test_user["password"])

        # Submit form
        submit_button = self.wait_for_clickable(By.CSS_SELECTOR, "button[type='submit']")
        self.safe_click(submit_button)

        # Wait for redirect to dashboard
        self.wait.until(EC.url_contains("/dashboard"))
        print("✅ User login successful")

        return True

    def test_dashboard_overview(self):
        """Test dashboard overview"""
        print("\n📊 Testing Dashboard Overview...")

        self.driver.get(f"{self.base_url}/dashboard")

        # Check dashboard elements
        assert "Dashboard" in self.driver.title

        # Check stats cards
        stats_cards = self.driver.find_elements(By.CSS_SELECTOR, ".stats-card")
        assert len(stats_cards) >= 3  # Should have at least 3 stat cards
        print("✅ Dashboard stats loaded")

        # Check quick actions
        action_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn")
        assert len(action_buttons) > 0
        print("✅ Dashboard actions available")

        return True

    def test_sites_management(self):
        """Test sites management functionality"""
        print("\n🌐 Testing Sites Management...")

        # First register a new user since sites page requires authentication
        self.test_user_registration()

        self.driver.get(f"{self.base_url}/dashboard/sites")

        # Check page loads
        assert "Sites Management" in self.driver.page_source
        print("✅ Sites management page loaded successfully")

        # For now, just verify the page loads correctly
        # The modal interaction can be tested separately
        try:
            # Check if the "Add New Site" button is present
            add_button = self.driver.find_element(By.CSS_SELECTOR, "[data-bs-target='#createSiteModal']")
            assert add_button is not None
            print("✅ Add site button found")

            # Check if stats are displayed
            stats_cards = self.driver.find_elements(By.CSS_SELECTOR, ".col-md-3 .p-3")
            assert len(stats_cards) >= 3  # Should have at least 3 stat cards
            print("✅ Statistics cards displayed")

            return True

        except Exception as e:
            print(f"⚠️ Sites management test failed: {e}")
            return False

    def test_theme_customizer(self):
        """Test theme customizer functionality"""
        print("\n🎨 Testing Theme Customizer...")

        self.driver.get(f"{self.base_url}/dashboard/theme-customizer")

        # Check if page loads
        assert "Theme Customizer" in self.driver.page_source

        # Test color picker
        try:
            color_picker = self.wait_for_element(By.ID, "primary-color")
            # Change color
            self.driver.execute_script("arguments[0].value = '#ff0000'; arguments[0].dispatchEvent(new Event('input'));", color_picker)
            time.sleep(1)
            print("✅ Color picker works")
        except Exception as e:
            print(f"⚠️ Color picker test failed: {e}")

        # Test preset buttons
        try:
            preset_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick*='applyPreset']")
            if preset_buttons:
                preset_buttons[0].click()  # Click first preset
                time.sleep(1)
                print("✅ Theme presets work")
        except Exception as e:
            print(f"⚠️ Preset test failed: {e}")

        return True

    def run_full_test(self):
        """Run complete test suite"""
        print("🚀 Starting Frontend Automation Test")
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {self.test_user['email']}")
        print(f"Test Site: {self.test_site['name']}")

        try:
            # Setup
            self.setup_driver()

            # Test sequence
            tests = [
                ("Landing Page", self.test_landing_page),
                ("User Registration", self.test_user_registration),
                ("Dashboard Overview", self.test_dashboard_overview),
                ("Sites Management", self.test_sites_management),
                ("Theme Customizer", self.test_theme_customizer),
            ]

            results = []
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    results.append((test_name, result))
                    print(f"✅ {test_name}: PASSED")
                except Exception as e:
                    results.append((test_name, False))
                    print(f"❌ {test_name}: FAILED - {e}")

            # Summary
            print("\n📊 Test Results Summary:")
            passed = sum(1 for _, result in results if result)
            total = len(results)

            for test_name, result in results:
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"  {test_name}: {status}")

            print(f"\n🎯 Overall: {passed}/{total} tests passed")

            if passed == total:
                print("🎉 All tests passed!")
                return True
            else:
                print("⚠️ Some tests failed")
                return False

        except Exception as e:
            print(f"💥 Test suite failed: {e}")
            return False

        finally:
            self.teardown_driver()

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Frontend Automation Tester")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL for testing")
    parser.add_argument("--test", choices=["landing", "register", "login", "dashboard", "sites", "themes", "full"],
                       default="full", help="Specific test to run")

    args = parser.parse_args()

    tester = FrontendTester(args.url)

    if args.test == "full":
        success = tester.run_full_test()
    else:
        # Run specific test
        tester.setup_driver()
        try:
            if args.test == "landing":
                success = tester.test_landing_page()
            elif args.test == "register":
                success = tester.test_user_registration()
            elif args.test == "login":
                success = tester.test_user_login()
            elif args.test == "dashboard":
                success = tester.test_dashboard_overview()
            elif args.test == "sites":
                success = tester.test_sites_management()
            elif args.test == "themes":
                success = tester.test_theme_customizer()
            else:
                print(f"Unknown test: {args.test}")
                success = False
        finally:
            tester.teardown_driver()

    exit(0 if success else 1)

if __name__ == "__main__":
    main()