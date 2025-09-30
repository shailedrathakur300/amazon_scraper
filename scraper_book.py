# work click on the title and open it but the problem is not fine the imge url


from playwright.sync_api import sync_playwright, Page
import pandas as pd
import time


# MODIFICATION: The function now returns dimensions instead of image_url.
def get_book_info(page: Page, isbn: str):
    """
    Searches for a book by its ISBN on Amazon and scrapes its details.
    """
    try:
        print(f"\n--- Searching for ISBN: {isbn} ---")
        page.goto("https://www.amazon.com")

        # 1. Wait for the search box and type the ISBN
        page.wait_for_selector("input#twotabsearchtextbox")
        page.fill("input#twotabsearchtextbox", isbn)

        # 2. Press Enter and wait for results
        page.keyboard.press("Enter")
        page.wait_for_selector("div.s-main-slot")

        # 3. Find the first search result link
        first_result_link = page.query_selector("div[data-cy='title-recipe'] a")
        if not first_result_link:
            print(f"Could not find the first result link for ISBN: {isbn}")
            # MODIFICATION: Return dimensions as "Not found" on failure.
            return isbn, "Result link not found", "Dimensions not found"

        # 4. Click the link and wait for the product page to load
        first_result_link.click(timeout=5000)
        page.wait_for_selector("#productTitle")

        # 5. Extract the title
        title_element = page.query_selector("#productTitle")
        title = (
            title_element.inner_text().strip() if title_element else "Title not found"
        )

        # 6. Extract the dimensions.
        dimensions = "Dimensions not found"
        try:
            # This single locator is robust. It finds any list item or table row
            # containing the text "Dimensions" and gets its full text content.
            dimension_locator = page.locator("li:has-text('Dimensions'), tr:has-text('Dimensions')").first
            
            # Get the full text (e.g., "Dimensions : 12.85 x 0.99 x 19.84 cm")
            full_text = dimension_locator.inner_text(timeout=5000)
            
            # Split the text at the colon and take the second part.
            dimensions = full_text.split(':', 1)[-1].strip()
            # dimensions = full_text.lower().replace("dimensions", "").replace(":", "").strip()

        except Exception as e:
            print(f"Could not find dimensions for ISBN {isbn}. Using default value.")

        """
                # MODIFICATION: Replaced image URL extraction with dimension scraping.
                # 6. Extract the dimensions with a primary and fallback method.
                dimensions = "Dimensions not found"
                
                # Primary Method: Check inside the detail bullets list.
                detail_bullets = page.query_selector("#detailBullets_feature_div")
                if detail_bullets:
                    dimension_item = detail_bullets.query_selector("li:has-text('Dimensions')")
                    if dimension_item:
                        span_element = dimension_item.query_selector("span.a-list-item > span:nth-of-type(2)")
                        if span_element:
                            dimensions = span_element.inner_text().strip()

                # Fallback Method: If not found, check the product details table.
                if dimensions == "Dimensions not found":
                    details_table = page.query_selector("#productDetailsTable")
                    if details_table:
                        rows = details_table.query_selector_all("tr")
                        for row in rows:
                            header = row.query_selector("th")
                            if header and "Dimensions" in header.inner_text():
                                value_cell = row.query_selector("td")
                                if value_cell:
                                    dimensions = value_cell.inner_text().strip()
                                    break
                
                # MODIFICATION: Updated the console log to show dimensions.
        """
        print("--- Product Details ---")
        print(f"Book Title: {title}")
        print(f"Scraped Dimensions: {dimensions}")

        # MODIFICATION: Return the scraped dimensions instead of image URL.
        return isbn, title, dimensions

    except Exception as e:
        print(f"An error occurred while processing ISBN {isbn}: {e}")
        # MODIFICATION: Return dimensions as "Error" on exception.
        return isbn, "Error", str(e)


if __name__ == "__main__":
    excel_file_path = "updated_September.xlsx"

    try:
        # Read all sheets into a dictionary of DataFrames
        all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
        sheet_names = list(all_sheets.keys())

        print(f"Available sheets: {sheet_names}")
        sheet_name = input("Enter the sheet name to process: ").strip()

        if sheet_name not in all_sheets:
            print("Invalid sheet name. Exiting.")
            exit()

        # Get the specific DataFrame to work on
        df = all_sheets[sheet_name]
        print(f"Total rows in sheet '{sheet_name}': {len(df)}")

        if "ISBN 13" not in df.columns:
            print("Error: 'ISBN 13' column not found. Exiting.")
            exit()

        # MODIFICATION: Add "Scraped Dimensions" column instead of "Image URL".
        # This will not touch an existing "Dimensions" column.
        if "Scraped Dimensions" not in df.columns:
            df["Scraped Dimensions"] = ""

        start_row = int(input("Enter start row index (0-based): ").strip())
        end_row = int(input("Enter end row index (0-based, inclusive): ").strip())

        if start_row < 0 or end_row >= len(df) or start_row > end_row:
            print("Invalid row range. Exiting.")
            exit()

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

            results = []
            for i in range(start_row, end_row + 1):
                isbn_val = df.loc[i, "ISBN 13"]
                isbn = str(isbn_val).strip() if pd.notna(isbn_val) else ""

                if not isbn or isbn == "nan":
                    print(f"Skipping row {i}: No valid ISBN")
                    continue

                print(f"Processing row {i}, ISBN: {isbn}")
                # MODIFICATION: The function now returns dimensions.
                isbn_result, title, dimensions = get_book_info(page, isbn)

                # MODIFICATION: Update the "Scraped Dimensions" column.
                df.loc[i, "Scraped Dimensions"] = dimensions
                # MODIFICATION: Also update the title in case it was corrected.
                df.loc[i, "Scraped Title"] = title


                # MODIFICATION: Update the results list to include dimensions.
                results.append(
                    {
                        "Row": i,
                        "ISBN": isbn_result,
                        "Title": title,
                        "Scraped Dimensions": dimensions,
                    }
                )
                time.sleep(3)

            browser.close()

        # **REVISED SAVING LOGIC**
        # Update the dictionary of sheets with our modified DataFrame
        all_sheets[sheet_name] = df

        # Write all sheets back to the Excel file, overwriting it
        with pd.ExcelWriter(excel_file_path, engine="openpyxl") as writer:
            for sheet, data in all_sheets.items():
                data.to_excel(writer, sheet_name=sheet, index=False)

        print(f"\nExcel file '{excel_file_path}' has been successfully updated!")

        if results:
            result_df = pd.DataFrame(results)
            print("\nSummary of Scraped Data:")
            print(result_df.to_string(index=False))
        else:
            print("No results to display.")

    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

