import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Input file with all the base URLs
input_file = "chegg_all_urls.txt"
# Output file to save the paginated URLs
output_file = "chegg_paginated_urls.txt"
# Temporary file to store remaining URLs
temp_file = "temp_chegg_urls.txt"

# Function to set up undetected-chromedriver
def setup_driver():
    options = uc.ChromeOptions()
    # Add any options you need (e.g., headless mode)
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    driver = uc.Chrome(options=options)
    return driver

# Function to get the total number of pages using Selenium
def get_total_pages(driver, url):
    try:
        driver.get(url)
        # Wait for the pagination element to be present
        pagination_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#eggshell-2 > ul > li:nth-child(6)'))
        )
        total_pages = int(pagination_element.text.strip())
        return total_pages
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return -1  # Indicate an error with -1

# Function to generate and save paginated URLs
def generate_paginated_urls(input_file, output_file):
    driver = setup_driver()
    with open(input_file, 'r') as infile, open(output_file, 'a') as outfile, open(temp_file, 'w') as temp:
        for base_url in infile:
            base_url = base_url.strip()
            total_pages = get_total_pages(driver, base_url)
            
            if total_pages == -1:
                print(f"Stopping script due to an error at {base_url}.")
                break  # Stop the script if an error occurred
            
            # Write paginated URLs to the output file
            for page in range(1, total_pages + 1):
                if page == 1:
                    outfile.write(f"{base_url}\n")
                else:
                    paginated_url = f"{base_url}?page={page}"
                    outfile.write(f"{paginated_url}\n")
            
            # Print status and delay to avoid server overload
            print(f"Processed {base_url} with {total_pages} pages.")
            time.sleep(1)  # Optional delay
            
        # Write unprocessed URLs to a temporary file for later resumption
        temp.write(f"{base_url}\n")
    
    # Close the driver after finishing
    driver.quit()
    
    # Replace input file with the remaining URLs in temp file
    import os
    os.replace(temp_file, input_file)

# Run the function to generate paginated URLs
generate_paginated_urls(input_file, output_file)

print(f"Script completed. Processed URLs have been saved to {output_file}. Remaining URLs are in {input_file}.")
