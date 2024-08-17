import discord
from discord.ext import commands
import asyncio
import re
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.message_content = True

class BartlebyBot(commands.Bot):
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

        allowed_channels = [1240006256278638662, 1245866706098716822, 1245866164815659123, 1261921662278828133]
        if message.channel.id not in allowed_channels:
            return

        bartleby_url_list = re.findall(r'https:\/\/www\.bartleby\.com\/(?:questions-and-answers|solution-answer)\/\S+', message.content)

        if len(bartleby_url_list) > 0:
            await message.add_reaction('⏳')
            await self.queue.put((message.author, message, bartleby_url_list))
            if not self.running:
                self.running = True
                await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            author, message, url_list = await self.queue.get()
            for url in url_list:
                html_content, file_name = await self.get_bartleby_html(url)
                if not html_content:
                    embed = discord.Embed(
                        color=0xFF0000
                    )
                    embed.add_field(name='Error', value='Failed to retrieve HTML content.', inline=False)
                    await message.channel.send(embed=embed)
                else:
                    # Sanitize the file name by replacing invalid characters
                    sanitized_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                    file_path = os.path.join("C:\\Users\\MCBat\\Downloads", f"{sanitized_file_name}.html")
                    
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)

                    sent_message = await message.channel.send(file=discord.File(file_path))
                    file_download_link = sent_message.attachments[0].url

                    embed = discord.Embed(
                        title="**Bartleby Question Unlocked!**",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name='View Answer', value=f'[Download]({file_download_link})', inline=False)
                    embed.add_field(name='View Question', value=f'[Question]({url})', inline=False)
                    
                    if author.avatar:
                        embed.set_footer(text=author.display_name, icon_url=author.avatar.url)
                    else:
                        embed.set_footer(text=author.display_name)

                    await message.channel.send(embed=embed)

                    # Delete the file after sending it
                    if os.path.exists(file_path):
                        os.remove(file_path)  # This line deletes the file

            await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False

    async def get_bartleby_html(self, url):
        cookie_string = "attentive_id=92cdda5d59cc456aa252075626119113; attn=eyJ1Ijoie1wiY29cIjoxNzIyNjk2Mzk4OTQyLFwidW9cIjoxNzIyNjk2Mzk4OTQyLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjkyY2RkYTVkNTljYzQ1NmFhMjUyMDc1NjI2MTE5MTEzXCJ9In0=; attentive_cco=1722696398950; _gid=GA1.2.1951683253.1722696399; _gat_UA-20169249-1=1; _fbp=fb.1.1722696400167.536923485121505961; G_ENABLED_IDPS=google; FooterBannerVisiblity1=true; viewedPagesCount=3; _tt_enable_cookie=1; _ttp=O8aGIL-jDFZ45BaIwdjFF7RoyPO; ajs_user_id=369fc79a-b669-445c-ab04-5605c872febb; ajs_anonymous_id=d8fecc5c-c716-4530-afd8-feca31229c0d; attentive_dv=1; _clck=19xyozw%7C2%7Cfoa%7C0%7C1676; _ga=GA1.2.1884310578.1722696399; attntv_mstore_email=Donbrobarka@gmail.com:0; refreshToken=20efd8a9ced453406e98d06528076d8a90411ede; userId=72f6123f-a4d6-44ce-82de-551dada3cb50; userStatus=A1; promotionId=; sku=bb699firstweek_1499_intl_plus_3; accessToken=463ae2ab6ab65db854283a7e60ee1ab5fb3499e6; bartlebyRefreshTokenExpiresAt=2024-09-12T11:05:54.274Z; category=Plus; btbHomeDashboardAnimationTriggerDate=2024-08-14T11:05:59.158Z; btbHomeDashboardTooltipAnimationCount=1; _gat_UA-93748-2=1; attentive_ss_referrer=ORGANIC; btbHomeDashboardBonusChallengeModalCount=0; __attentive_pv=2; _ga_R3RTBJZFE8=GS1.1.1723547152.24.1.1723547169.0.0.0; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Aug+13+2024+16%3A36%3A09+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=cb7c7543-7ccd-4f91-81eb-998dfea96b5f&interactionCount=0&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1%2CC0005%3A1&AwaitingReconsent=false"

        cookies = {}
        for item in cookie_string.split('; '):
            key, value = item.split('=', 1)
            cookies[key] = value

        response = requests.get(url, cookies=cookies)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove the specified top container
        top_container = soup.find('div', class_='styles__StickyAtTopFixedOuterContainer-sc-a0ee5f82-0 DVqDN')
        if top_container:
            top_container.decompose()
        
        top_container = soup.find('div', class_='styles__AppLayoutBaseRailWithMargins-sc-a0ee5f82-13')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__BookmarkButtonContainer-sc-70138c7b-13 knplcx')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__AppLayoutBottomContentWithoutRailsOuterWrapper-sc-a0ee5f82-16 cZjjSj')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__AppLayoutFooter-sc-a0ee5f82-12 fYonzL')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__MyAnswerBottomContainer-sc-251af6e9-2 McIdp')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__NextPreviousOuterWrapper-sc-252bf7a5-32')
        if top_container:
            top_container.decompose()

        top_container = soup.find('div', class_='styles__BookmarkSolutionContainer-sc-252bf7a5-17 kNvfOL')
        if top_container:
            top_container.decompose()

        img_tag = soup.find('img', alt='Check Mark')
        if img_tag:
            img_tag.decompose()

        file_name = url.split('/')[-1]
        return str(soup), file_name

bot = BartlebyBot()
bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')