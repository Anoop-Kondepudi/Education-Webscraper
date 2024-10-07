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

class StudyBot(commands.Bot):
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

        allowed_channels = [1240006256278638662, 1278490959075610775, 1278490605886111816]
        if message.channel.id not in allowed_channels:
            return

        study_url_list = re.findall(r'https:\/\/study\.com\/academy\/lesson\/\S+', message.content)

        if len(study_url_list) > 0:
            await message.add_reaction('⏳')
            await self.queue.put((message.author, message, study_url_list))
            if not self.running:
                self.running = True
                await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            author, message, url_list = await self.queue.get()
            for url in url_list:
                # Unpack the three returned values
                html_content, file_name, video_link = await self.get_study_html(url)
                
                if not html_content:
                    embed = discord.Embed(
                        color=0xFF0000
                    )
                    embed.add_field(name='Error', value='Failed to retrieve HTML content.', inline=False)
                    await message.channel.send(embed=embed)
                else:
                    sanitized_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                    file_path = os.path.join("C:\\Users\\MCBat\\Downloads", f"{sanitized_file_name}.html")

                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)

                    sent_message = await message.channel.send(file=discord.File(file_path))
                    file_download_link = sent_message.attachments[0].url

                    embed = discord.Embed(
                        title="**Study.com Lesson Unlocked!**",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name='View Lesson', value=f'[Download]({file_download_link})', inline=False)
                    embed.add_field(name='Lesson Link', value=f'[Lesson]({url})', inline=False)

                    # Add the video link to the embed, if found
                    if video_link:
                        embed.add_field(name='Lesson Video', value=f'[Watch Video]({video_link})', inline=False)

                    if author.avatar:
                        embed.set_footer(text=author.display_name, icon_url=author.avatar.url)
                    else:
                        embed.set_footer(text=author.display_name)

                    await message.channel.send(embed=embed)

                    # Delete the file after sending it
                    if os.path.exists(file_path):
                        os.remove(file_path)

            await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False


    import re

    async def get_study_html(self, url):
        cookie_string = "hasSeen=true; ariel=c28d413001e691c1625e2a3e7a54c191; _sv=D; _idsv=D; member=1638094549000; __stripe_mid=5d947973-f1bb-4779-9f17-b1d45ca5db2f7edd85; paidTrialEligible=true; aens=enp; cocoon=; NODEID=bda84ac7; surveyCriteriaUrlPatterns=INVALID_INELIGIBLE; ssoe_debug=basicPrice2023-control.basicPriceOct2023-v1.braintree-V3.breakthroughLogo-control.ccButtonColor-control.ccButtonCopy-create.ccpaCompactFooter-x.cherryPickQuestions-v1.claimStatsRedesign-v1.classroomTeacherPriceOct2023-v1.customCourseModuleReact-react.cxSocialProof-x.dummy20240529-test.eagerlyRenderPartialRegModal-control.emailCollectionForm-v1.emphasizeCoupon-x.enrollSuccessOverlayReact-x.familyPlanChangeStudentAccountReact-x.feedbackCarouselReact-control.feedbackInlineReact-react.forum-partnersonly.globalCssDefer-v1.hideSixMonthCta-hide.homepage2024-v4stacked.improvePracticeOnBuyPages-3.jsPaywall-control.lessonPageLeftRail-courseNavigator.lessonPageSegmenterFourUp-control.lessonSingleColumnLayout-x.lessonTableOfContentsModernize-v1.lessonTableOfContentsPosition-aboveCourseNav.lessonTabsBelowVideo-control.lowLevelPillarPage-x.mobileApp-control.mobileVideoAboveFold-x.nitpuxAIAssistant-control.pauseTrial-control.pillarNavMember-control.ppcLesson-v25.ppcVideoHero-control.practiceQuestionLoading-control.premiumPrice2023-control.premiumPriceOct2023-v1.priceTestSavingsBadge-percentOff.printQuizReactPage-control.reactAddOrInviteStudent-x.reactBellNotificationsAllNavs-v1.reactBilling-control.reactSchoolCredit-control.regCtaTest-control.removeTutoringFromTopNav-v1.renameCX-saver.replaceCtaFromRightSidebar-inLeftRail.seoInterlinking-v1.smsAcquisition-x.smsAcquisitionV3-x.someoneJustSubscribed-control.steelhouse-control.stickyBarManager-v1.studyGoalControlsReact-x.teacherPriceOct2023-v1.testPrepAiAssistantBeta-control.testPrepCourseNameWithSocialProof-x.testPrepIntegratedUx-v1.testPrepPrice202307-control.testPrepYoutubeVideoSection-x.updateCxRegFlow-control; requestGuid=3e200e91c2f5f3bfc219256b237207e6; announcements-date=2024-09-11T17:37:13-05:00; __stripe_sid=a709dc8a-837d-4065-b810-0cddec348b8af0b13c; datadome=2VZNMfEpL0raRqkAqvXfXZcotR~q706TBYIUvsw3MesCLbSbtMotmB375pYCI0fFMKVA229S8ohda~EsHjPj1KfNx1AnBsJa5nB6ca6VernnpR04N5EwmJIe9S1eJcbJ"

        cookies = {}
        for item in cookie_string.split('; '):
            key, value = item.split('=', 1)
            cookies[key] = value

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        response = requests.get(url, cookies=cookies, headers=headers)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the video .mp4 links before any formatting
        html_str = str(soup)
        mp4_links = re.findall(r'https://[\w./-]+\.mp4', html_str)

        # Print all found .mp4 links to the terminal
        if mp4_links:
            print("Found .mp4 links:")
            for link in mp4_links:
                print(link)
        else:
            print("No .mp4 links found")

        # Store the first .mp4 link to be returned in the Discord message
        video_link = mp4_links[0] if mp4_links else None

        # Now proceed to remove specific elements
        selectors_to_remove = [
            '#hiddenVideoTools',
            '#tab-links',
            '#seo-video-container > aside',
            '#seo-cta-container',
            '#mainContainer > div.lesson-with-left-rail-course-nav > div.lesson-left-rail',
            'body > nav',
            '#mainContainer > div.hdiv',
            '#videoLessonWrapper > div > header > div',
            '#seo-description-container',
            '#videoLessonWrapper > div > main > div',
            '#transcriptPaywall',
            '#seo-related-study-materials-tabbed',
            '#videoLessonWrapper > div > section',
            '#searchBrowseModule',
            '#upgradeToEnrollModal',
            '#footer',
            '#partialRegFormModal'
        ]

        for selector in selectors_to_remove:
            element = soup.select_one(selector)
            if element:
                element.decompose()  # Remove the element from the HTML

        file_name = url.split('/')[-1]
        return str(soup), file_name, video_link

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the .env file
token = os.getenv('DISCORD_TOKEN')

# Initialize the bot
bot = StudyBot()

# Run the bot using the token from the .env file
bot.run(token)
