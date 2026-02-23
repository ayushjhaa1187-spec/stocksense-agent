from playwright.sync_api import sync_playwright, expect
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to page...")
        page.goto("http://localhost:8000")

        # Check title
        title = page.title()
        print(f"Page title: {title}")
        assert "StockSense Agent" in title

        # Press Tab to focus the skip link
        print("Pressing Tab...")
        page.keyboard.press("Tab")

        # Wait for transition (CSS transition: top 0.3s)
        time.sleep(0.5)

        skip_link = page.locator(".skip-link")

        # Check if focused
        print("Checking focus...")
        active_element_class = page.evaluate("document.activeElement.className")
        print(f"Active element class: {active_element_class}")
        assert "skip-link" in active_element_class, "Skip link should be focused"

        # Check visibility
        box = skip_link.bounding_box()
        print(f"Bounding box: {box}")
        assert box['y'] >= 0, "Skip link should be visible at top of page"

        # Take screenshot
        page.screenshot(path="verification/skip-link-focused.png")
        print("Screenshot saved to verification/skip-link-focused.png")

        # Press Enter to activate link
        print("Pressing Enter...")
        page.keyboard.press("Enter")

        # Wait for URL change
        try:
            # wait_for_url matches exact URL or regex/glob.
            # Using wait_for_function to check location.hash
            page.wait_for_function("window.location.hash === '#main-content'", timeout=3000)
            print("URL updated successfully.")
        except Exception as e:
            print(f"Timeout waiting for URL update: {e}")

        print(f"Current URL: {page.url}")
        assert "#main-content" in page.url, "URL should contain fragment #main-content"

        browser.close()

if __name__ == "__main__":
    run()
