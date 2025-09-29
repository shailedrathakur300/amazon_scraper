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
    page.goto("https://www.amazon.com")

    # 2. Wait for the search box
    page.wait_for_selector("input#twotabsearchtextbox")
    # 3. Type your search (title, ISBN, etc.)
    isbn = "9780132350884"  # example ISBN for "Clean Code"
    page.fill("input#twotabsearchtextbox", isbn)

    # 4. Press Enter (submit search)
    page.keyboard.press("Enter")
    # 5. Wait for search results to load
    page.wait_for_selector("div.s-main-slot")
    print(page.title())
    first_result_link = page.query_selector("div[data-cy='title-recipe'] a")
    if first_result_link:
        # Get the link's URL (href attribute)
        link_url = first_result_link.get_attribute("href")
        # Get the visible text of the link
        link_text = first_result_link.inner_text()
        first_result_link.click()
        print(f"\nFound Result!")
        print(f"Title: {link_text}")
        print(f"URL: https://www.amazon.in{link_url}")
        # 3. Extract the title
        page.wait_for_selector("#productTitle")

        # 6. Extract and print the title
        title = page.query_selector("#productTitle").inner_text()
        print("Book Title:", title)
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
        print("\nCould not find the first result link.")

    time.sleep(5)
    browser.close()
