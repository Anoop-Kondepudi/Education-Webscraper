import discord
import requests
import json

# Discord Bot Token and GitHub Info
DISCORD_TOKEN = 'MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s'
GITHUB_TOKEN = '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'
GIST_ID = 'b9c4c7058c68c7a16bd25fc2b17be768'  # The ID of the Gist you want to update

# Proxy settings
proxies = {
    "http": "http://wr37kDWXUGoa:USMuWej9iXz8@121.91.240.183:8080",
    "https": "http://wr37kDWXUGoa:USMuWej9iXz8@121.91.240.183:8080"
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