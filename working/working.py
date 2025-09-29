from playwright.sync_api import sync_playwright


def get_first_available_book(isbns):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        page = browser.new_page()

        # Pretend to be a real browser
        page.set_extra_http_headers(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )
            }
        )

        for isbn in isbns:
            print(f"\nSearching for ISBN: {isbn}")
            try:
                page.goto("https://www.amazon.com")
                page.wait_for_selector("input#twotabsearchtextbox")
                page.fill("input#twotabsearchtextbox", isbn)
                page.keyboard.press("Enter")
                page.wait_for_selector("div.s-main-slot")

                # Get first search result
                first_result = page.query_selector("h2 a")
                if not first_result:
                    print(f"No results found for ISBN: {isbn}")
                    continue  # try next ISBN

                # Extract link & text
                link_url = first_result.get_attribute("href")
                link_text = first_result.inner_text()

                # Click the first result
                first_result.click()

                # Wait for product page
                page.wait_for_selector("#productTitle")
                product_title_el = page.query_selector("#productTitle")
                product_title = (
                    product_title_el.inner_text().strip()
                    if product_title_el
                    else "Title not found"
                )

                # Extract main image
                image_el = page.query_selector("#landingImage")
                image_url = (
                    image_el.get_attribute("src") if image_el else "Image URL not found"
                )

                # Print result
                print("\n--- Product Details ---")
                print(f"Search Result Title: {link_text}")
                print(f"Product Page Title: {product_title}")
                print(f"Product URL: https://www.amazon.com{link_url}")
                print(f"Image URL: {image_url}")

                # Stop after first successful ISBN
                break

            except Exception as e:
                print(f"Error searching ISBN {isbn}: {e}")
                continue

        browser.close()


if __name__ == "__main__":
    isbn_list = ["9780132350884", "9780137081073", "9781491957660"]
    get_first_available_book(isbn_list)
