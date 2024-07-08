import os
import asyncio
import glob
import re
import discord
from pynput.keyboard import Key, Controller
from PIL import Image
import webbrowser
import pyautogui
import time
import boto3
import secrets
import botocore.exceptions

keyboard = Controller()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
queue = asyncio.Queue()
running = False

# Define the paths to the images of the download buttons and GoFullPage button
download_button_path = "Define_Your_Path"
tripledot_redownload_button_path = "Define_Your_Path"
download_redownload_button_path = "Define_Your_Path"
go_full_page_button_path = "Define_Your_Path"

# Log when bot has come online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await process_queue()

# Define the custom emojis
loading_emoji = 'Add_Your_Emoji'
check_emoji = 'Add_Your_Emoji'
uncheck_emoji = 'Add_Your_Emoji'

# Process message with Brainly or CourseHero links
async def process_message(message):
    if message.author == client.user:
        return
    
    brainly_channel_id = Your_Channel_ID
    coursehero_channel_id = Your_Channel_ID
    general_channel_id = Your_Channel_ID

    # Process Brainly and CourseHero links based on the channel
    brainly_url_list = re.findall(r'brainly\.com/question/\d+', message.content) if message.channel.id in [brainly_channel_id, general_channel_id] else []
    coursehero_url_list = re.findall(r'(?:https?:://)?(?:www\.)?coursehero\.com/(?:file|[\w\d]+)/\S+', message.content) if message.channel.id in [coursehero_channel_id, general_channel_id] else []

    url_list = brainly_url_list + coursehero_url_list
    if len(url_list) > 0:
        await message.add_reaction(loading_emoji)
        # Put (message.author, message, url_list) tuple into the queue
        await queue.put((message.author, message, url_list))

# Capture screenshot of the webpage
def capture_screenshot():
    try:
        # Locate the "GoFullPage" button image and click on it with 100% confidence
        if click_button(go_full_page_button_path, "GoFullPage Button", confidence=0.9):
            print("Screenshot captured successfully.")
            time.sleep(12)
        else:
            print("Failed to capture screenshot. GoFullPage button not found.")
    except Exception as e:
        print(f"An error occurred while trying to capture screenshot: {e}")

# Convert screenshot to PDF
def convert_to_pdf(image_path, pdf_path):
    with Image.open(image_path) as img:
        img.save(pdf_path, "PDF", resolution=100.0)

# Close the current browser tab
def close_tab():
    with keyboard.pressed(Key.ctrl):
        keyboard.press('w')
        keyboard.release('w')

# Function to open the CourseHero webpage and wait for it to load
async def open_coursehero_page(url):
    webbrowser.open(url)
    await asyncio.sleep(12)  # Adjust the sleep time as necessary to allow the page to load

# Function to locate the image and click on it
def click_button(image_path, description, is_coursehero=False, delay_after_click=0, confidence=None):
    try:
        # Define the region based on whether the operation is for CourseHero or Brainly
        region = (0, 87, 1024, 725) if is_coursehero else None

        button_location = None
        for i in range(20):  # Try locating the button for up to 30 seconds
            button_location = pyautogui.locateCenterOnScreen(image_path, region=region, confidence=confidence)
            if button_location is not None:
                break
            time.sleep(1.5)

        if button_location is not None:
            pyautogui.moveTo(button_location)
            pyautogui.click()
            print(f"{description} button clicked.")
            if delay_after_click > 0:
                time.sleep(delay_after_click)
            return True
        else:
            print(f"{description} button not found on the screen.")
            return False
    except Exception as e:
        print(f"An error occurred while trying to click the {description} button: {e}")
        return False

async def wait_for_downloaded_file(download_folder):
    # Wait for a short period before checking for downloaded files
    await asyncio.sleep(5)
    # Check for the downloaded file in the specified folder
    for i in range(20):  # Wait for the download to complete
        downloaded_files = glob.glob(os.path.join(download_folder, "*"))
        # Filter out unwanted files, such as directories
        downloaded_files = [file for file in downloaded_files if os.path.isfile(file)]
        if downloaded_files:
            downloaded_file = max(downloaded_files, key=os.path.getmtime)
            return downloaded_file
        await asyncio.sleep(1.5)
    
    # If no file is found, return None
    return None

# Main function to handle the CourseHero download process
async def handle_coursehero_download(url, download_button_path, tripledot_redownload_button_path, download_redownload_button_path):
    await open_coursehero_page(url)

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    # Try clicking the download button directly with 80% confidence
    if click_button(download_button_path, "Download", confidence=0.8):
        # Download successful, wait for the downloaded file
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(2)  # Add a short delay after download
            pyautogui.click(960, 650) # Click the mouse at the specific location (960, 650).
            print("Clicked Mouse at (960,650)")
            return downloaded_file

    # If the download button is not available, try the redownload process with 80% confidence
    if click_button(tripledot_redownload_button_path, "Redownload", delay_after_click=2, confidence=0.8):
        click_button(download_redownload_button_path, "Confirm Redownload", delay_after_click=2, confidence=0.8)
        # Download successful, wait for the downloaded file
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(3.5)  # Add a short delay after download
            pyautogui.click(960, 650) # Click the mouse at the specific location (960, 650).
            print("Clicked Mouse at (960,650)")
            return downloaded_file

    # If both sequences fail or the file cannot be uploaded, return None
    return None

