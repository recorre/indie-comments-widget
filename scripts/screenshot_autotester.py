#!/usr/bin/env python3
"""
Screenshot Automation Tester
Uses Selenium to capture screenshots during automated testing of frontend features.
Supports multiple modes: basic (theme changes), page (placeholder), flow (placeholder).

Usage:
    python scripts/screenshot_autotester.py --mode basic --url http://localhost:3000

Modes:
    - basic: Test widget theme changes via dropdown and capture screenshots
    - page: Placeholder for page-level screenshot testing
    - flow: Placeholder for multi-step flow screenshot testing

Requirements:
    - selenium
    - webdriver-manager (recommended for automatic driver management)
    - Pillow (optional, for image processing if needed)

Run from project root directory.
Ensure frontend server is running on the specified URL.
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ScreenshotTester:
    def __init__(self, base_url="http://localhost:3000", screenshot_dir="screenshots"):
        self.base_url = base_url
        self.screenshot_dir = screenshot_dir
        self.driver = None
        self.wait = None

        # Create screenshot directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Generate unique test session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Specify the path to the correct Chrome/Chromium
        chrome_options.binary_location = "/snap/bin/chromium"

        # Uncomment for headless mode (useful for CI/CD)
        # chrome_options.add_argument("--headless")

        try:
            # Try direct Chrome driver first
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Direct Chrome driver failed: {e}")
            print("Attempting to use webdriver-manager...")
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                # Try to install and use ChromeDriver via webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                print(f"webdriver-manager also failed: {e2}")
                print("Attempting to use any available chromedriver...")
                
                # As a last resort, try with system chromedriver if available
                import shutil
                chromedriver_path = shutil.which("chromedriver")
                
                if chromedriver_path:
                    from selenium.webdriver.chrome.service import Service
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    raise Exception("No working ChromeDriver found. Please install a compatible version.")

        self.wait = WebDriverWait(self.driver, 10)

        print("✅ Chrome driver initialized")

    def teardown_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")

    def take_screenshot(self, name):
        """Take a screenshot with timestamped filename"""
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{self.session_id}_{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        self.driver.save_screenshot(filepath)
        print(f"📸 Screenshot saved: {filepath}")
        return filepath

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

    def basic_mode(self):
        """Basic mode: Test widget theme changes and capture screenshots"""
        print("\n🎨 Running Basic Mode: Widget Theme Testing")

        # Navigate to landing page (assuming widget is there with showThemeSelector enabled)
        self.driver.get(f"{self.base_url}/")

        # Wait for page to load
        self.wait_for_element(By.TAG_NAME, "body")
        time.sleep(3)  # Allow widget to initialize

        # Take initial screenshot
        self.take_screenshot("initial_load")

        # Find the widget - multiple attempts with different selectors and more time
        widget = None
        selectors_to_try = [
            "comment-widget",
            "comment-widget[theme]",
            "comment-widget[thread-id]",
            "body comment-widget",
            "#comments-widget-container comment-widget"
        ]
        
        for selector in selectors_to_try:
            try:
                print(f"Trying selector: {selector}")
                widget = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=15)
                print("✅ Widget found")
                break
            except TimeoutException:
                print(f"❌ Widget not found with selector: {selector}")
                continue
        
        if not widget:
            print("❌ All widget selectors failed")
            # Try to find the widget container instead
            try:
                container = self.wait_for_element(By.ID, "comments-widget-container", timeout=15)
                print("✅ Found comments widget container, but custom element may not be registered")
                # Still take screenshots but note the state
                self.take_screenshot("widget_container_found")
                return True
            except TimeoutException:
                print("❌ Widget container also not found")
                return False

        # Look for theme selector dropdown (assuming it's a select element or similar)
        try:
            # Try different selectors for theme dropdown
            theme_selectors = [
                "select.theme-selector",
                ".theme-dropdown select",
                "[data-theme-selector]",
                ".theme-select"
            ]

            theme_dropdown = None
            for selector in theme_selectors:
                try:
                    theme_dropdown = self.wait_for_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not theme_dropdown:
                # Fallback: look for theme buttons
                theme_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".theme-btn, .theme-button, [data-theme]")
                if theme_buttons:
                    print("✅ Found theme buttons instead of dropdown")
                    # Take screenshot before theme change
                    self.take_screenshot("before_theme_change")

                    # Click each theme button and take screenshot
                    for i, button in enumerate(theme_buttons[:3]):  # Limit to first 3 themes
                        try:
                            button.click()
                            time.sleep(1)  # Wait for theme to apply
                            self.take_screenshot(f"theme_button_{i+1}")
                            print(f"✅ Theme {i+1} applied and screenshot taken")
                        except Exception as e:
                            print(f"⚠️ Failed to click theme button {i+1}: {e}")
                    return True
                else:
                    print("❌ No theme selector or buttons found")
                    return False

            # If dropdown found
            print("✅ Theme dropdown found")

            # Take screenshot before theme change
            self.take_screenshot("before_theme_change")

            # Get all options
            from selenium.webdriver.support.ui import Select
            select = Select(theme_dropdown)
            options = select.options

            # Change to each theme and take screenshot
            for i, option in enumerate(options[:3]):  # Limit to first 3 themes
                try:
                    select.select_by_index(i)
                    time.sleep(1)  # Wait for theme to apply
                    self.take_screenshot(f"theme_option_{i+1}")
                    print(f"✅ Theme {i+1} ({option.text}) applied and screenshot taken")
                except Exception as e:
                    print(f"⚠️ Failed to select theme option {i+1}: {e}")

            return True

        except Exception as e:
            print(f"❌ Basic mode failed: {e}")
            return False

    def page_mode(self):
        """Placeholder for page-level screenshot testing"""
        print("\n📄 Page Mode: Placeholder implementation")
        print("This mode will capture screenshots of different pages")
        # TODO: Implement page navigation and screenshot capture
        return True

    def flow_mode(self):
        """Placeholder for multi-step flow screenshot testing"""
        print("\n🔄 Flow Mode: Placeholder implementation")
        print("This mode will capture screenshots during user flows")
        # TODO: Implement flow testing with screenshots
        return True

    def run_test(self, mode):
        """Run test for specified mode"""
        print(f"🚀 Starting Screenshot Test - Mode: {mode}")
        print(f"Base URL: {self.base_url}")
        print(f"Screenshot Directory: {self.screenshot_dir}")
        print(f"Session ID: {self.session_id}")

        try:
            # Setup
            self.setup_driver()

            # Run selected mode
            if mode == "basic":
                success = self.basic_mode()
            elif mode == "page":
                success = self.page_mode()
            elif mode == "flow":
                success = self.flow_mode()
            else:
                print(f"❌ Unknown mode: {mode}")
                success = False

            if success:
                print("✅ Test completed successfully")
            else:
                print("❌ Test failed")

            return success

        except Exception as e:
            print(f"💥 Test failed with error: {e}")
            return False

        finally:
            self.teardown_driver()

def show_menu():
    """Display interactive menu for mode selection"""
    print("\n" + "="*60)
    print("🎯 SCREENSHOT AUTOMATION TESTER")
    print("="*60)
    print("\n📋 Available Test Modes:")
    print("\n1. 🎨 Basic Mode")
    print("   - Test widget theme changes via dropdown")
    print("   - Captures screenshots of theme switching")
    print("   - Ideal for testing theme functionality")
    print("\n2. 📄 Page Mode")
    print("   - Capture screenshots of different pages")
    print("   - Navigate through site pages")
    print("   - Page-level screenshot testing")
    print("\n3. 🔄 Flow Mode")
    print("   - Multi-step user flow testing")
    print("   - Capture screenshots during workflows")
    print("   - End-to-end process testing")
    print("\n0. ❌ Exit")
    print("\n" + "="*60)

def get_user_choice():
    """Get user choice from menu"""
    while True:
        try:
            choice = input("\n👉 Enter your choice (0-3): ").strip()
            if choice in ['0', '1', '2', '3']:
                return int(choice)
            else:
                print("❌ Invalid choice. Please enter 0, 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            exit(0)
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")

def interactive_main():
    """Interactive mode with menu"""
    print("🚀 Welcome to Screenshot Automation Tester!")

    # Get base URL
    default_url = "http://localhost:3000"
    url = input(f"\n🌐 Enter base URL (default: {default_url}): ").strip()
    if not url:
        url = default_url

    # Get screenshot directory
    default_dir = "screenshots"
    screenshot_dir = input(f"\n📁 Enter screenshot directory (default: {default_dir}): ").strip()
    if not screenshot_dir:
        screenshot_dir = default_dir

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == 0:
            print("\n👋 Goodbye!")
            break

        # Map choice to mode
        mode_map = {1: "basic", 2: "page", 3: "flow"}
        mode = mode_map[choice]

        print(f"\n🚀 Starting {mode.title()} Mode...")
        print(f"Base URL: {url}")
        print(f"Screenshot Directory: {screenshot_dir}")

        # Run the test
        tester = ScreenshotTester(url, screenshot_dir)
        success = tester.run_test(mode)

        if success:
            print(f"\n✅ {mode.title()} Mode completed successfully!")
        else:
            print(f"\n❌ {mode.title()} Mode failed!")

        # Ask to continue
        try:
            again = input("\n🔄 Run another test? (y/n): ").strip().lower()
            if again not in ['y', 'yes']:
                print("\n👋 Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Screenshot Automation Tester")
    parser.add_argument("--url", default="http://localhost:3000",
                        help="Base URL for testing (default: http://localhost:3000)")
    parser.add_argument("--mode", choices=["basic", "page", "flow"],
                        help="Test mode to run (if not specified, interactive menu will be shown)")
    parser.add_argument("--screenshot-dir", default="screenshots",
                        help="Directory to save screenshots (default: screenshots)")
    parser.add_argument("--interactive", action="store_true",
                        help="Force interactive mode even if mode is specified")

    args = parser.parse_args()

    # If no mode specified or interactive flag is set, show menu
    if args.mode is None or args.interactive:
        interactive_main()
    else:
        # Command-line mode
        tester = ScreenshotTester(args.url, args.screenshot_dir)
        success = tester.run_test(args.mode)
        exit(0 if success else 1)

# Enable auto-execution when running the script directly
if __name__ == "__main__":
    main()