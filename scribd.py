import discord
from discord.ext import commands
import re
import requests
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent explicitly

class ScribdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.allowed_channels = [1240006256278638662, 1238373226283929641, 1245866164815659123, 1262248765037871136]  # Update with your channel IDs

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Check if the message is in allowed channels
        if message.channel.id not in self.allowed_channels:
            return

        # Find Scribd URLs in the message content
        scribd_url_list = re.findall(r'https:\/\/(?:www\.|id\.|es\.)scribd\.com\/(document|doc|presentation)\/(\d+)\/', message.content)

        if len(scribd_url_list) > 0:
            # Add a checkmark emoji reaction to indicate processing
            await message.add_reaction('✅')

            for type_, doc_id in scribd_url_list:
                embed_link = f'https://www.scribd.com/embeds/{doc_id}/content'
                response = requests.get(embed_link)
                html_content = response.text
                
                file_path = f"{doc_id}.html"
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                
                # Send the HTML file to the channel
                sent_file = await message.channel.send(file=discord.File(file_path))
                download_url = sent_file.attachments[0].url

                # Send the embed with view and download links
                embed = discord.Embed(
                    title="**Scribd Document Unlocked!**",
                    description="",
                    color=discord.Color.green()
                )
                embed.add_field(name="Download Your Answer:", value=f"[Download Answer]({download_url})", inline=False)
                embed.add_field(name="View Your Question:", value=f"[View Answer]({embed_link})", inline=False)
                
                if message.author.avatar:
                    embed.set_footer(text=message.author.display_name, icon_url=message.author.avatar.url)
                else:
                    embed.set_footer(text=message.author.display_name)

                await message.channel.send(embed=embed)

                # Clean up the local file
                os.remove(file_path)

    async def on_error(self, event_method, *args, **kwargs):
        print(f'Error occurred in {event_method}: {args[0]}')

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the bot token from the .env file
    token = os.getenv('DISCORD_TOKEN')

    # Initialize the bot
    bot = ScribdBot()

    # Run the bot using the token from the .env file
    bot.run(token)
