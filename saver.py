import discord
from discord.ext import commands
import requests
import os
import re
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True

class ProfessorScraperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.author.id == 1194375738929991680:  # Professor bot ID
            if message.embeds:  # Check if the message contains an embed
                embed = message.embeds[0]  # Get the first embed
                if embed.title and "Success" in embed.title:
                    print(f"Embed Title: {embed.title}")
                    print(f"Embed Description: {embed.description}")
                    print(f"Embed Fields: {embed.fields}")
                    await self.process_professor_message(embed, message)

    async def process_professor_message(self, embed, message):
        # Extract the Chegg question ID from the embed description
        chegg_url_match = re.search(r'https:\/\/www\.chegg\.com\/homework-help\/questions-and-answers\/[a-zA-Z0-9_-]+-q([0-9]+)', embed.description)
        if chegg_url_match:
            chegg_question_id = chegg_url_match.group(1)
            file_name = f"q{chegg_question_id}.html"
            file_path = os.path.join("E:\\egg", file_name)

            # Extract the StudyHelp.io URL
            studyhelp_match = re.search(r'https:\/\/solution\.studyhelp\.io\/chegg\/[a-zA-Z0-9_-]+', embed.description)
            if studyhelp_match:
                answer_url = studyhelp_match.group(0)
                print(f"Attempting to scrape URL: {answer_url}")
                response = requests.get(answer_url)

                # Debug: Check the status code and content
                print(f"Response Status Code: {response.status_code}")
                if response.status_code == 200:
                    print(f"Response Content (first 200 characters): {response.text[:200]}")

                    # Format HTML - Remove specific <h1> element with "© Professor Premium"
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for header in soup.find_all('h1', class_='Container-header'):
                        if "© Professor Premium" in header.text:
                            header.decompose()  # Remove the element

                    # Save the formatted HTML
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(str(soup))

                    # Uncomment the following line to re-add the success emoji
                    # await message.add_reaction('✅')
                else:
                    print(f"Failed to scrape the URL. Status Code: {response.status_code}")

                    # Send failure message to the private channel
                    debug_channel = self.get_channel(1240006256278638662)
                    await debug_channel.send(f"Failed to scrape URL: {answer_url}")
                    await debug_channel.send(f"Status Code: {response.status_code}")
                    # Uncomment the following line to re-add the failure emoji
                    # await message.add_reaction('❌')
        else:
            print("Chegg question ID not found.")
            # Uncomment the following line to re-add the failure emoji
            # await message.add_reaction('❌')

bot = ProfessorScraperBot()
bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')
