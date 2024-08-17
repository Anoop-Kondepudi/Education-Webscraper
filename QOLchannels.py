import discord
from discord.ext import commands
import asyncio

# Define the necessary intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True  # Required for commands to work properly

# Create an instance of Bot with the command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define the channel configurations (channel_id: (role_id, open_name, close_name))
CHANNEL_CONFIGS = {
    1259682197221408888: (1258194950277959710, '🟢-cours3hero-bot', '🔴-cours3hero-bot'),
    1261921662278828133: (1258194950277959710, '🟢-bartl3by-bot', '🔴-bartl3by-bot'),
    1262252612590239834: (1258194950277959710, '🟢-bra1nly-bot', '🔴-bra1nly-bot'),
    1262185849324306612: (1258194950277959710, '🟢-num3rade-bot', '🔴-num3rade-bot'),
    1262248765037871136: (1258194950277959710, '🟢-scr1bd-bot', '🔴-scr1bd-bot'),
    1262248819895177416: (1258194950277959710, '🟢-stud0cu-bot', '🔴-stud0cu-bot'),
    1258196398093111426: (1258194950277959710, '🟢-ch3gg-bot', '🔴-ch3gg-bot'),
    1273812941099237546: (1258194950277959710, '🟢-quizl3t-bot', '🔴-quizl3t-bot'),
}

# Authorized user IDs
AUTHORIZED_USERS = [823981400260476968, 1032536677186543616]

# Event to notify when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Close command
@bot.command()
async def close(ctx):
    config = CHANNEL_CONFIGS.get(ctx.channel.id)
    if config and ctx.author.id in AUTHORIZED_USERS:
        role_id, open_name, close_name = config
        role = ctx.guild.get_role(role_id)
        await ctx.channel.set_permissions(role, send_messages=False)
        await ctx.channel.edit(name=close_name)
        await ctx.send("The channel has been closed.")
        await asyncio.sleep(2)  # Add delay between requests
    else:
        await ctx.send("You don't have permission to execute this command or the channel is not configured.")

# Open command
@bot.command()
async def open(ctx):
    config = CHANNEL_CONFIGS.get(ctx.channel.id)
    if config and ctx.author.id in AUTHORIZED_USERS:
        role_id, open_name, close_name = config
        role = ctx.guild.get_role(role_id)
        await ctx.channel.set_permissions(role, send_messages=True)
        await ctx.channel.edit(name=open_name)
        await ctx.send("The channel has been opened.")
        await asyncio.sleep(2)  # Add delay between requests
    else:
        await ctx.send("You don't have permission to execute this command or the channel is not configured.")

# Run the bot with your bot token
bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')