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

        allowed_channels = [1240006256278638662, 1238373245351231509, 1245866164815659123, 1262185849324306612]
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
                video_links = await self.get_numerade_answer(url)
                if not video_links:
                    embed = discord.Embed(
                        color=0xFF0000
                    )
                    embed.add_field(name='Error', value='Failed to retrieve video link.', inline=False)
                    await message.channel.send(embed=embed)
                else:
                    video_link_main, video_link_backup = video_links
                    embed = discord.Embed(
                        title="Numerade Video Generated!",
                        color=discord.Color.green()
                    )
                    embed.add_field(name='Video Answer', value=f'[Here]({video_link_main}) or [Here]({video_link_backup})', inline=False)
                    embed.add_field(name='Requested Link', value=f'[Here]({url})', inline=False)
                    
                    if author.avatar:
                        embed.set_footer(text=author.display_name, icon_url=author.avatar.url)
                    else:
                        embed.set_footer(text=author.display_name)
                    
                    retry_count = 0
                    success = False
                    while not success and retry_count < 3:
                        try:
                            await message.channel.send(embed=embed)
                            await message.channel.send(f'[||VIDEO||]({video_link_main}) or [||VIDEO||]({video_link_backup})')
                            success = True
                        except discord.errors.DiscordServerError as e:
                            retry_count += 1
                            print(f"[DEBUG] Retry {retry_count} due to Discord server error: {str(e)}")
                            await asyncio.sleep(5)  # Wait before retrying

                    if not success:
                        print(f"[DEBUG] Failed to send message after {retry_count} retries.")

                await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False

    async def get_numerade_answer(self, link):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Print the HTML content for debugging
                print("[DEBUG] HTML content loaded:")
                print(soup.prettify())

                video_id = None

                # Check for the project-universal video URL
                project_universal_url_pattern = re.search(r'https://cdn\.numerade\.com/project-universal/previews/([a-zA-Z0-9\-]+)_large.jpg', soup.prettify())
                if project_universal_url_pattern:
                    video_id = project_universal_url_pattern.group(1)
                    print(f"[DEBUG] Project-universal URL found: {project_universal_url_pattern.group(0)}")
                    print(f"[DEBUG] Video ID: {video_id}")
                    video_url_main = f'https://cdn.numerade.com/project-universal/encoded/{video_id}.mp4'
                    return video_url_main, None

                # If project-universal is not found, check for other video URLs
                gif_url_pattern = re.search(r'https://cdn\.numerade\.com/previews/([a-zA-Z0-9\-]+)\.gif', soup.prettify())
                if gif_url_pattern:
                    video_id = gif_url_pattern.group(1)
                    print(f"[DEBUG] GIF URL found: {gif_url_pattern.group(0)}")
                    print(f"[DEBUG] Video ID: {video_id}")
                    video_url_main = f'https://cdn.numerade.com/ask_video/{video_id}.mp4'
                    video_url_backup = f'https://cdn.numerade.com/encoded/{video_id}.mp4'
                    return video_url_main, video_url_backup

                # Check for regular video URL patterns within '/questions/' URLs
                gif_url_pattern_regular = re.search(r'https://cdn\.numerade\.com/previews/([a-zA-Z0-9\-]+)_large.jpg', soup.prettify())
                data_video_url_pattern = soup.find('div', {'data-video-url': True})
                if gif_url_pattern_regular:
                    video_id = gif_url_pattern_regular.group(1)
                    print(f"[DEBUG] Regular GIF URL found: {gif_url_pattern_regular.group(0)}")
                    print(f"[DEBUG] Video ID: {video_id}")
                    video_url_main = f'https://cdn.numerade.com/encoded/{video_id}.mp4'
                    video_url_backup = f'https://cdn.numerade.com/ask_video/{video_id}.mp4'
                    return video_url_main, video_url_backup
                elif data_video_url_pattern:
                    video_id = data_video_url_pattern['data-video-url']
                    print(f"[DEBUG] Data video URL found: {video_id}")
                    video_url_main = f'https://cdn.numerade.com/encoded/{video_id}.mp4'
                    video_url_backup = f'https://cdn.numerade.com/ask_video/{video_id}.mp4'
                    return video_url_main, video_url_backup

                print("[DEBUG] No matching video URL found")
                return None, None
        except Exception as e:
            print(f"[DEBUG] Exception occurred for link: {link}, error: {str(e)}")
            return None, None


if __name__ == '__main__':
    bot = NumeradeBot()
    bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')
