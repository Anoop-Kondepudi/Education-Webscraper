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
import mimetypes
import subprocess

keyboard = Controller()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
queue = asyncio.Queue()
running = False

# Define the paths to the images of the download buttons and GoFullPage button
download_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/download.png"
tripledot_redownload_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/tripledot_redownload.png"
download_redownload_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/download_redownload.png"
go_full_page_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/GoFullPage.png"
tutor_unlock_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/Tutor_Unlock.png"
html_download_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/HTML_Download.png"
chegg_unlock_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/Chegg_Unlock.png"
log_in_button_coords = (880, 190)
welcome_back_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/welcome_back.png"
log_in_blue_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/log_in_blue.png"
password_cracked_ok_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/password_cracked_ok.png"
download_button_region = (791, 410, 229, 173)

# Log when bot has come online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    try:
        await process_queue()
    except Exception as e:
        print(f"An error occurred in process_queue: {e}")

# Define the custom emojis
loading_emoji = '<:Loading2:1240447269313183785>'
check_emoji = '<:Check:1240449377806319616>'
uncheck_emoji = '<:Uncheck:1240449376703484004>'

# Process message with Brainly or CourseHero links
async def process_message(message):
    if message.author == client.user:
        return
    
    #Study Solutions:
    brainly_channel_id = 1241857920224858163
    coursehero_channel_id = 1287500278345764865
    all_channel_id = 1245866164815659123
    chegg_channel_id = 1262531507436785825
    testing_priv_channel_id = 1240006256278638662
    studycom_channel_id_ss = 1278490959075610775

    #School Essentials (soon)
    brainly_channel_id_schoolaro = 1235648614118719569
    brainly_channel_id_se = 1262628998949634058
    coursehero_channel_id_se = 1262628709723013181
    quizlet_channel_id_se = 1285437540374941726
    studycom_channel_id_se = 1285437552416915509
    #se = Study Essentials

    #Homework Unlocker
    coursehero_channel_id_homeworkunlocker = 1260659627654123612
    brainly_channel_id_homeworkunlocker = 1266234146934493296

    #Homework Help (EVIL)
    coursehero_channel_id_homeworkhelp = 1259682197221408888
    brainly_channel_id_homeworkhelp = 1262252612590239834
    chegg_channel_id_homeworkhelp = 1263324400674148393
    studycom_channel_id_homeworkhelp = 1278490605886111816

    quizlet_channel_id_homeworkhelp = 1273812941099237546
    quizlet_channel_id_ss = 1273680069423796347
    quizlet_channel_id_homeworkunlocker = 1278461429833400330

    #Kita Study
    coursehero_channel_id_ks = 1274056906574401537

    # Process Brainly and CourseHero links based on the channel
    #Brainly Channel ID List: brainly_channel_id, all_channel_id, brainly_channel_id_homeworkhelp, brainly_channel_id_schoolaro
    brainly_url_list = re.findall(r'brainly\.com/question/\d+', message.content) if message.channel.id in [brainly_channel_id, all_channel_id, brainly_channel_id_homeworkhelp, brainly_channel_id_schoolaro, brainly_channel_id_se, brainly_channel_id_homeworkunlocker] else []
    coursehero_url_list = re.findall(r'(?:https?:://)?(?:www\.)?coursehero\.com/(?:file|[\w\d]+)/\S+', message.content) if message.channel.id in [coursehero_channel_id, all_channel_id, coursehero_channel_id_se, testing_priv_channel_id, coursehero_channel_id_homeworkunlocker] else []
    tutor_url_list = re.findall(r'(?:https?:://)?(?:www\.)?coursehero\.com/(?:tutors-problems|student-questions)/\S+', message.content) if message.channel.id in [coursehero_channel_id, all_channel_id, coursehero_channel_id_se, testing_priv_channel_id, coursehero_channel_id_homeworkunlocker] else []
    chegg_url_list = re.findall(r'(?:https?://)?(?:www\.)?chegg\.com/(?:homework-help|study-guide)/\S+', message.content) if message.channel.id in [1240006256278638662] else []
    textbook_solutions_url_list = re.findall(r'(?:https?:://)?(?:www\.)?coursehero\.com/textbook-solutions/\S+', message.content) if message.channel.id in [coursehero_channel_id, all_channel_id, coursehero_channel_id_homeworkhelp, coursehero_channel_id_se, coursehero_channel_id_homeworkunlocker, testing_priv_channel_id] else []
    quizlet_question_url_list = re.findall(r'quizlet\.com/explanations/questions/\S+', message.content) if message.channel.id in [quizlet_channel_id_homeworkhelp, quizlet_channel_id_ss, quizlet_channel_id_homeworkunlocker, quizlet_channel_id_se, testing_priv_channel_id] else []
    quizlet_textbook_solutions_url_list = re.findall(r'quizlet\.com/explanations/textbook-solutions/\S+', message.content) if message.channel.id in [quizlet_channel_id_homeworkhelp, quizlet_channel_id_ss, quizlet_channel_id_homeworkunlocker, quizlet_channel_id_se, testing_priv_channel_id] else []
    study_url_list = re.findall(r'(homework\.study\.com/explanation/\S+|study\.com/academy/lesson/\S+)', message.content) if message.channel.id in [studycom_channel_id_homeworkhelp, studycom_channel_id_ss, studycom_channel_id_se, testing_priv_channel_id] else []

    #url_list = brainly_url_list + coursehero_url_list + tutor_url_list + textbook_solutions_url_list + chegg_url_list + quizlet_question_url_list + quizlet_textbook_solutions_url_list
    url_list = brainly_url_list + chegg_url_list + quizlet_question_url_list + quizlet_textbook_solutions_url_list + study_url_list + coursehero_url_list + tutor_url_list
    if len(url_list) > 0:
        try:
            await message.add_reaction(loading_emoji)
        except discord.errors.NotFound:
            print("Message not found when trying to add loading emoji.")

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