# Function to generate a unique token
def generate_unique_token(existing_tokens):
    while True:
        gen_token = secrets.token_hex(16)
        if gen_token not in existing_tokens:
            return gen_token

# Function to upload file to S3
def upload_to_s3(file_path, bucket_name='studysolutions'):
    s3 = boto3.client(
        's3',
        region_name='us-east-2',
        aws_access_key_id='AKIAZQ3DR6XOHHTMTHIE',
        aws_secret_access_key='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',
        config=boto3.session.Config(signature_version='s3v4'))

    # Generate a unique key for the file to avoid name collisions
    existing_tokens = set()  # Ensure you keep track of generated tokens if needed
    unique_token = generate_unique_token(existing_tokens)
    s3_key = f'{unique_token}.pdf'

    s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={'ContentType': 'application/pdf'})

    # Generate a presigned URL for the uploaded file
    link = s3.generate_presigned_url('get_object',
                                     Params={'Bucket': bucket_name, 'Key': s3_key},
                                     ExpiresIn=3600)  # Link valid for 1 hour
    
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={'ContentType': 'application/pdf'})
            link = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': s3_key}, ExpiresIn=3600)
            return link
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'RequestTimeTooSkewed' and retries < max_retries:
                retries += 1
                wait_time = 2 ** retries
                print(f"Retry {retries} in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    else:
        raise Exception("Max retries exceeded. Unable to upload to S3.")

    
    return link

    

# Process the queue of Brainly or CourseHero links
async def process_queue():
    global running
    while True:
        author, message, url_list = await queue.get()
        if not running:
            running = True
            print(f'Processing links: {url_list}')
            for url in url_list:
                try:
                    if 'coursehero.com' in url:
                        # Handle CourseHero download process
                        downloaded_file = await handle_coursehero_download(
                            f'https://{url}',
                            download_button_path,
                            tripledot_redownload_button_path,
                            download_redownload_button_path
                        )
                        if not downloaded_file:
                            await message.channel.send("Failed to download the CourseHero document.")
                            await message.remove_reaction(loading_emoji, client.user)
                            await message.add_reaction(uncheck_emoji)
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        question_link = f"CourseHero document"
                        await message.channel.send(f"{user_mention}, here is your {question_link}:", file=discord.File(downloaded_file))

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'brainly.com' in url:
                        # Open the webpage
                        full_url = f'https://{url}'
                        webbrowser.open(full_url)
                        await asyncio.sleep(12)  # Wait for the webpage to load

                        # Capture screenshot
                        capture_screenshot()

                        # Check for the captured screenshot
                        path = "C:\\Users\\MCBat\\Downloads\\CheggBotScreenshot\\*.jpg"
                        for i in range(20):
                            print(f"Checking files {i+1}")
                            files = glob.glob(path, recursive=True)
                            if len(files) > 0:
                                file_loc = max(files, key=os.path.getmtime)
                                break
                            await asyncio.sleep(1.5)
                        else:
                            print("Failed to find the image. Try checking the path.")
                            await message.channel.send("Failed to retrieve image.")
                            await message.remove_reaction(loading_emoji, client.user)
                            await message.add_reaction(uncheck_emoji)
                            running = False
                            break

                        # Move the mouse to the specific location (960, 650) and click.
                        pyautogui.click(960, 650)

                        # Convert screenshot to PDF
                        pdf_path = 'output.pdf'
                        convert_to_pdf(file_loc, pdf_path)

                        # Determine the type of question
                        question_type = 'Brainly'

                        # Upload the PDF to S3 and get the URL
                        pdf_url = upload_to_s3(pdf_path)

                        # Send the PDF with user mention and hyperlink
                        user_mention = f"<@{author.id}>"
                        question_link = f"{question_type} question"
                        await message.channel.send(
                            f"{user_mention}, here is your answer to the {question_link}:\n\n# Click [here]({pdf_url}) to view the PDF online.",
                            file=discord.File(pdf_path)
                        )

                        # Remove the screenshot and PDF
                        os.remove(file_loc)
                        os.remove(pdf_path)

                except Exception as e:
                    print(f"An error occurred: {e}")
                    await message.channel.send("An error occurred while processing your request.")
                    await message.remove_reaction(loading_emoji, client.user)
                    await message.add_reaction(uncheck_emoji)
                finally:
                    # Close the current browser tab
                    close_tab()

                    # Remove loading emoji and add check emoji
                    await message.remove_reaction(loading_emoji, client.user)
                    await message.add_reaction(check_emoji)

            else:
                await message.channel.send("All links processed successfully.")
            running = False

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return  # Ignore messages from DMs
    await process_message(message)

# Run the bot
with open('SSkey.txt') as f:
    key = f.read().strip()
#print(f"Using token: {key}")  # Debugging output
client.run(key)
