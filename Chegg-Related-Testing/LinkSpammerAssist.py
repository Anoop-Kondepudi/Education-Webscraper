import discord
from discord.ext import commands

# Initialize the bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Define the ID of the Egg Bot
EGG_BOT_ID = 1283659292469362711

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    # Check if the message is from Egg Bot
    if message.author.id == EGG_BOT_ID:
        # Check if the message contains 😔 or ⚠️
        if '😔' in message.content or '⚠️' in message.content:
            try:
                await message.delete()
                print(f"Deleted message from Egg Bot containing '😔' or '⚠️': {message.content}")
            except discord.errors.Forbidden:
                print("Bot lacks permission to delete this message.")
            except discord.errors.HTTPException as e:
                print(f"Failed to delete message: {e}")

# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual bot token
bot.run('MTI4NzkxNzEwMzExMzgzNDU1Ng.Gozfz4.luzPIB1upicL05JBOtAnnLX4YP1ENwsD_X1Oi8')
