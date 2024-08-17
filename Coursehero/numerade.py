import discord
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup
import asyncio
import re

intents = discord.Intents.default()
intents.message_content = True

class NumeradeBot(commands.Bot):
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

        allowed_channels = [1238373245351231509, 1240006256278638662, 1245866164815659123]
        if message.channel.id not in allowed_channels:
            return

        numerade_url_list = re.findall(r'https:\/\/www\.numerade\.com\/(?:ask\/question|questions)\/\S+', message.content)

        if len(numerade_url_list) > 0:
            await message.add_reaction('⏳')
            await self.queue.put((message.author, message, numerade_url_list))
            if not self.running:
                self.running = True
                await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            author, message, url_list = await self.queue.get()
            for url in url_list:
                video_link = await self.get_numerade_answer(url)
                if not video_link:
                    embed = discord.Embed(
                        color=0xFF0000
                    )
                    embed.add_field(name='Error', value='Failed to retrieve video link.', inline=False)
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Numerade Video Generated!",
                        color=discord.Color.green()
                    )
                    embed.add_field(name='Video Answer', value=f'[Here]({video_link})', inline=False)
                    embed.add_field(name='Requested Link', value=f'[Here]({url})', inline=False)
                    embed.set_footer(text=author.display_name, icon_url=author.avatar.url)
                    await message.channel.send(embed=embed)

                    # Post the video link directly after the embedded message
                    await message.channel.send(f'[||VIDEO||]({video_link})')

            await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False

    async def get_numerade_answer(self, link):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Determine which pattern to search for based on the URL structure
                gif_url = None
                if '/ask/question/' in link:
                    gif_url_pattern = re.search(r'https://cdn\.numerade\.com/previews/\S+\.gif', soup.prettify())
                    if gif_url_pattern:
                        gif_url = gif_url_pattern.group(0)
                        video_id = gif_url.split('/')[-1].split('.')[0]
                        video_url = f'https://cdn.numerade.com/ask_video/{video_id}.mp4'
                        return video_url
                elif '/questions/' in link:
                    # Check for both patterns within '/questions/' URLs
                    gif_url_pattern_project = re.search(r'https://cdn\.numerade\.com/project-universal/previews/\S+\_large.jpg', soup.prettify())
                    gif_url_pattern_regular = re.search(r'https://cdn\.numerade\.com/previews/\S+\_large.jpg', soup.prettify())
                    
                    if gif_url_pattern_project:
                        gif_url = gif_url_pattern_project.group(0)
                        video_id = gif_url.split('/')[-1].split('_')[0]
                        video_url = f'https://cdn.numerade.com/project-universal/encoded/{video_id}.mp4'
                        return video_url
                    elif gif_url_pattern_regular:
                        gif_url = gif_url_pattern_regular.group(0)
                        video_id = gif_url.split('/')[-1].split('_')[0]
                        video_url = f'https://cdn.numerade.com/encoded/{video_id}.mp4'
                        return video_url

                return None
        except Exception as e:
            print(f"[DEBUG] Exception occurred for link: {link}, error: {str(e)}")
            return None


if __name__ == '__main__':
    bot = NumeradeBot()
    bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GvVh8p.mOjqiBuiPYYyjqbwaxKQemrNTwcZd99HrE-ImA')