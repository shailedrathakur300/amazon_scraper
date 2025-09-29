import pandas as pd

# import requests
from bs4 import BeautifulSoup
import re
import time
import requests

# Function to get headers for requests (to mimic a browser)


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def get_book_info(isbn):
    try:
        image_url = None

        # Try amazon.com first
        print(f"Searching for product on amazon.com for ISBN: {isbn}")
        search_url = "https://www.amazon.com/s"
        params = {"k": isbn}
        r = requests.get(search_url, params=params, headers=get_headers(), timeout=10)
        if r.status_code != 200:
            print(f"Failed to fetch amazon.com search page: {r.status_code}")
        soup = BeautifulSoup(r.text, "lxml")

        # Fallback: any link with /dp/ in href
        product_link = soup.select_one("a[href*='/dp/']")
        if product_link:
            print("Product found on amazon.com")
            href = product_link.get("href", "")
            if href:
                if isinstance(href, list):
                    href_str = href[0] if href else ""
                else:
                    href_str = href
                if href_str.startswith('/'):
                    product_url = f"https://www.amazon.com{href_str}"
                else:
                    product_url = href_str
                print(f"Visiting product page: {product_url}")

                # Visit product page for .com
                r = requests.get(product_url, headers=get_headers(), timeout=10)
                if r.status_code != 200:
                    print(f"Failed to fetch amazon.com product page: {r.status_code}")
                soup = BeautifulSoup(r.text, "lxml")

                print("Searching for image on amazon.com")

                # Try multiple selectors for image
                img_selectors = ["#landingImage", "#main-image-container img", ".a-dynamic-image", "img#imgTagWrapperId img"]
                for selector in img_selectors:
                    img_element = soup.select_one(selector)
                    if img_element:
                        # Try src first, then data-a-dynamic-image or other attributes
                        image_url = img_element.get("src") or img_element.get("data-a-dynamic-image") or img_element.get("data-old-hires")
                        if image_url:
                            print(f"Image found on amazon.com using selector '{selector}': {image_url}")
                            break
                        else:
                            print(f"Found element with selector '{selector}' but no image URL attribute")
                    else:
                        print(f"No element found with selector '{selector}' on amazon.com")

                if not image_url:
                    print("No image found on amazon.com")

        if not image_url:
            if product_link:
                print("Image not found on amazon.com, searching on amazon.in")
            else:
                print("No product found on amazon.com, searching on amazon.in")
            # Try amazon.in
            search_url_in = "https://www.amazon.in/s"
            params = {"k": isbn}
            r_in = requests.get(search_url_in, params=params, headers=get_headers(), timeout=10)
            if r_in.status_code != 200:
                print(f"Failed to fetch amazon.in search page: {r_in.status_code}")
            soup_in = BeautifulSoup(r_in.text, "lxml")

            # Fallback: any link with /dp/ in href
            product_link_in = soup_in.select_one("a[href*='/dp/']")
            if product_link_in:
                print("Product found on amazon.in")
                href_in = product_link_in.get("href", "")
                if href_in:
                    if isinstance(href_in, list):
                        href_str = href_in[0] if href_in else ""
                    else:
                        href_str = href_in
                    if href_str.startswith('/'):
                        product_url_in = f"https://www.amazon.in{href_str}"
                    else:
                        product_url_in = href_str
                    print(f"Visiting product page on amazon.in: {product_url_in}")

                    # Visit product page for .in
                    r_in = requests.get(product_url_in, headers=get_headers(), timeout=10)
                    if r_in.status_code != 200:
                        print(f"Failed to fetch amazon.in product page: {r_in.status_code}")
                    soup_in = BeautifulSoup(r_in.text, "lxml")

                    print("Searching for image on amazon.in")

                    # Try multiple selectors for image on .in
                    img_selectors_in = ["#landingImage", "#main-image-container img", ".a-dynamic-image", "img#imgTagWrapperId img"]
                    for selector in img_selectors_in:
                        img_element_in = soup_in.select_one(selector)
                        if img_element_in:
                            image_url = img_element_in.get("src") or img_element_in.get("data-a-dynamic-image") or img_element_in.get("data-old-hires")
                            if image_url:
                                print(f"Image found on amazon.in using selector '{selector}': {image_url}")
                                break
                            else:
                                print(f"Found element with selector '{selector}' on amazon.in but no image URL attribute")
                        else:
                            print(f"No element found with selector '{selector}' on amazon.in")

                    if not image_url:
                        print("No image found on amazon.in")
            else:
                print("No product found on amazon.in")

        if image_url:
            print(f"Final image URL for ISBN {isbn}: {image_url}")
        else:
            print(f"No image URL found for ISBN {isbn}")

        return (isbn, image_url)

    except Exception as e:
        print(f"Error for {isbn}: {e}")
        return (isbn, None)


