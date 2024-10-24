import discord
from discord.ext import commands
import requests
import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

class ScraperSaverBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # Updated list of bot IDs and channel IDs to check
        supported_bot_ids = [1194375738929991680, 1283659292469362711, 1286396342373056533, 1141799262485745695, 1288114837993553920]
        supported_channels = [1287858800526884875, 1286395936452382841, 1260426776551624774, 1288340990167486464, 1285302064087302234]

        if message.author.id in supported_bot_ids and message.channel.id in supported_channels:
            # Check for messages from bot 1288114837993553920 containing an embed
            if message.author.id == 1288114837993553920:
                if message.embeds:  # Check if the message contains an embed
                    embed = message.embeds[0]  # Get the first embed
                    if embed.description and "Click here to view your answer" in embed.description:
                        print(f"Embed Description: {embed.description}")
                        await self.process_new_bot_embed(embed, message)
            # Check for messages from other supported bots with attachments or buttons
            elif message.author.id in supported_bot_ids:
                if message.attachments:
                    await self.process_html_attachment(message)
                elif message.components:  # Check if the message contains buttons
                    button = message.components[0].children[0]  # Get the first button
                    if button.label == "View Answer":  # Ensure it's the correct button
                        print("Found 'View Answer' button, processing...")
                        await self.process_button_url(button.url)

    async def process_new_bot_embed(self, embed, message):
        # Updated regex to capture the entire URL including query parameters
        link_match = re.search(r'https:\/\/cdn\.discordapp\.com\/attachments\/[a-zA-Z0-9\/_-]+\.html\?[^ ]*', embed.description)
        if link_match:
            download_link = link_match.group(0)
            print(f"Found download link: {download_link}")
            await self.download_and_process_html(download_link)
        else:
            print("No download link found in the embed description.")

    async def process_button_url(self, url):
        # Handle any external URL now, like the website provided
        print(f"Processing URL: {url}")
        await self.download_and_process_html(url)

    async def download_and_process_html(self, download_link):
        # Download the HTML file from the external site or Discord
        response = requests.get(download_link)
        if response.status_code == 200:
            temp_path = os.path.join("E:\\egg", "downloaded.html")
            with open(temp_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded HTML file to {temp_path}")

            # Process the downloaded HTML file
            await self.process_html_file(temp_path)
        else:
            print(f"Failed to download the HTML file. Status Code: {response.status_code}")

    async def process_html_file(self, temp_path):
        try:
            # Process the downloaded HTML file
            with open(temp_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # Ensure the title is set to "Study Solutions"
            title_tag = soup.find('title')
            if title_tag:
                title_tag.string = "Study Solutions"
            else:
                # Create a new <title> tag if it doesn't exist
                new_title_tag = soup.new_tag('title')
                new_title_tag.string = "Study Solutions"
                soup.head.append(new_title_tag)

            # Extract the Chegg question URL
            chegg_url_element = soup.find('a', href=re.compile(r'https:\/\/www\.chegg\.com\/homework-help\/questions-and-answers\/'))
            if chegg_url_element:
                chegg_url = chegg_url_element['href']
                chegg_question_id = re.search(r'q(\d+)', chegg_url).group(0)
                print(f"Extracted Chegg URL: {chegg_url}")
                print(f"Chegg Question ID: {chegg_question_id}")

                # Save the processed HTML with the Chegg question ID as filename
                file_name = f"{chegg_question_id}.html"
                file_path = os.path.join("E:\\egg", file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(str(soup))
                print(f"Saved processed HTML file as {file_name}")
            else:
                # Save the HTML as is if no Chegg link is found
                file_name = "processed_external.html"
                file_path = os.path.join("E:\\egg", file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(str(soup))
                print(f"Saved processed HTML file as {file_name}")
        finally:
            # Always remove the temporary file after processing
            os.remove(temp_path)

    async def process_html_attachment(self, message):
        # Process HTML attachments for other bots
        html_attachment = None
        for attachment in message.attachments:
            if attachment.filename.endswith('.html'):
                html_attachment = attachment
                break

        if html_attachment:
            # Save the HTML file temporarily
            temp_path = os.path.join("E:\\egg", "temp.html")
            await html_attachment.save(temp_path)
            print(f"Saved temporary HTML file to {temp_path}")

            # Open the saved HTML and parse to extract Chegg question ID
            chegg_question_id = None
            with open(temp_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # Updated selector based on the provided structure
            target_element = soup.select_one('div.container > div > a')
            if target_element:
                url = target_element.get('href')
                print(f"Found URL: {url}")

                # Extract the question ID by iterating from the end of the URL
                chegg_question_id = ""
                for i in range(len(url) - 1, -1, -1):
                    if url[i].isdigit():
                        chegg_question_id = url[i] + chegg_question_id
                    elif url[i] == 'q':
                        chegg_question_id = 'q' + chegg_question_id
                        break
                
                if chegg_question_id.startswith('q'):
                    print(f"Extracted Chegg Question ID: {chegg_question_id}")
                else:
                    print("Chegg question ID not found correctly in the provided URL.")
            else:
                print("Target element with the given selector not found in the HTML content.")

            # Set the final file path with the extracted question ID
            file_name = f"{chegg_question_id}.html" if chegg_question_id else html_attachment.filename
            file_path = os.path.join("E:\\egg", file_name)

            # Ensure the title is set to "Study Solutions"
            title_tag = soup.find('title')
            if title_tag:
                title_tag.string = "Study Solutions"
            else:
                # Create a new <title> tag if it doesn't exist
                new_title_tag = soup.new_tag('title')
                new_title_tag.string = "Study Solutions"
                soup.head.append(new_title_tag)

            # Save the modified HTML with the correct filename
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            print(f"Updated and saved HTML file as {file_name}")

            # Remove the temporary file
            os.remove(temp_path)

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the .env file
token = os.getenv('DISCORD_TOKEN')

# Initialize the bot
bot = ScraperSaverBot()

# Run the bot using the token from the .env file
bot.run(token)