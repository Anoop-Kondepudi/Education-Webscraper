import discord
from discord.ext import commands, tasks
import sqlite3
import asyncio
from datetime import datetime, timezone, timedelta

# Setup the bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
db = sqlite3.connect('trialUsers.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, assigned_at TEXT, notified INTEGER DEFAULT 0)''')
db.commit()

# Channel and Role IDs
CHANNEL_ID = 1267340900091301909  # Replace with your channel ID
ROLE_ID = 1267339418734170132    # Replace with your role ID
GUILD_ID = 1236810621731733624   # Replace with your guild ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    remove_expired_roles.start()  # Start the task to check and remove expired roles

@tasks.loop(minutes=1)  # Check every 1 minute
async def remove_expired_roles():
    print("Checking for expired roles...")
    # Calculate the cutoff time for role removal
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)  # Trial duration is 30 minutes
    cursor.execute('SELECT id FROM users WHERE assigned_at <= ? AND notified = 0', (cutoff_time.isoformat(),))
    rows = cursor.fetchall()
    
    for row in rows:
        user_id = row[0]
        guild = bot.get_guild(GUILD_ID)
        if guild:
            role = guild.get_role(ROLE_ID)
            if role:
                member = guild.get_member(int(user_id))
                if member:
                    await member.remove_roles(role)
                    cursor.execute('UPDATE users SET notified = 1 WHERE id = ?', (user_id,))
                    db.commit()
                    print(f"Role removed from user {user_id}. User ID retained in database.")
                    channel = bot.get_channel(CHANNEL_ID)
                    if channel:
                        await channel.send(f"{member.mention}, your trial has ended. Please consider inviting 25 for the `Inviter` role or purchasing a pass/subscription from <#1254914316533235712> for as low as $1. Thank you!")
                else:
                    print(f"Member with ID {user_id} not found in guild {guild.name}.")
            else:
                print(f"Role with ID {ROLE_ID} not found in guild {guild.name}.")
        else:
            print(f"Guild with ID {GUILD_ID} not found.")

@bot.command()
async def trial(ctx):
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("This command can't be used in this channel.")
        return  # Ignore commands outside the specified channel

    user_id = str(ctx.author.id)
    cursor.execute('SELECT id FROM users WHERE id=?', (user_id,))
    row = cursor.fetchone()

    if row:
        await ctx.send("You've already used your trial.")
    else:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            role = guild.get_role(ROLE_ID)
            if role:
                await ctx.author.add_roles(role)
                cursor.execute('INSERT INTO users (id, assigned_at) VALUES (?, ?)', 
                               (user_id, datetime.now(timezone.utc).isoformat()))
                db.commit()
                await ctx.send(f"{ctx.author.mention}, you have been granted the `Trial Access` role for 30 minutes!")
            else:
                await ctx.send("Role not found.")
        else:
            await ctx.send("Guild not found.")

@bot.command()
async def history(ctx):
    cursor.execute('SELECT id, assigned_at FROM users')
    rows = cursor.fetchall()
    
    if not rows:
        await ctx.send("No trial history available.")
        return
    
    embed = discord.Embed(title="Trial Access History", color=discord.Color.blue())
    for row in rows:
        user_id, assigned_at = row
        user = await bot.fetch_user(int(user_id))
        if user:
            assigned_time = datetime.fromisoformat(assigned_at).strftime('%Y-%m-%d %H:%M:%S UTC')
            embed.add_field(name=f"User {user.name}", value=f"<@!{user_id}> claimed the Trial Access role on <t:{int(datetime.fromisoformat(assigned_at).timestamp())}:F>", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    # Total users who have claimed the Trial Access role
    cursor.execute('SELECT COUNT(*) FROM users')
    total_claimed = cursor.fetchone()[0]

    # Users currently with the Trial Access role
    guild = bot.get_guild(GUILD_ID)
    if guild:
        role = guild.get_role(ROLE_ID)
        if role:
            current_trial_users = len(role.members)
        else:
            current_trial_users = 0
    else:
        current_trial_users = 0

    # Total users notified (trial expired)
    cursor.execute('SELECT COUNT(*) FROM users WHERE notified = 1')
    total_notified = cursor.fetchone()[0]

    await ctx.send(f"**Trial Access Stats**\n"
                   f"Total users who claimed: {total_claimed}\n"
                   f"Current Trial Access users: {current_trial_users}\n"
                   f"Total users notified (trial expired): {total_notified}")

bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')
