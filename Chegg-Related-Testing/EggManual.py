import discord
from discord.ext import commands
import re
import os

# Replace with your bot's token
TOKEN = 'MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s'
CHANNEL_ID = 1269414620150366323  # The channel ID you want to monitor
USER_ID = 823981400260476968      # The user ID allowed to use the commands
LOADING_EMOJI = 1240447269313183785  # ID for loading emoji
CHECKMARK_EMOJI = 1240449377806319616  # ID for checkmark emoji
XMARK_EMOJI = 1240449376703484004      # ID for X mark emoji

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

# Setting up the bot with a command prefix and intents
bot = commands.Bot(command_prefix='?', intents=intents)

# Regex pattern for Chegg link
chegg_url_pattern = re.compile(
    r'https:\/\/www\.chegg\.com\/homework-help\/questions-and-answers\/[a-zA-Z0-9_-]+-q([0-9]+)'
)

# Event: Bot Ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot is ready and monitoring channel: {CHANNEL_ID}')

# Command: Save Chegg links from the last {number} messages
@bot.command(name='save')
async def save_links(ctx, number: int):
    # Check if the command user is the allowed user
    if ctx.author.id != USER_ID:
        await ctx.send("You are not allowed to use this command.")
        return

    # Check if the command is issued in the correct channel
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("This command can only be used in the specified channel.")
        return

    # Fetch the last {number} messages
    messages = []
    async for message in ctx.channel.history(limit=number):
        messages.append(message)
        
    chegg_links = []

    # Fetch custom emoji objects
    loading_emoji = bot.get_emoji(LOADING_EMOJI)
    checkmark_emoji = bot.get_emoji(CHECKMARK_EMOJI)
    xmark_emoji = bot.get_emoji(XMARK_EMOJI)

    for message in messages:
        if message.author.bot:
            continue

        # Search for Chegg links in the message
        chegg_url_match = chegg_url_pattern.search(message.content)
        if chegg_url_match:
            question_id = chegg_url_match.group(1)
            chegg_links.append(chegg_url_match.group(0))  # Save the entire link
            if loading_emoji:
                await message.add_reaction(loading_emoji)  # Add custom emoji
            else:
                await message.add_reaction("⏳")  # Add a default Unicode emoji as a fallback

    # Save all detected links to a .txt file
    with open('chegg_links.txt', 'w') as file:
        for link in chegg_links:
            file.write(f'{link}\n')

    await ctx.send(f'Saved {len(chegg_links)} Chegg links to chegg_links.txt. Please process and save HTML files into E:\\egg.')

# Command: Answer based on the question number
@bot.command(name='answer')
async def send_answer(ctx, number_of_messages: int = 100):  # Accept number of messages to search
    # Check if the command user is the allowed user
    if ctx.author.id != USER_ID:
        await ctx.send("You are not allowed to use this command.")
        return

    # Fetch custom emoji objects
    loading_emoji = bot.get_emoji(LOADING_EMOJI)
    checkmark_emoji = bot.get_emoji(CHECKMARK_EMOJI)
    xmark_emoji = bot.get_emoji(XMARK_EMOJI)

    # Find messages with the loading emoji
    channel = bot.get_channel(CHANNEL_ID)
    
    # Collect messages into a list
    messages = []
    async for message in channel.history(limit=number_of_messages):
        messages.append(message)
    
    for message in messages:
        if loading_emoji and str(loading_emoji) in [str(reaction.emoji) for reaction in message.reactions]:
            # Extract question ID from the message content
            chegg_url_match = chegg_url_pattern.search(message.content)
            if chegg_url_match:
                question_id = chegg_url_match.group(1)
                # Attempt to send the HTML file via DM to the original message author
                html_filename = f'q{question_id}.html'
                file_path = os.path.join('E:\\egg', html_filename)
                try:
                    await message.author.send(file=discord.File(file_path))  # Send to original author
                    await message.clear_reactions()
                    if checkmark_emoji:
                        await message.add_reaction(checkmark_emoji)
                    else:
                        await message.add_reaction("✅")  # Default Unicode emoji as a fallback
                except Exception as e:
                    await message.clear_reactions()
                    if xmark_emoji:
                        await message.add_reaction(xmark_emoji)
                    else:
                        await message.add_reaction("❌")  # Default Unicode emoji as a fallback
                    await ctx.send(f'Failed to send the file for q{question_id}. Error: {e}')

    await ctx.send(f'Checked the last {number_of_messages} messages for matching questions.')

# Run the bot
bot.run(TOKEN)