async def open_url_non_blocking(url):
    subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe', url])
    await asyncio.sleep(12)  # Adjust based on page load time

# Function to perform the login process
async def perform_login():
    try:
        # Click the login button at specified coordinates
        #pyautogui.click(log_in_button_coords)
        await asyncio.sleep(10)  # Wait for 10 seconds

        # Check if the welcome back image is present
        if pyautogui.locateOnScreen(welcome_back_path, confidence=0.8):
            print("Welcome back detected, proceeding with login...")
            
            # Scroll down
            keyboard.press(Key.page_down)
            keyboard.release(Key.page_down)
            await asyncio.sleep(10)

            # Click the blue login button
            if pyautogui.locateOnScreen(log_in_blue_button_path, confidence=0.8):
                pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(log_in_blue_button_path, confidence=0.8)))
                await asyncio.sleep(10)  # Wait for 10 seconds after clicking log in
                
                # Click the password cracked OK button
                if pyautogui.locateOnScreen(password_cracked_ok_path, confidence=0.8):
                    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(password_cracked_ok_path, confidence=0.8)))
                    await asyncio.sleep(5)
                    print("Clicked Password Cracked OK button.")
                else:
                    print("Password Cracked OK button not found.")
                
                print("Logged in successfully.")
                
            else:
                print("Blue login button not found.")
        else:
            print("Welcome back screen not detected, canceling login process.")
        
    except Exception as e:
        print(f"An error occurred during login: {e}")

async def perform_logout():
    try:
        # Navigate to the dashboard URL
        logout_url = "https://www.coursehero.com/dashboard/"
        webbrowser.open(logout_url)
        await asyncio.sleep(20)  # Wait 20 seconds for the page to load

        # Click at LOCATION_1 (x=968, y=106)
        LOCATION_1 = (968, 106)
        pyautogui.click(LOCATION_1)
        await asyncio.sleep(3)  # Wait 3 seconds after the first click

        # Click at LOCATION_2 (x=737, y=349)
        LOCATION_2 = (737, 349)
        pyautogui.click(LOCATION_2)

        print("Logged out successfully.")
        await asyncio.sleep(30)
        close_tab()
    except Exception as e:
        print(f"An error occurred during logout: {e}")

