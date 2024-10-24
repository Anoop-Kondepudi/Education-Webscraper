import discord
from discord.ext import commands
import asyncio
import re
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

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
        cookie_string = "__attentive_id=52e7892753d548b8a6393dab3ab75fe2; _attn_=eyJ1Ijoie1wiY29cIjoxNzI2Njg3MjI5Mjk2LFwidW9cIjoxNzI2Njg3MjI5Mjk2LFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjUyZTc4OTI3NTNkNTQ4YjhhNjM5M2RhYjNhYjc1ZmUyXCJ9In0=; __attentive_cco=1726687229306; G_ENABLED_IDPS=google; viewedPagesCount=3; _gid=GA1.2.2035215044.1726774304; _gat_UA-20169249-1=1; _fbp=fb.1.1726774304464.30552403223013135; OTGPPConsent=DBABLA~BVQqAAAACgA.QA; _tt_enable_cookie=1; _ttp=GJpIajYxeuZdqWZrEGnnaKLSeD6; cdn.bartleby.126401.ka.ck=d2bac3da56db3d0beb66adef9cfa9588ccbba8866f8b920b74c3bc5fc901572895c007cb9fbe8fc9443e975e2a43f126877d82d5a0337f34f0deafc25258d388db0e1cbc92589dd66ce4d14b8ae886a80111b52a86b05450833e5a601145b9c1de12e873e445e6d6940f2908bff8d28a9475b47ea9316f515b5510adf2eb3fd8492ac7cdcf889baad5d96bbaaed05ff0592db759a55c23c2a5cdf8; _sharedID=35102185-9e3d-4bfe-9e0d-96e4057ca9c9; _sharedID_cst=zix7LPQsHA%3D%3D; pbjs-unifiedid_cst=zix7LPQsHA%3D%3D; _cc_id=8e5d0397fc15504f26e7ac0831078833; __qca=P0-384749698-1727438557108; pbjs-unifiedid=%7B%22TDID%22%3A%22e1556a55-913f-448d-8391-2c7b640806eb%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222024-08-29T20%3A18%3A17%22%7D; __gads=ID=8e4bc9a018421cb0:T=1727438567:RT=1727666286:S=ALNI_MZGTiD5ENJq5q6B5nm41fH6PS992Q; __gpi=UID=00000f2061ed0bb6:T=1727438567:RT=1727666286:S=ALNI_Mb22PCBl_tk26k8byu1O3oz7riEcw; __eoi=ID=490be4010895bad1:T=1727438567:RT=1727666286:S=AA-AfjaHZ_ySbW5HEU6dbM9xo2e-; ajs_user_id=f0a0eb35-fe11-41d2-bd80-3a3ab8d06ba0; ajs_anonymous_id=557e3bdb-81ee-4768-91ab-ec82e430da84; _clck=1x7wr1g%7C2%7Cfpv%7C0%7C1723; __attentive_dv=1; _ga=GA1.2.60156874.1726687229; attntv_mstore_email=dashboard+mena@gmail.com:0; refreshToken=43e2489d469ede02966967c4aae809872e08ac68; userId=651230b5-c9af-44f2-899b-fb34c51301a7; userStatus=A1; promotionId=; sku=bb699firstweek_1499_intl_plus_3; accessToken=b9d09db9ef191425ef01b9d4b4a8d684b9428da8; bartlebyRefreshTokenExpiresAt=2024-11-08T04:38:07.477Z; category=Plus; __attentive_ss_referrer=ORGANIC; btbHomeDashboardAnimationTriggerDate=2024-10-10T04:38:14.878Z; btbHomeDashboardTooltipAnimationCount=1; _gat_UA-93748-2=1; __attentive_pv=2; ABTastySession=mrasn=&lp=https%253A%252F%252Fwww.bartleby.com%252Fdashboard%252Fhome; ABTasty=uid=gzhtq1p97c8ayka3&fst=1727288571061&pst=1728316610843&cst=1728448695035&ns=9&pvt=239&pvis=2&th=1310541.1624107.64.1.6.1.1727757872864.1728448697285.0.9; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Oct+09+2024+10%3A08%3A21+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=dd5e7176-79fd-4edb-9d00-748f91c451a5&interactionCount=0&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1%2CC0005%3A1&AwaitingReconsent=false&GPPCookiesCount=1; _ga_R3RTBJZFE8=GS1.1.1728448681.30.1.1728448702.0.0.0"

        cookies = {}
        for item in cookie_string.split('; '):
            key, value = item.split('=', 1)
            cookies[key] = value

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': url
        }

        response = requests.get(url, cookies=cookies, headers=headers)
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

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Run the bot using the token from the environment
bot = BartlebyBot()
bot.run(DISCORD_TOKEN)