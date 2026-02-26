import os
import time
from playwright.sync_api import sync_playwright

def verify_accessibility():
    # Ensure index.html exists
    if not os.path.exists("index.html"):
        print("Error: index.html not found.")
        return

    file_path = os.path.abspath("index.html")
    file_url = f"file://{file_path}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(file_url)

        # 1. Verify smooth scrolling
        html_style = page.evaluate("window.getComputedStyle(document.documentElement).scrollBehavior")
        if html_style == 'smooth':
            print("PASS: Smooth scrolling is enabled.")
        else:
            print(f"FAIL: Smooth scrolling is NOT enabled (current: {html_style}).")

        # 2. Verify Skip Link existence
        skip_link = page.locator('.skip-link')
        if skip_link.count() == 0:
            print("FAIL: Skip link (.skip-link) not found.")
        else:
            print("PASS: Skip link found.")

            # 3. Verify it is hidden initially (or off-screen)
            # We'll check if it's off-screen (top < 0) or opacity 0 or visibility hidden
            # For this implementation, we expect it to be positioned off-screen.
            box = skip_link.bounding_box()
            # If it's completely off screen, bounding box might be None or have negative coordinates
            # Let's check computed style top
            top_val = page.evaluate("document.querySelector('.skip-link').getBoundingClientRect().top")

            if top_val < 0:
                 print("PASS: Skip link is initially off-screen.")
            else:
                 print(f"FAIL: Skip link is NOT initially off-screen (top: {top_val}).")

            # 4. Verify it becomes visible on focus
            skip_link.focus()
            # Wait a bit for transition if any
            time.sleep(0.5)

            top_val_focused = page.evaluate("document.querySelector('.skip-link').getBoundingClientRect().top")
            if top_val_focused >= 0:
                print("PASS: Skip link is visible on focus.")
                # Take screenshot
                page.screenshot(path="verification/skip_link_focused.png")
                print("Screenshot saved to verification/skip_link_focused.png")
            else:
                print(f"FAIL: Skip link is NOT visible on focus (top: {top_val_focused}).")

            # 5. Verify clicking moves focus to main content
            # We can trigger a click or just press Enter since it's focused
            page.keyboard.press("Enter")

            # Check active element
            active_id = page.evaluate("document.activeElement.id")
            if active_id == "main-content":
                print("PASS: Focus moved to main content.")
            else:
                 # Sometimes focus isn't strictly on the element if it's not focusable (tabindex="-1" might be needed)
                 # But the URL hash should change
                 url = page.url
                 if "#main-content" in url:
                     print("PASS: URL updated to #main-content.")
                 else:
                     print(f"FAIL: Focus/URL did not update correctly (active: {active_id}, url: {url}).")

        browser.close()

if __name__ == "__main__":
    verify_accessibility()
