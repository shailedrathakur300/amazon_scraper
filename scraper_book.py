# work click on the title and open it but the problem is not fine the imge url


from playwright.sync_api import sync_playwright, Page
import pandas as pd
import time


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
            return isbn, "Result link not found", "Result link not found"

        # 4. Click the link and wait for the product page to load
        first_result_link.click()
        page.wait_for_selector("#productTitle")

        # 5. Extract the title
        title_element = page.query_selector("#productTitle")
        title = title_element.inner_text().strip() if title_element else "Title not found"

        # 6. Extract the image URL
        image_element = page.query_selector("#landingImage")
        image_url = image_element.get_attribute("src") if image_element else "Image URL not found"

        print("--- Product Details ---")
        print(f"Book Title: {title}")
        print(f"Image URL: {image_url}")

        return isbn, title, image_url

    except Exception as e:
        print(f"An error occurred while processing ISBN {isbn}: {e}")
        return isbn, "Error", str(e)


if __name__ == "__main__":
    # Path to your Excel file. Assuming it's in the 'old' directory based on your workspace.
    excel_file_path = "old/updatedexelbook.xlsx"

    try:
        # Load the Excel file to work with it
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names

        print(f"Available sheets: {sheet_names}")
        sheet_name = input("Enter the sheet name to process: ").strip()

        if sheet_name not in sheet_names:
            print("Invalid sheet name. Exiting.")
            exit()

        # Read the specific sheet into a DataFrame
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        print(f"Total rows in sheet: {len(df)}")

        # Check if required columns exist
        if "ISBN 13" not in df.columns:
            print("Error: 'ISBN 13' column not found. Exiting.")
            exit()

        # Add columns for the scraped data if they don't exist
        if "Scraped Title" not in df.columns:
            df["Scraped Title"] = ""
        if "Image URL" not in df.columns:
            df["Image URL"] = ""

        # Get user input for row range
        start_row = int(input("Enter start row index (0-based): ").strip())
        end_row = int(input("Enter end row index (0-based, inclusive): ").strip())

        if start_row < 0 or end_row >= len(df) or start_row > end_row:
            print("Invalid row range. Exiting.")
            exit()

        # Launch the browser once before the loop
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
                # Ensure ISBN is a clean string
                isbn_val = df.loc[i, "ISBN 13"]
                isbn = str(isbn_val).strip() if pd.notna(isbn_val) else ""

                if not isbn or isbn == "nan":
                    print(f"Skipping row {i}: No valid ISBN")
                    continue

                print(f"Processing row {i}, ISBN: {isbn}")

                # Get book info using the single browser page
                isbn_result, title, image_url = get_book_info(page, isbn)

                # Update the DataFrame with the new data
                df.loc[i, "Scraped Title"] = title
                df.loc[i, "Image URL"] = image_url

                results.append(
                    {
                        "Row": i,
                        "ISBN": isbn_result,
                        "Title": title,
                        "Image URL": image_url if image_url else "Not found",
                    }
                )

                time.sleep(3)  # Wait before the next request

            # Close the browser after the loop is finished
            browser.close()

        # Save the updated DataFrame back to the same sheet in the Excel file
        with pd.ExcelWriter(
            excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\nExcel file '{excel_file_path}' has been updated!")

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
