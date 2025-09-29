# work click on the title and open it but the problem is not fine the imge url


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

    # 1. Create a list of ISBNs to search for
    isbns = ["9780132350884", "9780201633610", "9780134494166"]

    # 2. Loop through each ISBN in the list
    for isbn in isbns:
        print(f"\n--- Searching for ISBN: {isbn} ---")
        page.goto("https://www.amazon.com")

        # 3. Wait for the search box
        page.wait_for_selector("input#twotabsearchtextbox")
        # 4. Type the current ISBN
        page.fill("input#twotabsearchtextbox", isbn)

        # 5. Press Enter (submit search)
        page.keyboard.press("Enter")
        # 6. Wait for search results to load
        page.wait_for_selector("div.s-main-slot")

        first_result_link = page.query_selector("div[data-cy='title-recipe'] a")
        if first_result_link:
            # Get the link's URL (href attribute)
            link_url = first_result_link.get_attribute("href")
            # Get the visible text of the link
            link_text = first_result_link.inner_text()
            first_result_link.click()
            print(f"Found Result!")
            print(f"Title: {link_text}")
            print(f"URL: https://www.amazon.com{link_url}") # Using .com to match the goto
            
            # Wait for the product page to load by waiting for the title
            page.wait_for_selector("#productTitle")

            # Extract and print the title
            title_element = page.query_selector("#productTitle")
            title = title_element.inner_text() if title_element else "Title not found"
            
            # Select the main image element using its ID: #landingImage
            image_element = page.query_selector("#landingImage")

            # Get the 'src' attribute from the image element
            image_url = (
                image_element.get_attribute("src")
                if image_element
                else "Image URL not found"
            )

            print("\n--- Product Details ---")
            print(f"Book Title: {title}")
            print(f"Image URL: {image_url}")

        else:
            print(f"\nCould not find the first result link for ISBN: {isbn}")
        
        # A short delay before the next search
        time.sleep(2)

    print("\n--- Scraping finished ---")
    time.sleep(5)
    browser.close()
