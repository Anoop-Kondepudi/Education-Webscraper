import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
import re

# Define the bot and intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True  # Enable members intent to modify roles

bot = commands.Bot(command_prefix="?", intents=intents)

# Constants
TARGET_SERVER_ID = 1236810621731733624  # Replace with your server ID
TICKET_TOOL_ID = 557628352828014614     # Ticket Tool bot ID
CHEGG_ROLE_ID = 1241543024320843806     # Role ID to be assigned for Chegg links
ADMIN_USER_ID = 823981400260476968      # Replace with the ID of the user allowed to use the ?clear command
LOG_CHANNEL_ID = 1288697786149113879    # Channel ID for logging actions
TICKET_PREFIX = "ticket-"               # Prefix for ticket channels

# Function to log actions taken on a ticket
async def log_action(ticket_channel, action, ticket_deleted):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        ticket_number = ticket_channel.name
        log_message = f"""
#{ticket_number}
** **
{action}
** **
Ticket Deleted: {ticket_deleted}
"""
        await log_channel.send(log_message)
        print(f"Logged action for {ticket_number} in log channel.")

# Check and delete tickets based on conditions
async def check_and_clear_tickets(guild, ctx):
    print(f"Checking tickets in server {guild.name}...")
    for channel in guild.text_channels:
        if channel.name.startswith(TICKET_PREFIX):
            user_who_opened_ticket = None
            async for message in channel.history(limit=1, oldest_first=True):
                if message.author.id == TICKET_TOOL_ID:
                    if message.mentions:
                        user_who_opened_ticket = message.mentions[0]  # Get the first mentioned user

            if user_who_opened_ticket:
                # Check if the user has sent any messages after 30 minutes
                user_message_found = False
                chegg_link_found = False
                role = guild.get_role(CHEGG_ROLE_ID)
                
                async for message in channel.history(limit=100):
                    if message.author.id == user_who_opened_ticket.id:
                        user_message_found = True
                        break

                    if re.findall(r'(?:https?://)?(?:www\.)?chegg\.com/(?:homework-help|study-guide)/\S+', message.content):
                        if role not in user_who_opened_ticket.roles:
                            chegg_link_found = True

                # Action log variable
                action_log = ""

                # Check if 30 minutes have passed without a message from the user
                if not user_message_found:
                    creation_time = datetime.fromisoformat(message.created_at.isoformat())
                    time_since_creation = datetime.now(timezone.utc) - creation_time
                    if time_since_creation.total_seconds() > 1800:
                        action_log += f"No response from <@!{user_who_opened_ticket.id}> in 30 minutes. "
                        await channel.delete(reason="No response from user after 30 minutes.")
                        action_log += "Deleted the ticket."
                        await log_action(channel, action_log, "Yes")
                        continue

                # If Chegg link is found and user does not have the role, assign role and notify
                if chegg_link_found:
                    await user_who_opened_ticket.add_roles(role)
                    action_log += f"Gave user: <@!{user_who_opened_ticket.id}> Chegg Role because Chegg link in ticket. "
                    try:
                        await user_who_opened_ticket.send(f"Hello {user_who_opened_ticket.mention}, I've given you the role manually, please refer to: <#1241993597239164991> to learn how our server works!")
                        action_log += "Successfully DM'ed user."
                    except discord.Forbidden:
                        await channel.send(f"Hello {user_who_opened_ticket.mention}, I've given you the role manually, please refer to: <#1241993597239164991> to learn how our server works!")
                        action_log += "Unable to DM user. Sent message in ticket channel."
                    await log_action(channel, action_log, "No")
    
    await ctx.send("Ticket cleanup process completed!")  # Indicate the process is finished

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Command to clear inactive tickets
@bot.command()
async def clear(ctx):
    if ctx.author.id == ADMIN_USER_ID:
        guild = bot.get_guild(TARGET_SERVER_ID)
        if guild:
            await ctx.send("Ticket cleanup process started...")
            await check_and_clear_tickets(guild, ctx)
        else:
            await ctx.send("Server not found.")
    else:
        await ctx.send("You do not have permission to use this command.")

# Add your bot token
TOKEN = 'MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s'  # Replace with your actual bot token

# Run the bot
bot.run(TOKEN)