async def handle_study_com_download(url):
    await open_study_com_page(url)

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    await asyncio.sleep(20)  # Wait for 20 seconds after opening the URL

    # Click the HTML Download button with 90% confidence
    if click_button(html_download_button_path, "Study_HTML_Download", delay_after_click=2, confidence=0.9):
        # Download successful, wait for the downloaded file
        await asyncio.sleep(12)
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(6)  # Add a short delay after download
            pyautogui.click(960, 640)  # Click the mouse at the specific location (960, 640).
            print("Clicked Mouse at (960,640)")
            #close_tab()
            return downloaded_file
    else:
        # If download fails, return None
        return None

async def open_study_com_page(url):
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    await open_url_non_blocking(url)
    await asyncio.sleep(7)  # Wait for 20 seconds to ensure the page is fully loaded

#Add new function for handling textbook solutions
async def handle_coursehero_textbook_solution(url):
    await open_coursehero_page(url)

    # Wait for 30 seconds to ensure page is loaded
    await asyncio.sleep(30)

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    # Click HTML Download button with 90% confidence
    if click_button(html_download_button_path, "HTML_Download", delay_after_click=2, confidence=0.9):
        # Download successful, wait for the downloaded file
        await asyncio.sleep(12)
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(6)  # Add a short delay after download
            pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650).
            print("Clicked Mouse at (960,650)")
            return downloaded_file

    # If download fails, return None
    return None

async def handle_coursehero_tutor_question(url):
    await open_coursehero_page(url)

    # Perform login if necessary
    await perform_login()  # Ensure to await the coroutine

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
    await asyncio.sleep(1)

    # Try clicking the Tutor_Unlock image first
    if click_button(tutor_unlock_button_path, "Tutor_Unlock", confidence=0.8):
        # Click HTML Download button with 90% confidence
        asyncio.wait(0.5)
        pyautogui.click(1)
        await asyncio.sleep(30)
        if click_button(html_download_button_path, "HTML_Download", delay_after_click=2, confidence=0.9):
            # Download successful, wait for the downloaded file
            await asyncio.sleep(12)
            downloaded_file = await wait_for_downloaded_file(download_folder)
            if downloaded_file:
                await asyncio.sleep(6)  # Add a short delay after download
                pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
                print("Clicked Mouse at (960,650)")
                return downloaded_file
    elif click_button(html_download_button_path, "HTML_Download", delay_after_click=2, confidence=0.9):
            # Download successful, wait for the downloaded file
            await asyncio.sleep(12)
            downloaded_file = await wait_for_downloaded_file(download_folder)
            if downloaded_file:
                await asyncio.sleep(6)  # Add a short delay after download
                pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
                print("Clicked Mouse at (960,650)")
                return downloaded_file

    # If both sequences fail or the file cannot be downloaded, return None
    return None

# Function to open the Quizlet webpage and wait for it to load
async def open_quizlet_page(url):
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    await open_url_non_blocking(url)
    await asyncio.sleep(7)  # Wait for 20 seconds to ensure the page is fully loaded

# Function to handle Quizlet download process
async def handle_quizlet_download(url):
    await open_quizlet_page(url)

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    await asyncio.sleep(3)  # Wait for 20 seconds after opening the URL

    # Click the HTML Download button with 90% confidence
    if click_button(html_download_button_path, "Quizlet_HTML_Download", delay_after_click=2, confidence=0.9):
        # Download successful, wait for the downloaded file
        await asyncio.sleep(12)
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(6)  # Add a short delay after download
            pyautogui.click(960, 640)  # Click the mouse at the specific location (960, 640).
            print("Clicked Mouse at (960,640)")
            #close_tab()
            return downloaded_file
    else:
        # If download fails, return None
        return None

# Define the path to the Chegg unlock button image
chegg_unlock_button_path = "C:/Users/MCBat/OneDrive/Desktop/cheggbot/Chegg_Unlock.png"

