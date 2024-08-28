import discord
from discord.ext import commands
import asyncio
import re
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.message_content = True

class StudocuBot(commands.Bot):
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

        allowed_channels = [1238373273964777525, 1245866164815659123, 1262248819895177416, 1240006256278638662]
        if message.channel.id not in allowed_channels:
            return

        studocu_url_list = re.findall(r'https:\/\/www\.studocu\.com\/\S+', message.content)

        if len(studocu_url_list) > 0:
            await message.add_reaction('⏳')
            await self.queue.put((message.author, message, studocu_url_list))
            if not self.running:
                self.running = True
                await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            author, message, url_list = await self.queue.get()
            for url in url_list:
                file_name = url.split('/')[-1]
                sanitized_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
                
                # Download PDF
                pdf_url = f"{url}/download/{file_name}.pdf"
                pdf_file_path = os.path.join("C:\\Users\\MCBat\\Downloads", f"{sanitized_file_name}.pdf")
                pdf_success = await self.download_pdf(pdf_url, pdf_file_path)

                if not pdf_success:
                    await message.channel.send(f"Failed to download PDF for {url}")
                
                # If PDF download fails, proceed with HTML backup
                html_content, file_name = await self.get_studocu_html(url)
                if not html_content:
                    embed = discord.Embed(color=0xFF0000)
                    embed.add_field(name='Error', value='Failed to retrieve content.', inline=False)
                    await message.channel.send(embed=embed)
                else:
                    # Save HTML content as a backup
                    html_file_path = os.path.join("C:\\Users\\MCBat\\Downloads", f"{sanitized_file_name}.html")
                    with open(html_file_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)

                    # Upload files to Discord and get links
                    pdf_message, html_message = None, None
                    if pdf_success:
                        pdf_message = await message.channel.send(file=discord.File(pdf_file_path))
                        pdf_link = pdf_message.attachments[0].url
                    else:
                        pdf_link = None

                    html_message = await message.channel.send(file=discord.File(html_file_path))
                    html_link = html_message.attachments[0].url

                    # Create embed message
                    embed = discord.Embed(title="**Studocu Document Unlocked!**", color=discord.Color.blue())
                    if pdf_link:
                        embed.add_field(name='View PDF', value=f'[Download PDF]({pdf_link})', inline=False)
                    else:
                        embed.add_field(name='View PDF', value='PDF could not be downloaded.', inline=False)
                    
                    embed.add_field(name='Backup Answer', value=f'[Download HTML]({html_link})', inline=False)
                    embed.add_field(name='View Question', value=f'[Document Link]({url})', inline=False)

                    if author.avatar:
                        embed.set_footer(text=author.display_name, icon_url=author.avatar.url)
                    else:
                        embed.set_footer(text=author.display_name)

                    await message.channel.send(embed=embed)

                    # Clean up files
                    if pdf_file_path and os.path.exists(pdf_file_path):
                        os.remove(pdf_file_path)
                    if html_file_path and os.path.exists(html_file_path):
                        os.remove(html_file_path)

            await asyncio.sleep(7)  # Delay before processing the next message

        self.running = False

    async def get_studocu_html(self, url):
        # Define the cookies as a dictionary
        cookies = {
            '_delighted_web': '{%22vRjf6mEd4ps2NtAE%22:{%22_delighted_fst%22:{%22t%22:%221720933872410%22}%2C%22_delighted_lst%22:{%22t%22:%221720972015744%22%2C%22m%22:{%22token%22:%22iFUzyGFlrTo44VSETcInKAbu%22}}}}',
            'ajs_anonymous_id': 'a0e634a2-549e-41ee-8470-deee6dfb740d',
            'OptanonAlertBoxClosed': '2024-07-18T19:23:29.935Z',
            'OptanonConsent': 'isGpcEnabled=0&datestamp=Mon+Aug+26+2024+11%3A37%3A42+GMT-0500+(Central+Daylight+Time)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=US%3BTX&AwaitingReconsent=false',
            '_pxhd': 'hAmeIezd4TsXaMC7JTSg3q7k4hgZ6FypXrIyi6/NDIJznMT-DqCbHQQmIzD0O30YguH70YDu1XpBMPijQm98Rw==:fpair/rgQk/HWl48hPJ9k-a3kHxdDYLLKWXwHenEELf2dvNbZtJiM5zeyjNJiTtNKT1EPSh1FU6Oog/Btz1lB/2sYw2xtY60lr1zpRI1mgg=',
            '_pxvid': '61b4d352-419f-11ef-b74a-70d2e6bb2ae4',
            'laravel_session': 'eyJpdiI6InN0SGNtWW5neStmKzlyS0x4b3MwbXc9PSIsInZhbHVlIjoiOUlnYUwrQzJHRWFYYW4wbjU3SFk0QWpDSEtEb3FWU0pqcFgrTGMxenVOaytOOUVnbVdnN1hETXZSNnVNWGJmNXBoSmxZZzV1Y0d0Slg0S0pGWTN0WVFFbGp4Z3A0TTRvQ3BJUlhmaFdLV1F1YU9WeUFjbjVadUlPaytJNi9TNTkiLCJtYWMiOiI1YzM4NWIzOTNiZGVlYjVkY2Q2ZDM2ZDc1ZGYwNjE0OGUyNDBjZThiNGUyZDQ4OWQ5NTM4ZDFkM2FkYjJhYTlkIiwidGFnIjoiIn0%3D',
            'locale': 'eyJpdiI6Ik9xMDNlSG1uUENERHRQRGVIMVUrZVE9PSIsInZhbHVlIjoiUmQyM0IzTCtxZFhMamtjc2piaDdRSHJ6R09TY3dvLy81d1BRVVl4TDkvMjYwS3dnTThpbFJjUW91MnRlVGh5SSIsIm1hYyI6IjQ0OWNjMjY2ZDk4MzVkMGJjNGU1NDcwZjUxODAzOTJmNzI4YzljYmVkMzkxZmNkZjM3ODBlNGU1N2U2NzcwZjMiLCJ0YWciOiIifQ%3D%3D',
            'rel_strat': '49bbcf41%7CFALSE',
            'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IjVpSXVrczkrcVp6ei9tQ2Z3WHVYNEE9PSIsInZhbHVlIjoiUnpaU0Z2ZUVUcVg0MG5weTJ0TVRiU24zNXBIbzFMdFpXblcwVlhYYUk2aWtoSk9hb1VEaXYyYUEwS1dtN0VValcraFcvVkhBNjdOaHUwVXhtLzR1TzZNUTJBUklLZGNyYTNkTkVEdWtoRFhuU0NVUVdRTU5RN1A0cVloNTI1TTRrV203RUYyRXpndWFLQW1kZU45MDBpZlBJZWlyYlpPYy9IYXY3TzJ6eHlGNDR6dmVOUW5aZ0lQeFp6d1lRZjFJR2xaQVMzeFRIWklNRTE4OVZzTlMrSWFaZkVGVlZkb0kzTUlJRllqaUJOWT0iLCJtYWMiOiIzMjk4YjAwYjExMmQ4NmIzNGZkNjQ1Njk0ZTBhNDA1MzM1ODk3MGRlNDA3NDI1M2ViYzA1MWZiYWY3YTkxM2U2IiwidGFnIjoiIn0%3D',
            'sd_cid': '82dad988-12c1-455a-818e-40a273a4110c',
            'sd_docs': 'eyJpdiI6IkhQR0ViM29yT2JGYW1LTXNMUGdJbUE9PSIsInZhbHVlIjoiRkRQK3c0b2ZBYVRicjJ4bnZGb2tPR3lndjM5OUVUMzFHdFZLZ1BNYkExVXF3Njk4ZXNLK2NkdjJwTmhaQWltR0pNSjZ4ejRkQU9uM2ZtVktqNVpoc1FzQU9EWHVvcjVpNlR4UnFJTEI4UUVsTFhnT2RBdT0iLCJtYWMiOiJmOTdmMjY3ZDA5MzcwZWM0YzMyMGE1NzUwYzIxN2Y4NzY2ODI0OTFhZTBkNDI5NzkwMjA2YjEwM2I3ZThhIiwidGFnIjoiIn0%3D'
        }


        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, cookies=cookies, headers=headers)
            if response.status_code != 200:
                return None, None

            soup = BeautifulSoup(response.text, 'html.parser')
            file_name = url.split('/')[-1]
            return str(soup), file_name

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Studocu URL: {e}")
            return None, None

    async def download_pdf(self, pdf_url, pdf_file_path):
        cookies = {
        "_delighted_web": '{%22vRjf6mEd4ps2NtAE%22:{%22_delighted_fst%22:{%22t%22:%221720933872410%22}%2C%22_delighted_lst%22:{%22t%22:%221720972015744%22%2C%22m%22:{%22token%22:%22iFUzyGFlrTo44VSETcInKAbu%22}}}}',
        "ajs_anonymous_id": "a0e634a2-549e-41ee-8470-deee6dfb740d",
        "OptanonAlertBoxClosed": "2024-07-18T19:23:29.935Z",
        "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Jul+29+2024+10%3A37%3A11+GMT-0500+(Central+Daylight+Time)&version=202404.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=US%3BTX&AwaitingReconsent=false",
        "_pxhd": "hAmeIezd4TsXaMC7JTSg3q7k4hgZ6FypXrIyi6/NDIJznMT-DqCbHQQmIzD0O30YguH70YDu1XpBMPijQm98Rw==:fpair/rgQk/HWl48hPJ9k-a3kHxdDYLLKWXwHenEELf2dvNbZtJiM5zeyjNJiTtNKT1EPSh1FU6Oog/Btz1lB/2sYw2xtY60lr1zpRI1mgg=",
        "_pxvid": "61b4d352-419f-11ef-b74a-70d2e6bb2ae4",
        "laravel_session": "eyJpdiI6Imw1QlVrS0tzNThKTW5FZVhPdWhJakE9PSIsInZhbHVlIjoiZzdob1cwdUdhOEUzMmhLamFnOU9xRzNpSk4vNjd0VkZlMVFoNkhmOXNtTlQwRjNSKzVEeis5eW9UZERoQmpQUkNTVUtWYlhXdFROWkRUbjl6ekFBN2FCelRMaktrLzFJWXQ1TVlTcWVjcm10d0liQUJWbFIzYU1HMWUvM2J5WWMiLCJtYWMiOiJiMjAzZjU0OGIxNWQzMWY5MWEwM2U2YzkwYmIwMGQzMTRlNzI5ZTY3YzgwYzM1NjFmMDgwOTBlZWRiNThmYzgxIiwidGFnIjoiIn0=",
        "locale": "eyJpdiI6IlVLN0JWallOekN4NTRSSzhKaDdwMWc9PSIsInZhbHVlIjoiZG43QUpJUEdGQkNoNXRtbDF4dWhSNzhSZUhQajBzSDJnV0FhSVdlUFk5L1QzOXgwUWRSVVZicG8xZ2l5RStneCIsIm1hYyI6IjJjNTkwZGY1N2RlMjg5ZDUxZmJhYTg0MTZkNjRjZGVlZjczNjA4Y2ViZmNmYzcwYjBkMGI1NTAwNjkzMjU4MGEiLCJ0YWciOiIifQ==",
        "rel_strat": "4ab2deb6%7CFALSE",
        "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": "eyJpdiI6Iks1WkpTblZFcUJvWlppSXBWbCsrYUE9PSIsInZhbHVlIjoiUEVSSzhvMFQ2ZzhCdk1qNFVYK0VzUTVvUmxlRHhHR2FuWGNsYlZheW44bzFBZ3BoMEFYU2VqK0FqQ3dSM0Evdm9nWEFrdVE2dThNVGNPRmVmOWNHb1UxeHVTamtUNXBXN2lEdDZRRFJWRG5TeW9GYnRreFBXN25qa2tacjhDMDFhVlVGK1NOdS9SdkVITW9wS2hOZEQ4ZlI0NXBoRmEyRzVzbWxSbXJGK1RodFhCNXNiSjlTMkVZUGl4SzBWSHZnTGM0b0hoQk9qSTJwUktCUjN6MUpxSmEwcTlkSW44UXpCdU1zK1JsT09YZz0iLCJtYWMiOiI0MGRlZGQzNzBlNWEwZTgyN2I2MWJmNzkyMjE1ZjU3MDkxNmFiODA0Yjg4YjFhZWVjYjg3MWI2ZjNkMGRjMmI4IiwidGFnIjoiIn0=",
        "sd_cid": "6b096cbe-5359-4d5d-9e27-ec5befb4b79b",
        "sd_docs": "eyJpdiI6IitlWGdWWEloTUIyMDZVQ3N3WHh5d2c9PSIsInZhbHVlIjoiWkg3RGFyQUlTMTlIYkRsdmRwV0NlRlZEMHkxR2FiVTVFc1JKVUxBNWgrVWhaODE3Y3JOUGdYbEo0MkJIQUxRVjB0QkszS3k3V3VkWGxudDA3VXpEWGo1bWVINEViS01MTVczQlJ3SzFCbEJtOHJFOTNsNWNBb2lEV3l5aDh1d3p0dzBFMFJPNjluZFVCcVF1a0JUTlZFd3RRQmJHVGhVeHRYeHcwTXEwTjJNPSIsIm1hYyI6IjYxNjE1OWQ4YTRkMmQ0ZWRkODdiNWQ0NGQxYzBkZDJhNTcwMmI5NjZlZGNlYTMxNWRjOWRjMGZmNWYzZmZkMDUiLCJ0YWciOiIifQ==",
        "studocu": "eyJpdiI6Img4dWZuS2RFamd4bVFkeHpNWGZuNWc9PSIsInZhbHVlIjoiK0xXd0xMd1l3S3VCU0hqZHV1OVRKSHc3bk9qa2FhM2lwcmJhWWpJQ1lMeFlFQUJyK3FhS20rMTJEbGtwaWVwNE4wNWxyckkyZE5peW4ySFJtNGtvSkJERDlZSmMzYXJIYWtwbHJhcHVPSS91SDVTYTExUkRKWjdJRTFodkt0NzEycW1zamFHSS90d3pvWS9ubXYyR242UlpNcDY5U09yRXdLTTBYRnBGQXVyTzVOQjJCWkpDOS94YUd5VlQ5d0s0U29lV2tPVk9DMjFaZ3gvU2todDU4enJkSFlIUWtYeUxCdWNUMXNZWE5SbFFiTTRDVCtzeWpndmc2d1VNbVlGSG5FSDkwaENYZURHYXJMbVp2TTBPeUdvRmlPZDhya3V6VDYycEVSbUJKbk9ERlBKMHl3cU55Nk9GMzBkUEZZYTQ0UVZGZmdEYmlmZEIzTy9naFg2bEFKbXF5cjR5bldGNWhJT01vMWc4VG9FaHI2QVhZTG5KTGJ5QTZVRnlZb1dwN1VkeVhheXcyaG1mY2dmY2EwT2FBSTY1M25yR3hkWW1hcFN5SXpLcXFpVlE4TnF1QjcvVjhWRU52TUJTQXJJVFROTG41N0hwSEVSUHFlMkpTUkllNEhOVXN6dS8zd1NCNFo0YWZKdHFwWnhrbThjVUJOb2RCa3BnT0dDb0xzOUxvYXVuN1MxdExWaStMbEVPTVBkenRJQ2FFcTNsTkI5MGdjLzh1VnBSYUEwcWl4N3RXOEgyaW4xUWkvTDUveGlKai9uNGtMeVNkM2owemt5TDR6Q3NadlMyTUhOVGoyRWM0NE56bEVnNjUvQ01Sdk1BWENDcFFOUU9rN3dZSEc0T21XOTRGQkpaVjdVWGtQZkZSQk44Q01SNkZnMDVSM1c4OVRBblpSN0lZQnBJYmMrK1ExbmlpT2Y0dXZzWnppbC9jNllWd0FlQWlzV3ZGZmtRWStRc0kxUFBHQUFXcFBudEhESDNGR3VvQTkyR050SW1hRzA2dkhKVHVTZ0xHSThpdFQvN1grZjFaZHFoeUdUcW9ncFNpOVV6QU00aFpGZFZXY0JQSy8wTHlHc1VkR0lsemplbG0ycFk2SDJJMjRzR3RXclcyRnE0UHBvdnlCWWh0NjU2c29XMVNkV0ZNTndwbXhWL2xscytkQWExd2NwYlpjek9QbXdObFVYbE9BNk40NElOR1ZXRU01dzB2aDJBUDd4ZkpBRTdzb0VCeVI5YVNOekZHUktQS0Q1L0trSkwvQ0tNR1N4UFFOaXUyL0N5Q1A5NDdnbE9xWXpnL1RIcFltb1EwbmFqYUcyNFA5Ty9GWm9VS0VybnJOOVNGYmNxR2ROMDVyV2RYVXp6QjlNVkUvOThna3AzclNuaXE5UHorNlh5Tlk4enJXeHVub3daZVA2VDlZUWdKYXgybStjNmE1SGhiRXFxY0I0N2d5RHhYeUJlOE1tTXBwSjZKeFhJRTJQSzBpeTRac29wM1RrdUJUMDVHT0ZONVREdHBPVk9MUTE0TjlpdkwyWHdCeU1RRysyYm4zQk5oWHNnUWl6d0VmQjJ0MFZOQmdSNWQ2OHUvM08xNmYzQUpxQjR5Yk5TRHN1bi9VOUxVTjFEa0Vra3RzYkNwejN4ZFlsZjI0MzhLbWs4ZmUzOTQ0SkdQZGlmeG5VRlhFdmo2NDd4RXBVSkV3MmNIeFVPUStWUjRQckRmK04yMHVxYzRldjA3QXZCSTVzQllma3JrYm8zKzRVVUUxdnBaamp6NkgxMmlvZ0hqUDIvSWphNlprZ2cvYldNTDdHTjQ1R0Y1eUg4cjZMQkJqMis2cTZhSUNaVWYyV2RTK1dZZWprZjZXWkFEY1hhWTRiVmZ5dUhrVGVKOGVNWXR0V0JISVVPU1UwNjNXKy9OSHVHWkpNWmE2Ti9DdVJCRVdiczdvOWVDUlc2UnpDb3VWNFF4ZW5jQ1A1L09JMXJCV2UreHloRCtocUZKWE5zOXJRaDdNb1dSR3p3Z1VmekhPQTJtS3czQnZQN1JpbnZEQnkvNVhRTmlxczd2aUlkU2lFMXFudzBpMVNrR3gyQ01zcUlZUmN3bVdqRDcxSjVCUG9lSGpTSDRwOXFsVHQ3SU1GczlndnRtOHBXcG5aSVRLSmhJbDN4M2dhaXAvK1NLQ1BoaEYvdC95djNaU2ZGb0M4NzRIZXp1Vy9NazFwU1dNcWIyOER2Q3daYko3OUJ0RlFzVzdiZGdGU2YwY0VKOW1FSjR1VmI5c25WbVVyc3JveVEvSW9NL1RJSHBGaU5zUFJaS0huU21CdVQ1dVhXKzVlN1Rxa3JremkvbHRITlhLdUFTdz09",
        "XSRF-TOKEN": "eyJpdiI6IkRiM2MzNktkMnM1bWkxTXBWcktSbEE9PSIsInZhbHVlIjoiamY5OVdVMERNSDVyVnFpWDAvU3F2dUwyUDBiMDdvN3E3aUZYNmQ4bXkxOExHd1VMa2MxMFB1K2I5dHNJN1ZUNnhnUisvbXZPelJ3UVhlb3htQkVUb2JYWFhtU3RwY2ZGOXFnSUR2VXZSNk94R21renliaHNpRUVpQ2RuSDhSUHAiLCJtYWMiOiJiMDJkZDYxZDM0YTJkODdjZWM0Nzg4ZTgxOGY0ZmFhZjNiOGZlMWE1MTY0MjA1YWNmZDUxMTY1ZmJmMTYzNTlhIiwidGFnIjoiIn0="
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(pdf_url, cookies=cookies, headers=headers)
            if response.status_code == 200:
                with open(pdf_file_path, 'wb') as file:
                    file.write(response.content)
                return True
            else:
                print(f"Failed to download PDF from {pdf_url}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF: {e}")
            return False

bot = StudocuBot()
bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')
