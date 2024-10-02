import pyautogui
import pyperclip
import time

time.sleep(5)  # Wait for 5 seconds

# Function to read the first link from the file and delete it
def read_and_remove_first_link(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    if lines:
        first_link = lines[0].strip()
        # Write the remaining links back to the file, skipping the first link
        with open(file_path, 'w') as file:
            file.writelines(lines[1:])
        return first_link
    return None

# Function to paste link and press enter
def paste_and_enter(link):
    pyperclip.copy(link)  # Copy link to clipboard
    pyautogui.hotkey('ctrl', 'v')  # Paste the link
    pyautogui.press('enter')  # Press Enter

# Path to the chegg_links.txt file
file_path = 'chegg_links.txt'

while True:
    # Read the first link and remove it from the file
    link = read_and_remove_first_link(file_path)
    if link is None:
        print("All links processed or file is empty.")
        break  # Exit loop if no more links

    print(f'Processing link: {link}')
    paste_and_enter(link)  # Paste and enter the link
    time.sleep(3)  # Wait for 5 seconds

print("All links processed.")