# Function to handle Chegg download process
async def handle_chegg_download(url):
    await open_chegg_page(url)
    
    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"
    
    await asyncio.sleep(12)  # Wait for 12 seconds after opening the URL

    # Click the unlock button with 90% confidence
    if click_button(chegg_unlock_button_path, "Chegg_Unlock", confidence=0.9):
        await asyncio.sleep(30)  # Wait for 30 seconds after clicking the unlock button

        # Click the HTML Download button with 90% confidence
        if click_button(html_download_button_path, "HTML_Download", delay_after_click=2, confidence=0.9):
            # Download successful, wait for the downloaded file
            await asyncio.sleep(12)
            downloaded_file = await wait_for_downloaded_file(download_folder)
            if downloaded_file:
                await asyncio.sleep(6)  # Add a short delay after download
                pyautogui.click(960, 640)  # Click the mouse at the specific location (960, 640).
                print("Clicked Mouse at (960,640)")
                close_tab()
                return downloaded_file
    elif click_button(html_download_button_path, "HTML_Download", delay_after_click=2, confidence=0.9):
            # Download successful, wait for the downloaded file
            await asyncio.sleep(12)
            downloaded_file = await wait_for_downloaded_file(download_folder)
            if downloaded_file:
                await asyncio.sleep(6)  # Add a short delay after download
                pyautogui.click(960, 650) # Click the mouse at the specific location (960, 650).
                print("Clicked Mouse at (960,650)")
                return downloaded_file

    # If download fails, return None
    return None

# Function to handle Brainly HTML download process
async def handle_brainly_download(url):
    await open_brainly_page(url)
    
    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"
    
    # Click HTML Download button with 90% confidence
    if click_button(html_download_button_path, "Brainly_HTML_Download", delay_after_click=2, confidence=0.9):
        # Download successful, wait for the downloaded file
        await asyncio.sleep(12)
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(6)  # Add a short delay after download
            pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650).
            print("Clicked Mouse at (960,650)")
            return downloaded_file

    # If download fails, return None
    return None

# Function to open the Brainly webpage and wait for it to load
async def open_brainly_page(url):
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    await open_url_non_blocking(url)
    await asyncio.sleep(7)  # Adjust the sleep time as necessary to allow the page to load

# Function to open the Chegg webpage and wait for it to load
async def open_chegg_page(url):
    webbrowser.open(url)
    await asyncio.sleep(12)  # Adjust the sleep time as necessary to allow the page to load

# Function to open the CourseHero webpage and wait for it to load
async def open_coursehero_page(url):
    webbrowser.open(url)
    await asyncio.sleep(60)  # Adjust the sleep time as necessary to allow the page to load

# Updated click_button function with region support
def click_button(image_path, description, region=None, delay_after_click=0, confidence=0.8):
    try:
        button_location = None
        for i in range(20):  # Try locating the button for up to 30 seconds
            button_location = pyautogui.locateOnScreen(image_path, region=region, confidence=confidence)
            if button_location is not None:
                break
            time.sleep(1.5)

        if button_location is not None:
            button_center = pyautogui.center(button_location)
            pyautogui.moveTo(button_center)
            pyautogui.click()
            print(f"{description} button clicked.")
            if delay_after_click > 0:
                time.sleep(delay_after_click)
            return True
        else:
            print(f"{description} button not found{' in the specified region' if region else ''}.")
            return False
    except Exception as e:
        print(f"An error occurred while trying to click the {description} button: {e}")
        return False

async def wait_for_downloaded_file(download_folder):
    await asyncio.sleep(5)
    for i in range(20):  # Increased attempts
        downloaded_files = glob.glob(os.path.join(download_folder, "*"))
        downloaded_files = [file for file in downloaded_files if os.path.isfile(file)]
        if downloaded_files:
            downloaded_file = max(downloaded_files, key=os.path.getmtime)
            if not downloaded_file.endswith('.crdownload'):  # Ensure the file is fully downloaded
                return downloaded_file
        await asyncio.sleep(1.5)
    return None


