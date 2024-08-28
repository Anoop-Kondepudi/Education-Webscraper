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
        cookie_string = "__attentive_id=92cdda5d59cc456aa252075626119113; _attn_=eyJ1Ijoie1wiY29cIjoxNzIyNjk2Mzk4OTQyLFwidW9cIjoxNzIyNjk2Mzk4OTQyLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjkyY2RkYTVkNTljYzQ1NmFhMjUyMDc1NjI2MTE5MTEzXCJ9In0=; __attentive_cco=1722696398950; _gid=GA1.2.1951683253.1722696399; _gat_UA-20169249-1=1; _fbp=fb.1.1722696400167.536923485121505961; G_ENABLED_IDPS=google; FooterBannerVisiblity1=true; viewedPagesCount=3; _tt_enable_cookie=1; _ttp=O8aGIL-jDFZ45BaIwdjFF7RoyPO; _sharedID=4ee393e8-d08f-450f-b4e5-6a72bc4ac1aa; _sharedID_cst=zix7LPQsHA%3D%3D; __qca=P0-1428572696-1723894755082; pbjs-unifiedid_cst=zix7LPQsHA%3D%3D; _cc_id=2771143b886d023655450e1d36b9971a; ajs_user_id=5857bec7-42dd-4e84-853c-a271323289cf; ajs_anonymous_id=0af5da68-2920-4cad-ab48-eb66f4575861; _lc2_fpi=b297128b6752--01j5tvxa30hd4y97qh1rc4pvyx; _lc2_fpi_meta=%7B%22w%22%3A1724257314912%7D; panoramaId=8444c56786d41316a1fc2f363ec7185ca02cc9eaa3e3a0bfce1cfc043a2e804e; pbjs-unifiedid=%7B%22TDID%22%3A%22c2045dc5-5373-466b-8e5e-f59486a2eb75%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222024-07-21T16%3A21%3A56%22%7D; panoramaId_expiry=1724862116445; cto_bundle=-_c5ql83c0c1c2RDYm5odXgzQm5NVGdNMkElMkIwYnBrcmFRUXRJWFREbFZPS20lMkZyejZEJTJGSGdnNEx6bmtOWTFRVm9Gem54ZkdqYXBIeWhCbmolMkJabFhoJTJGS0JLcDRERTh0OEl2MFM1UUhpWjl2U0pRdDRqZlZPYkwybGxWJTJCRFRUd0NvYTR3c1RnQjR3UHY3MHNVV0FEVTF6cHVWaHclM0QlM0Q; cto_bidid=6gpELF8lMkJGbHFGell2TmJqMCUyRmxXSlAwbXJQZG5pRk9Ib3dna3pueHN6MUxBOUhEcndWSDlWb1lxNHdNWlklMkIwbndOSVZvRENCMEc4YXRZSlQ5UTVib2E0R2VmZE9qRGdleU83WiUyQk53M3JOdXdUWVJzJTNE; __gads=ID=9eb3e65892a64e3f:T=1723894757:RT=1724257318:S=ALNI_MYFcN7puwpSge2qQrgPowzwvG8J4g; __gpi=UID=00000ec23f7487d8:T=1723894757:RT=1724257318:S=ALNI_Mbee1WnPa90LEzbtG9NRImuuF6BlA; __eoi=ID=642c153a4c61f051:T=1723894757:RT=1724257318:S=AA-AfjZ5J68HoDMyiPVU3K5UPjxd; __attentive_block=true; __attentive_ss_referrer=ORGANIC; _clck=19xyozw%7C2%7Cfoo%7C0%7C1676; _ga=GA1.2.1884310578.1722696399; __attentive_dv=1; attntv_mstore_email=Demonshsbrobarka@gmail.com:0; refreshToken=13cb57f43cf10b8d549a5e446fbb2c572cf78ccd; userId=1eb463a4-8615-40b0-a113-3d43689e7810; userStatus=A1; promotionId=; sku=bb699firstweek_1499_intl_plus_3; accessToken=c2e9c6833d805822851eec31203f6918fe657d5c; bartlebyRefreshTokenExpiresAt=2024-09-26T15:52:38.299Z; category=Plus; __attentive_pv=3; btbHomeDashboardAnimationTriggerDate=2024-08-28T15:52:51.300Z; btbHomeDashboardTooltipAnimationCount=1; btbHomeDashboardBonusChallengeModalCount=0; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Aug+27+2024+21%3A23%3A19+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=cb7c7543-7ccd-4f91-81eb-998dfea96b5f&interactionCount=0&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1%2CC0005%3A1&AwaitingReconsent=false; _ga_R3RTBJZFE8=GS1.1.1724773932.42.1.1724774000.0.0.0; _clsk=v7vhcc%7C1724774001272%7C3%7C1%7Cz.clarity.ms%2Fcollect"

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