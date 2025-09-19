import pandas as pd
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


if __name__ == "__main__":
    excel_file_path = "exelbook.xlsx"

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
        # This creates a copy of the Excel data in memory that we can modify
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

        # Display the total number of rows for reference
        print(f"Total rows in sheet: {len(df)}")

        # Check if required columns exist
        if "ISBN 13" not in df.columns:
            print("Error: 'ISBN 13' column not found. Exiting.")
            exit()

        # Add new columns if they don't exist
        # This ensures we have places to store our scraped data
        if "Dimensions" not in df.columns:
            df["Dimensions"] = ""  # Create empty column for dimensions
        if "Image URL" not in df.columns:
            df["Image URL"] = ""  # Create empty column for image URLs

        # Get user input for row range
        start_row = int(input("Enter start row index (0-based): ").strip())
        end_row = int(input("Enter end row index (0-based, inclusive): ").strip())

        # Validate the row range to prevent errors
        if start_row < 0 or end_row >= len(df) or start_row > end_row:
            print("Invalid row range. Exiting.")
            exit()

        # Process each row in the specified range
        results = []  # For displaying results in terminal

        for i in range(start_row, end_row + 1):
            # Get the ISBN from the current row
            isbn = str(df.iloc[i]["ISBN 13"]).strip()

            if not isbn or isbn == "nan":  # Skip empty or invalid ISBNs
                print(f"Skipping row {i}: No valid ISBN")
                continue

            print(f"Processing row {i}, ISBN: {isbn}")

            # Scrape book information from Amazon
            isbn_result, dimensions, image_url = get_book_info(isbn)

            # Update the DataFrame with scraped data
            # .iloc[i] selects the specific row by index
            # We update the columns with our scraped data
            if dimensions:
                df.iloc[i, df.columns.get_loc("Dimensions")] = dimensions
            if image_url:
                df.iloc[i, df.columns.get_loc("Image URL")] = image_url

            # Store results for terminal display
            results.append(
                {
                    "Row": i,
                    "ISBN": isbn_result,
                    "Dimensions": dimensions if dimensions else "Not found",
                    "Image URL": image_url if image_url else "Not found",
                }
            )

            # Delay to avoid being blocked by Amazon
            time.sleep(2)

        # Save the updated DataFrame back to Excel
        # We need to handle multiple sheets properly
        with pd.ExcelWriter(
            excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as writer:
            # Write the updated sheet back
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Copy other sheets that weren't modified
            for other_sheet in sheet_names:
                if other_sheet != sheet_name:
                    other_df = pd.read_excel(excel_file_path, sheet_name=other_sheet)
                    other_df.to_excel(writer, sheet_name=other_sheet, index=False)

        print(f"\nExcel file '{excel_file_path}' has been updated!")

        # Display results in terminal as a table
        if results:
            result_df = pd.DataFrame(results)
            print("\nResults Table:")
            print(result_df.to_string(index=False))
        else:
            print("No results to display.")

    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
