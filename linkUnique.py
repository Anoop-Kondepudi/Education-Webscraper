# Script to clean up duplicate links in the new file and compare with the backup

new_links_file_path = r"C:\Users\MCBat\OneDrive\Desktop\Education-Webscraper\NEW_unique_chegg_links.txt"
backup_links_file_path = r"C:\Users\MCBat\OneDrive\Desktop\Education-Webscraper\unqiue_chegg_links_backup.txt"

# Read all the links from the new file
with open(new_links_file_path, 'r') as new_file:
    new_links = new_file.readlines()

# Read all the links from the backup file
with open(backup_links_file_path, 'r') as backup_file:
    backup_links = set(backup_file.readlines())

# Remove duplicates within the new file
unique_new_links = set(new_links)

# Remove links that are in the backup
filtered_new_links = [link for link in unique_new_links if link not in backup_links]

# Save the cleaned links back to the new file
with open(new_links_file_path, 'w') as cleaned_file:
    cleaned_file.writelines(filtered_new_links)

print(f"Removed duplicates and filtered links from {new_links_file_path}.")


#Confirm:
'''# Paths to your files
new_links_path = r"C:\Users\MCBat\OneDrive\Desktop\Education-Webscraper\NEW_unique_chegg_links.txt"
backup_links_path = r"C:\Users\MCBat\OneDrive\Desktop\Education-Webscraper\unqiue_chegg_links_backup.txt"

# Load the links into sets
with open(new_links_path, 'r') as new_file:
    new_links = set([line.strip() for line in new_file.readlines()])

with open(backup_links_path, 'r') as backup_file:
    backup_links = set([line.strip() for line in backup_file.readlines()])

# Check for any overlap (should be empty if duplicates were removed correctly)
duplicates = new_links.intersection(backup_links)

print(f"Number of duplicates found in both files: {len(duplicates)}")
if len(duplicates) > 0:
    print("Some duplicates were not removed:")
    for duplicate in duplicates:
        print(duplicate)

# Check for duplicates within the new links set itself
internal_duplicates = len(new_links) < len(set(new_links))
if internal_duplicates:
    print("Duplicates found within the NEW list itself.")
else:
    print("No duplicates within the NEW list itself.")

# Output the counts for verification
print(f"Total unique links in NEW list: {len(new_links)}")
print(f"Total unique links in backup list: {len(backup_links)}")
'''