# Main function to handle the CourseHero download process
async def handle_coursehero_download(url, download_button_path, tripledot_redownload_button_path, download_redownload_button_path):
    await open_coursehero_page(url)

    # Perform login if necessary
    await perform_login()

    # Ensure that the login process has enough time to complete
    await asyncio.sleep(5)  # Adjust as necessary for your system's speed

    # Define the download folder path
    download_folder = "C:\\Users\\MCBat\\Downloads"

    pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
    await asyncio.sleep(1)

    # Define the region where the download button is expected to be
    download_button_region = (791, 410, 229, 173)

    # Try clicking the download button directly within the specified region
    if click_button(download_button_path, "Download", region=download_button_region, confidence=0.9):
        # Download successful, wait for the downloaded file
        await asyncio.sleep(2)
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(2)  # Add a short delay after download
            pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
            print("Clicked Mouse at (960,650)")
            return downloaded_file

    # If the download button is not available, try the redownload process with 80% confidence
    # Replace asyncio.sleep(1.5) with await asyncio.sleep(1.5)
    if click_button(tripledot_redownload_button_path, "Redownload", confidence=0.8):
        await asyncio.sleep(1.5)  # Corrected line
        click_button(download_redownload_button_path, "Confirm Redownload", confidence=0.8)
        # Download successful, wait for the downloaded file
        downloaded_file = await wait_for_downloaded_file(download_folder)
        if downloaded_file:
            await asyncio.sleep(3.5)  # Add a short delay after download
            pyautogui.click(960, 650)  # Click the mouse at the specific location (960, 650)
            print("Clicked Mouse at (960,650)")
            return downloaded_file


    # If both sequences fail or the file cannot be downloaded, return None
    return None

# Function to upload file to S3
def upload_to_s3(file_path, bucket_name='studysolutions'):
    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-2',
            aws_access_key_id='AKIAZQ3DR6XOHHTMTHIE',
            aws_secret_access_key='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',
            config=boto3.session.Config(signature_version='s3v4')
        )

        # Generate a unique key for the file to avoid name collisions
        existing_tokens = set()  # Ensure you keep track of generated tokens if needed
        unique_token = generate_unique_token(existing_tokens)
        file_name = os.path.basename(file_path)
        s3_key = f'{unique_token}/{file_name}'

        # Determine ContentType based on file extension
        content_type, _ = mimetypes.guess_type(file_name)
        if content_type is None:
            if file_name.endswith('.html'):
                content_type = 'text/html'
            else:
                content_type = 'application/octet-stream'

        # Upload the file to S3 with ContentType
        s3.upload_file(file_path, bucket_name, s3_key, ExtraArgs={'ContentType': content_type})

        # Generate a presigned URL for the uploaded file valid for 1 hour
        link = s3.generate_presigned_url('get_object',
                                         Params={'Bucket': bucket_name, 'Key': s3_key},
                                         ExpiresIn=3600)

        return link

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'RequestTimeTooSkewed':
            raise Exception("RequestTimeTooSkewed: Adjust your system clock or retry later.")
        else:
            raise Exception(f"S3 Upload Error: {e}")

    except Exception as e:
        raise Exception(f"Error uploading file to S3: {e}")

