import discord
from discord.ext import commands, tasks
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

class CheggLinkSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = r"E:\100115.txt"  # Replace with your actual file path
        self.channel_id = 1287858800526884875  # Replace with your actual channel ID
        self.send_links.start()  # Start the task when the bot is ready

    @tasks.loop(seconds=1)  # Check every second for new messages and send the link if not rate limited
    async def send_links(self):
        # Get the channel and ensure it's valid
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            print(f"Channel ID {self.channel_id} not found or the bot has no access.")
            return

        # Read the file for the next link
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                lines = file.readlines()

            if lines:
                # Read the first link
                chegg_link = lines[0].strip()

                if chegg_link:
                    # Send the message
                    try:
                        message = await channel.send(chegg_link)
                        print(f"Sent: {chegg_link}")

                        # Remove the link from the file
                        with open(self.file_path, "w") as file:
                            file.writelines(lines[1:])  # Remove the first line

                        # Delete the message
                        await message.delete()
                        print(f"Deleted: {chegg_link}")

                    except discord.errors.HTTPException as e:
                        print(f"Rate limited or error occurred: {e}. Waiting before retrying.")
                        await asyncio.sleep(5)  # Wait before retrying due to rate limit

            else:
                print("File is empty. Stopping the loop.")
                self.send_links.stop()  # Stop the loop if the file is empty
        else:
            print(f"File {self.file_path} not found.")
            self.send_links.stop()  # Stop the loop if the file doesn't exist

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready and started sending links.")
        # Start the task only when the bot is ready
        self.send_links.start()

# Set up the bot and add the cog
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def main():
    # Add the cog to the bot in an async context
    await bot.add_cog(CheggLinkSender(bot))
    # Start the bot
    await bot.start('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')

# Use asyncio.run to start the bot
asyncio.run(main())
