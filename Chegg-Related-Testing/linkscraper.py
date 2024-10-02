import os
from bs4 import BeautifulSoup

# Define paths
html_directory = r"C:\Users\MCBat\Downloads\files"
output_file_path = r"C:\Users\MCBat\OneDrive\Desktop\Education-Webscraper\NEW_unique_chegg_links.txt"

# Create a set to keep track of links to avoid duplicates within this session
session_links = set()

# Open the output file in append mode
with open(output_file_path, 'a', encoding='utf-8') as output_file:
    # Iterate through each HTML file in the directory
    for filename in os.listdir(html_directory):
        if filename.endswith('.html'):
            file_path = os.path.join(html_directory, filename)
            print(f"Processing file: {file_path}")

            # Read the HTML content from the file
            try:
                with open(file_path, 'r', encoding='utf-8') as html_file:
                    html_content = html_file.read()

                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all 'a' tags with href attributes containing 'chegg.com'
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if 'chegg.com' in href and href not in session_links:
                        # Save each unique Chegg link to the output file
                        output_file.write(f"{href}\n")
                        session_links.add(href)
                        print(f"Added Chegg link: {href}")

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

print(f"Completed processing all files. Saved links to {output_file_path}.")