"""
# Path to your Excel file (note: it's spelled "exelbook.xlsx" in your code)
excel_file_path = "exelbook.xlsx"

try:
    # Load the Excel file to inspect sheets
    excel_file = pd.ExcelFile(excel_file_path)

    # Get the list of sheet names
    sheet_names = excel_file.sheet_names
    num_sheets = len(sheet_names)

    print(f"Total number of spreadsheets (sheets) in '{
          excel_file_path}': {num_sheets}")
    print("Sheet names:")
    for i, name in enumerate(sheet_names, start=1):
        print(f"  {i}. {name}")
    print("-" * 50)

    # Loop through each sheet and display books
    for sheet_name in sheet_names:
        print(f"\n--- Processing sheet: '{sheet_name}' ---")

        # Read the sheet into a DataFrame
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

        # Check if required columns exist
        if "name" not in df.columns or "ISBN 13" not in df.columns:
            print(
                f"Warning: Sheet '{
                    sheet_name
                }' does not have 'name' or 'ISBN 13' columns. Skipping."
            )
            continue


except FileNotFoundError:
    print(
        f"Error: The file '{
            excel_file_path
        }' was not found. Please check the file path and ensure it exists."
    )
except Exception as e:
    print(
        f"An error occurred: {
            e}. Please ensure the file is a valid XLSX and try again."
    )

"""
"""
# Main logic for testing with a single ISBN
if __name__ == "__main__":
    # Prompt for a single ISBN-13
    isbn = input("Enter a single ISBN-13 to test: ").strip()

    if not isbn:
        print("No ISBN provided. Exiting.")
        exit()

    print(f"Processing ISBN: {isbn}")
    isbn_result, image_url = get_book_info(isbn)

    print(f"  ISBN: {isbn_result}")
    print(f"  Image URL: {image_url if image_url else 'Not found'}")

    # Optional delay (remove if not needed for a single test)
    time.sleep(2)
    print("Test completed.")
    """

if __name__ == "__main__":
    excel_file_path = "exelbook.xlsx"

    try:
        # Load the Excel file
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names

        print(f"Available sheets: {sheet_names}")
        sheet_name = input("Enter the sheet name to process: ").strip()

        if sheet_name not in sheet_names:
            print("Invalid sheet name. Exiting.")
            exit()

        # Read the sheet into a DataFrame
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

        # Check if required columns exist
        if "ISBN 13" not in df.columns:
            print("Error: 'ISBN 13' column not found. Exiting.")
            exit()

        # Prompt for row range
        start_row = int(input("Enter start row index (0-based): ").strip())
        end_row = int(input("Enter end row index (0-based, inclusive): ").strip())

        if start_row < 0 or end_row >= len(df) or start_row > end_row:
            print("Invalid row range. Exiting.")
            exit()

        # Slice the DataFrame
        selected_df = df.iloc[start_row : end_row + 1]

        # List to hold results
        results = []

        for index, row in selected_df.iterrows():
            isbn = str(row["ISBN 13"]).strip()
            if not isbn:
                continue
            print(f"Processing ISBN: {isbn}")
            isbn_result, image_url = get_book_info(isbn)
            results.append(
                {
                    "ISBN": isbn_result,
                    "Image URL": image_url if image_url else "Not found",
                }
            )
            time.sleep(2)  # Delay to avoid rate limiting

        # Create a DataFrame from results
        result_df = pd.DataFrame(results)

        # Display the table
        print("\nResults Table:")
        print(result_df.to_string(index=False))

    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