def generate_unique_token(existing_tokens):
    while True:
        gen_token = secrets.token_hex(16)
        if gen_token not in existing_tokens:
            return gen_token
        
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
                    if 'coursehero.com/file' in url:
                        # Handle CourseHero download process
                        downloaded_file = await handle_coursehero_download(
                            f'https://{url}',
                            download_button_path,
                            tripledot_redownload_button_path,
                            download_redownload_button_path
                        )
                        if not downloaded_file:
                            await message.channel.send("Failed to download the CourseHero document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        question_link = f"CourseHero document"
                        await message.channel.send(f"{user_mention}, here is your {question_link}:", file=discord.File(downloaded_file))

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'tutors-problems' in url or 'student-questions' in url:
                        # Handle CourseHero Tutor question download process
                        downloaded_file = await handle_coursehero_tutor_question(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the CourseHero Tutor question document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the HTML file with user mention
                        user_mention = f"<@{author.id}>"
                        question_link = f"CourseHero Tutor Question Unlocked!"
                        with open(downloaded_file, 'rb') as f:
                            await message.channel.send(
                                f"{user_mention}, here is your {question_link}:",
                                file=discord.File(f, filename='CourseHero_Tutor_Question.html')
                            )

                        # Clean up: Remove downloaded file
                        os.remove(downloaded_file)

                    elif 'coursehero.com/textbook-solutions' in url:
                        # Handle CourseHero Textbook Solution download process
                        downloaded_file = await handle_coursehero_textbook_solution(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the CourseHero Textbook Solution document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded HTML file with user mention
                        user_mention = f"<@{author.id}>"
                        solution_link = f"CourseHero Textbook Solution"
                        with open(downloaded_file, 'rb') as f:
                            await message.channel.send(
                                f"{user_mention}, here is your {solution_link}:",
                                file=discord.File(f, filename='CourseHero_Textbook_Solution.html')
                            )

                        # Clean up: Remove downloaded file
                        os.remove(downloaded_file)

                    elif 'quizlet.com/explanations/questions' in url or 'quizlet.com/explanations/textbook-solutions' in url:
                        # Handle Quizlet download process
                        downloaded_file = await handle_quizlet_download(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the Quizlet document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        document_name = f"Quizlet document"
                        await message.channel.send(f"{user_mention}, here is your {document_name}:", file=discord.File(downloaded_file))

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'homework.study.com/explanation' in url:
                        # Handle Study.com download process
                        downloaded_file = await handle_study_com_download(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the Study.com document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        document_name = f"Study.com document"
                        await message.channel.send(f"{user_mention}, here is your {document_name}:", file=discord.File(downloaded_file))

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'study.com/academy/lesson' in url:
                        # Handle Study.com Academy Lesson download process
                        downloaded_file = await handle_study_com_download(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the Study.com lesson document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        document_name = f"Study.com Academy Lesson document"
                        await message.channel.send(f"{user_mention}, here is your {document_name}:", file=discord.File(downloaded_file))

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'chegg.com' in url:
                        # Handle Chegg download process
                        downloaded_file = await handle_chegg_download(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the Chegg document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded file
                        user_mention = f"<@{author.id}>"
                        document_name = f"Chegg document"
                        await message.channel.send(f"{user_mention}, here is your {document_name}:", file=discord.File(downloaded_file))
                        
                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                    elif 'brainly.com' in url:
                        # Handle Brainly download process
                        downloaded_file = await handle_brainly_download(url)
                        if not downloaded_file:
                            await message.channel.send("Failed to download the Brainly document.")
                            try:
                                await message.remove_reaction(loading_emoji, client.user)
                                await message.add_reaction(uncheck_emoji)
                            except discord.errors.NotFound:
                                print("Message not found when trying to add/remove reactions.")
                            continue

                        # Send the downloaded HTML file with user mention and hyperlink
                        user_mention = f"<@{author.id}>"
                        question_link = f"Brainly question"
                        with open(downloaded_file, 'rb') as f:
                            await message.channel.send(
                                f"{user_mention}, here is your {question_link}:",
                                file=discord.File(f, filename='Brainly_Question.html')
                            )

                        # Clean up by removing the downloaded file
                        os.remove(downloaded_file)

                except Exception as e:
                    print(f"An error occurred: {e}")
                    await message.channel.send("An error occurred while processing your request.")
                    try:
                        await message.remove_reaction(loading_emoji, client.user)
                        await message.add_reaction(uncheck_emoji)
                    except discord.errors.NotFound:
                        print("Message not found when trying to add/remove reactions.")
                    finally:
                        # Close the current browser tab
                        print("Close_Tab Should Be Here")

                # Move this part outside of the except block to ensure it always executes
                try:
                    await message.remove_reaction(loading_emoji, client.user)
                    await message.add_reaction(check_emoji)
                except discord.errors.NotFound:
                    print("Message not found when trying to add/remove reactions.")

            else:
                await message.channel.send("All links processed successfully.")
                close_tab()
            running = False

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return  # Ignore messages from DMs

    if message.content.lower() == "!logout":
        await message.channel.send("Logout process initiated. Please wait...")
        await perform_logout()
        await message.channel.send("Logout process completed.")

    await process_message(message)

# Run the bot
with open('C:/Users/MCBat/OneDrive/Desktop/Education-Webscraper/Education-Webscraper/Coursehero/SSkey.txt') as f:
    key = f.read().strip()
#print(f"Using token: {key}")  # Debugging output
client.run(key)
