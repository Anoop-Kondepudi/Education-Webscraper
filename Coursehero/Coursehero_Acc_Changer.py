import discord
import requests
import json
import os
from dotenv import load_dotenv

# Discord Bot Token and GitHub Info
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GIST_ID = os.getenv('GIST_ID')

# Proxy settings
proxies = {
    'http': 'http://wr37kDWXUGoa:USMuWej9iXz8@209.142.123.110:8080',
    'https': 'http://wr37kDWXUGoa:USMuWej9iXz8@209.142.123.110:8080'
}

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enables message content intent

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith('!login'):
        # Parse the username and password from the command
        _, credentials = message.content.split(' ', 1)
        username, password = credentials.split(':')
        
        # Prepare the new JSON content for the Gist
        new_content = {
            "email": username,
            "password": password
        }
        
        # Update the Gist using GitHub API
        response = requests.patch(
            f'https://api.github.com/gists/{GIST_ID}',
            headers={'Authorization': f'token {GITHUB_TOKEN}'},
            json={
                "files": {
                    "gistfile1.txt": {
                        "content": json.dumps(new_content)
                    }
                }
            },
            proxies=proxies  # Pass proxy settings
        )
        
        if response.status_code == 200:
            await message.channel.send("Gist updated successfully!")
        else:
            await message.channel.send("Failed to update Gist.")
        
client.run(DISCORD_TOKEN)