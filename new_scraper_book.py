"""
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright
import time


def get_amazon_book_details(isbn):
    with sync_playwright() as p:
        # 1. Launch Chrome (non-headless to see actions)
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # 2. Set headers to look like a real browser
        page.set_extra_http_headers(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )
            }
        )

        # 3. Open Amazon homepage
        page.goto("https://www.amazon.com")
        # wait for search box
        page.wait_for_selector("input#twotabsearchtextbox")

        # 4. Search ISBN
        page.fill("input#twotabsearchtextbox", isbn)
        page.keyboard.press("Enter")

        # 5. Wait for results container
        page.wait_for_selector("div.s-main-slot")

        # 6. Select the first result
        # works for most Amazon search results
        first_result = page.query_selector("h2 a")
        if not first_result:
            print(f"No results found for ISBN: {isbn}")
            browser.close()
            return

        # 7. Extract link & text
        link_url = first_result.get_attribute("href")
        link_text = first_result.inner_text()

        # 8. Click the first result
        first_result.click()

        # 9. Wait for product page title
        page.wait_for_selector("#productTitle")
        product_title_el = page.query_selector("#productTitle")
        product_title = (
            product_title_el.inner_text().strip()
            if product_title_el
            else "Title not found"
        )

        # 10. Extract main image
        image_el = page.query_selector("#landingImage")
        image_url = image_el.get_attribute("src") if image_el else "Image URL not found"

        # 11. Print results
        print("\n--- Product Details ---")
        print(f"Search Result Title: {link_text}")
        print(f"Product Page Title: {product_title}")
        print(f"Product URL: https://www.amazon.com{link_url}")
        print(f"Image URL: {image_url}")

        browser.close()


if __name__ == "__main__":
    isbn_number = "9780132350884"
    get_amazon_book_details(isbn_number)
"""

"""
from playwright.sync_api import sync_playwright


def get_amazon_book_details(isbn):
    with sync_playwright() as p:
        # 1. Launch Chrome
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # 2. Set headers to look like a real browser
        page.set_extra_http_headers(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )
            }
        )

        # 3. Go to Amazon
        page.goto("https://www.amazon.com")
        page.wait_for_selector("input#twotabsearchtextbox")

        # 4. Search ISBN
        page.fill("input#twotabsearchtextbox", isbn)
        page.keyboard.press("Enter")

        # 5. Wait for results container
        page.wait_for_selector("div.s-main-slot")

        # 6. Click the first search result
        first_result = page.query_selector("h2 a")
        if not first_result:
            print(f"No results found for ISBN: {isbn}")
            browser.close()
            return

        link_url = first_result.get_attribute("href")
        link_text = first_result.inner_text()
        first_result.click()

        # 7. Wait for product page title (ensures JS loaded)
        page.wait_for_selector("#productTitle", timeout=15000)
        # optional small wait for extra JS rendering
        page.wait_for_timeout(3000)

        # 8. Extract product title
        title_el = page.query_selector("#productTitle")
        product_title = title_el.inner_text().strip() if title_el else "Title not found"

        # 9. Extract main image with fallback selectors
        image_selectors = ["#landingImage", ".imgTagWrapper img", ".a-dynamic-image"]
        image_url = None
        for sel in image_selectors:
            el = page.query_selector(sel)
            if el:
                image_url = el.get_attribute("src")
                break
        if not image_url:
            image_url = "Image URL not found"

        # 10. Print results
        print("\n--- Product Details ---")
        print(f"Search Result Title: {link_text}")
        print(f"Product Page Title: {product_title}")
        print(f"Product URL: https://www.amazon.com{link_url}")
        print(f"Image URL: {image_url}")

        browser.close()


if __name__ == "__main__":
    isbn_number = "9780132350884"
    get_amazon_book_details(isbn_number)

"""


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=False)
    page = browser.new_page()
    page.set_extra_http_headers(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        }
    )
    page.goto("https://www.amazon.in")

    # Search for the book by ISBN
    page.wait_for_selector("input#twotabsearchtextbox")
    isbn = "9780132350884"
    page.fill("input#twotabsearchtextbox", isbn)
    page.keyboard.press("Enter")

    # Wait for search results and find the first link
    page.wait_for_selector("div.s-main-slot")
    first_result_link = page.query_selector("div[data-cy='title-recipe'] a")

    if first_result_link:
        print("Found search result. Clicking link...")

        # --- NEW CODE STARTS HERE ---

        # 1. Click the link to navigate to the product page
        first_result_link.click()

        # 2. Wait for the product page to load by looking for a unique element
        # We use the image container's ID from your HTML: #imgTagWrapperId
        print("Waiting for product page to load...")
        page.wait_for_selector("#imgTagWrapperId")

        # 3. Extract the title
        title_element = page.query_selector("#productTitle")
        title = title_element.inner_text() if title_element else "Title not found"

        # 4. Select the main image element using its ID: #landingImage
        image_element = page.query_selector("#landingImage")

        # 5. Get the 'src' attribute from the image element
        image_url = (
            image_element.get_attribute("src")
            if image_element
            else "Image URL not found"
        )

        print("\n--- Product Details ---")
        print(f"Book Title: {title}")
        print(f"Image URL: {image_url}")

    else:
        print("\nCould not find the first result link on the search page.")

    time.sleep(5)
    browser.close()
