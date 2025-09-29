from playwright.sync_api import sync_playwright
import time

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
