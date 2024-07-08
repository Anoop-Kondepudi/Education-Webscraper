# Education-Webscraper

# Coursehero + Brainly (How It Works)
Here's a summary of what the code does, broken down into sections as you requested:

### Libraries / Dependencies:
- *os*: Interacts with the operating system.
- *asyncio*: Provides support for asynchronous programming.
- *glob*: Finds all pathnames matching a specified pattern.
- *re*: Handles regular expressions.
- *discord*: Interacts with Discord API.
- *pynput.keyboard*: Controls and monitors keyboard events.
- *PIL (Pillow)*: Handles image processing.
- *webbrowser*: Opens URLs in a web browser.
- *pyautogui*: Provides GUI automation.
- *time*: Handles time-related functions.
- *boto3*: Interacts with Amazon Web Services (AWS) S3.
- *secrets*: Generates secure random numbers.
- *botocore.exceptions*: Handles exceptions from AWS services.

### Bot Initialization:
- Creates a Discord bot client with specific intents.
- Initializes a queue to handle incoming messages.

### File Paths:
- Defines paths to images used for identifying download buttons and the GoFullPage button.

### Event Handlers:
- **on_ready**: Logs when the bot is online and starts processing the queue.
- **on_message**: Processes incoming messages from Discord channels (ignores direct messages).

### Emoji Definitions:
- Defines custom emojis for loading, check, and uncheck statuses.

### Message Processing:
- **process_message**: Identifies Brainly and CourseHero links in messages and adds them to the queue.

### Screenshot and PDF Functions:
- **capture_screenshot**: Captures a screenshot using the GoFullPage extension.
- **convert_to_pdf**: Converts an image to a PDF file.

### Browser Automation:
- **close_tab**: Closes the current browser tab using keyboard shortcuts.
- **open_coursehero_page**: Opens a CourseHero URL and waits for the page to load.

### GUI Automation:
- **click_button**: Finds and clicks a button on the screen based on an image.
- **wait_for_downloaded_file**: Waits for a file to download in a specified folder.

### CourseHero Download Handling:
- **handle_coursehero_download**: Manages the download process for CourseHero documents, including fallback mechanisms if the first attempt fails.

### Token Generation and S3 Upload:
- **generate_unique_token**: Generates a unique token to avoid name collisions.
- **upload_to_s3**: Uploads a file to AWS S3 and generates a presigned URL for it.

### Queue Processing:
- **process_queue**: Processes the queue of messages, handles the download and screenshot capture, uploads files to S3, and sends the links back to Discord.

### Running the Bot:
- Reads the bot token from a file and starts the Discord client.

The bot automates downloading documents from CourseHero and capturing screenshots from Brainly, then converts them to PDFs, uploads them to AWS S3, and returns the PDF links on Discord.
