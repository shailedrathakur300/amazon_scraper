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
        search_url = "https://www.amazon.com/s"
        params = {"k": isbn}
        r = requests.get(search_url, params=params, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        # Fallback: any link with /dp/ in href
        product_link = soup.select_one("a[href*='/dp/']")
        if not product_link:
            return (isbn, None, None)
        product_url = "https://www.amazon.com" + product_link.get("href")

        # Step 3: Visit product page
        r = requests.get(product_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        # Step 4a: Extract dimensions (verified selector)
        # Try multiple selectors for dimensions
        dimensions = None
        dimension_selectors = [
            "#rpi-attribute-book_details-dimensions .rpi-attribute-value span",
            "[data-feature-name='detailBullets'] span:contains('Dimensions')",
            "#detailBullets_feature_div span:contains('x')",
            ".a-section:contains('Dimensions') + .a-section span",
        ]

        for selector in dimension_selectors:
            try:
                if "contains" in selector:
                    # For complex selectors, use text search
                    elements = soup.find_all(
                        string=re.compile(r"\d+\.?\d*\s*x\s*\d+\.?\d*\s*x\s*\d+\.?\d*")
                    )
                    if elements:
                        dimensions = elements[0].strip()
                        break
                else:
                    element = soup.select_one(selector)
                    if element and element.text.strip():
                        dimensions = element.text.strip()
                        break
            except:
                continue

        # Step 4b: Extract image URL (verified selector)
        img_element = soup.select_one("#landingImage")
        image_url = img_element["src"] if img_element else None

        return (isbn, dimensions, image_url)

    except Exception as e:
        print(f"Error for {isbn}: {e}")
        return (isbn, None, None)


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
    isbn_result, dimensions, image_url = get_book_info(isbn)

    print(f"  ISBN: {isbn_result}")
    print(f"  Dimensions: {dimensions if dimensions else 'Not found'}")
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
            isbn_result, dimensions, image_url = get_book_info(isbn)
            results.append(
                {
                    "ISBN": isbn_result,
                    "Dimensions": dimensions if dimensions else "Not found",
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
