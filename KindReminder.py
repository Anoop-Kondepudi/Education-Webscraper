import discord
from discord.ext import commands
import asyncio
import re

intents = discord.Intents.default()
intents.message_content = True

class LinkBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.queue = asyncio.Queue()
        self.running = False

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        await self.process_message(message)

    async def process_message(self, message):
        if message.author == self.user:
            return

        allowed_channels = [1241857794421035088, 1264247366202953729]
        if message.channel.id not in allowed_channels:
            return

        # Check for Chegg, CourseHero, Bartleby, Brainly, Numerade, Scribd, Studocu URLs
        url_list = re.findall(r'https:\/\/(?:www\.)?(chegg\.com|coursehero\.com|bartleby\.com|brainly\.com|numerade\.com|scribd\.com|studocu\.com)\/\S+', message.content)

        if len(url_list) > 0:
            await message.add_reaction('⏳')
            await self.queue.put((message.author, message, url_list))
            if not self.running:
                self.running = True
                await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            author, message, url_list = await self.queue.get()
            for url in url_list:
                await self.handle_url(author, message, url)
            await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False

    async def handle_url(self, author, message, url):
        embed = self.create_embed(url)
        
        try:
            # Attempt to send a DM to the author
            await author.send(embed=embed)
            await message.add_reaction('✉️')  # Reaction to indicate DM sent successfully

            # Delete the user's original message
            await message.delete()

            # Send a warning message to the user in the server channel
            warning_message = (
                f"Hello {author.mention}, I sent you a DM with some information regarding our server. "
                "Please read over that. If you continue sending question links where it is not meant to be sent, "
                "you will be muted, kicked or even banned. Please do not continue this behavior. Thank you!"
            )
            sent_warning = await message.channel.send(warning_message)

            # Wait 1 minute and then delete the warning message
            await asyncio.sleep(60)
            await sent_warning.delete()

        except discord.Forbidden:
            # If the DM fails, send the embed in the channel where the message was posted
            sent_embed = await message.reply(embed=embed)
            await message.add_reaction('📨')  # Reaction to indicate message sent in the server

            # Wait 1 minute and then delete both the user's message and the embed
            await asyncio.sleep(60)
            await message.delete()
            await sent_embed.delete()


    def create_embed(self, url):
        embed = discord.Embed(
            title="",
            description=(
                "**__To use our services, there are currently 3 ways__** (*Free & Paid*):\n\n"
                "1. **Free Trial!**\n"
                "Do the command: `!trial` in <#1267340900091301909>, and you will be given the <@&1267339418734170132> role for 30 minutes. "
                "During this 30 minute time period, you will be able to send messages in all the unlocks channels.\n\n"
                "2. **Free Access Forever!**\n"
                "If you invite **__25__** friends, you will get access to <#1245866164815659123>, where you can get any question answered. "
                "However, there is a *1 hour* cooldown. (*This cooldown amount may change in the future*).\n\n"
                "3. **Paid Way!**\n"
                "Purchase a pass for as low as **$1** (*Non-Reoccuring Payment*), to get access to all of our services with __no cooldown__!\n\n"
                "Check out our plans here: https://whop.com/study-solutions/ or here <#1254914316533235712>.\n\n"
                "**Need help?**\n"
                "Please read: <#1241993597239164991> to understand more about how the bots work.\n\n"
                "If you have further questions or problems, create a ticket: <#1241861578756722698>.\n\n"
            ),
            color=discord.Color.red()
        )
        embed.set_author(
            name="How To Unlock Your Questions",
            icon_url="https://cdn.discordapp.com/attachments/1241540891001225226/1243070186148466798/7cee5b62-479d-4320-93fe-3e265316e4fa.jpg?ex=66afb793&is=66ae6613&hm=93c598fdd2c60969358fa79ca61e8b5cd4da3e9e011f4edcfbf808bd7e805ab8&"
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1241540891001225226/1243070186148466798/7cee5b62-479d-4320-93fe-3e265316e4fa.jpg?ex=66afb793&is=66ae6613&hm=93c598fdd2c60969358fa79ca61e8b5cd4da3e9e011f4edcfbf808bd7e805ab8&"
        )
        embed.set_footer(
            text="Please ping zellydom (zelly) if you have any questions, comments, or concerns.",
            icon_url="https://cdn.discordapp.com/attachments/1241540891001225226/1243070186148466798/7cee5b62-479d-4320-93fe-3e265316e4fa.jpg?ex=66afb793&is=66ae6613&hm=93c598fdd2c60969358fa79ca61e8b5cd4da3e9e011f4edcfbf808bd7e805ab8&"
        )
        return embed

bot = LinkBot()
bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')
