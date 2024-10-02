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
            "_delighted_web": "{%22vRjf6mEd4ps2NtAE%22:{%22_delighted_fst%22:{%22t%22:%221720933872410%22}%2C%22_delighted_lst%22:{%22t%22:%221720972015744%22%2C%22m%22:{%22token%22:%22iFUzyGFlrTo44VSETcInKAbu%22}}}}",
            "_ga": "GA1.1.1289500183.1727220268",
            "_ga_SCG9G524F3": "GS1.1.1727220267.1.1.1727220372.47.0.0",
            "_gcl_au": "1.1.1826821450.1727220268",
            "ajs_anonymous_id": "$device:192265b0aa38db0-075777412fbb6d-26001051-306000-192265b0aa38db0",
            "OptanonAlertBoxClosed": "2024-07-18T19:23:29.935Z",
            "OptanonConsent": "isGpcEnabled=0&datestamp=Fri+Sep+06+2024+16%3A02%3A46+GMT-0500+(Central+Daylight+Time)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=US%3BTX&AwaitingReconsent=false",
            "_px3": "00b56a0cf50a90e1299f824d331f5d35cced50e95181a779b85c88764898cf21:HiYnkNAIqcnYHm14AWbRFygjHIkZtQ/BE9s3+a0w3dU84KNLwxQsDqODdD1op+gqFyWeaJQLz8nJmOiePCkakQ==:1000:glmiw6jADdWvDunWYbebMzb2+FXPMY96nuTdGIYfVWiAW3OMGyCOYnzUiJWMWva3NDKxDkOWgDVtSJuA48uBQjABqldfXsSj3jvwaJfvNCMvl+cVWJwMMi3Rc71GvDGsNBzYtNTNlBFE7LIu87SHBzpMCtGesMNl+DCE2MUTlX5eP7ztfGjcu6C/3+vvagiX9mN8au2kpq2GVQ9ePEuXjpJDZ2rAnaosNUaGtb7gfb0=",
            "_pxhd": "hAmeIezd4TsXaMC7JTSg3q7k4hgZ6FypXrIyi6/NDIJznMT-DqCbHQQmIzD0O30YguH70YDu1XpBMPijQm98Rw==:fpair/rgQk/HWl48hPJ9k-a3kHxdDYLLKWXwHenEELf2dvNbZtJiM5zeyjNJiTtNKT1EPSh1FU6Oog/Btz1lB/2sYw2xtY60lr1zpRI1mgg=",
            "_pxvid": "61b4d352-419f-11ef-b74a-70d2e6bb2ae4",
            "laravel_session": "eyJpdiI6IlZFQmNMeUdYa0paQXdKWUFnVmxyNWc9PSIsInZhbHVlIjoiNkpKQm1DQ2w3N3RnQkpoMWViczlYYnNsQS9BT1M3aHpKUVlhcWFmMXBVWEQ1V1IvL29ZaXdaVkl6Q0pTTFJWblkvRkFwQnBXSVczNU1nM2NndlIxcTk3ZW1EUzh4Uk0yRXdDY1pIWlprYlByUG1paEg3ZElRZ01vZFRLS2traDEiLCJtYWMiOiJmNGEzMTRhNzUwODA2YzQwYzQ0ZGFhOGY5ZWNhNzk1NDNjMmNlMzA1NTYwMjQ3YjljMTNlMjA4MDM5NGZiZWQyIiwidGFnIjoiIn0=",
            "locale": "eyJpdiI6ImttdEllYnNkd3FYMjlxTzNIL3FmM1E9PSIsInZhbHVlIjoiV0RKbVhYL1RBdUZZVVMwNXNyVG1MQy9UTXZJc09RVnBGdmwwNU04V085ajhUVHFBaURGSHNUQ2htM0JKaTdVayIsIm1hYyI6Ijg4ZTcyMTczNGNmMzAxMTdmOWJjOTNiZDE0ZDgzMTliYTY2MmQ3ZDMzZDEyNjgzNTg5NjAyMTFhOGVlM2M5MzYiLCJ0YWciOiIifQ==",
            "pxcts": "53e6f251-7d2c-11ef-a089-2fe58eae20fa",
            "rel_strat": "3ebce356%7CFALSE",
            "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": "eyJpdiI6ImRaWGRxNlpla0dkR3krYnkwdFlFWEE9PSIsInZhbHVlIjoiVEkwZnVmbVdEdUo5aThWbnVxV0FkQjJFTjBpSXEvRTR0Q1BwdVFOL29VQm40WjhxejhPRnZpYnRkNktib1dCcm0xMEd2U0d2UHJDekpUVGdTdWxzNWd1YnJyN3N6U1NwWHgraDBzbm1wTVh0M0ZqWjBka3gxcGpiZS9RZDVPNVh3VnNsdEtjNEZocTEzK3Jhc3hRVW9aVmNTUFVRczlNRTR2dGR0dHd3YXpIaXJJQThVSEFJZXdoKzMvbGEzUnVvTG8venE4cGxPcldYNnhGWGFJdXBQKzhPSjFEWE1XWGV1ZVZzNFo4cXg5Zz0iLCJtYWMiOiJhYWI0MzM4YjFiYzlmNjg0YWU4ZmIxYzUxOWYzNDdkMDk1MDYyMmNmNGQxZGZhYTBjZThlZTk4NjZkN2VjZTY5IiwidGFnIjoiIn0=",
            "sd_cid": "393b2e4f-10a9-4834-b600-47e3ef1e60e0",
            "sd_docs": "eyJpdiI6IjFEUFgxWTlTZ0JjYVpxVCszNXJBanc9PSIsInZhbHVlIjoiWTdPdEZKYmhLQ1ErSWE4dWk2amlqSDQ2cXYrc2xQSEU1R1pDSGJwQzlXVSswWGowZU1NRUZUWmNwblN4eUprZVdCZC84OXBjdmhqS3JwNFFOaUo1a25DTzMrcXNZdmxmcTk0WDNRTUc0WU41bENURXRKbW1DZTNYUGRZdklZdE5Ld3h3YjllclEvbkJyYzRUZkk0MXlVRlVkUllxNkhxWjhTOU1CdGxCYjdlenpzcStVMW5LMTFlVk1UaGdnMUUzSFVOZW5XMmxER2tNSkY3UkY0cnQyL3YrVEZQalZWaVNzM3ozS3NuV3NXOWNxUmpHVEJBcEJPc09GZFoxcWp4M2RpbXF0a09FeG5ROVZSYkVPZWJNL1Z4bHhEVHNCWCswSkp5d1ZnVnViSUczV0FoWTNrNHpoTFVYc1QwQ0kwUVAiLCJtYWMiOiI1MWQxODNhZDg3NDIyZTRkMGQ1YWU0NGVkNWQxYzYwZGQ1Mzk4ODdjMjFiNWJhOTI2N2UxNjhkY2IzMDhkODNkIiwidGFnIjoiIn0=",
            "sdab": "eyJpdiI6Ik9XZmZnVVhYQzg5NGI4K3d2aFNsMUE9PSIsInZhbHVlIjoiWG5rS3lZY0U5YlovcERwd2VUSW9nRnFKN2RxUVV5RDhMcGpHTFdVajRWK1BDR1lFTFl6eVdXVUhNK3JmVGFsQnAvMzdhdlM1OEZPN1lOdVhUSjN2YjdZaG0yOHVsd0g3QTczNXNmYStHcjlqWkVaYjhicjJTV2dxOWtiR25UZFRTaEREUllDNWZHSjVJQmNjZ3ZrWnNHcWd5MUdUT3VqU0pTVE45SHZFYUlIMDRReVlxeFA3TisvOUNwOUVPeGZtTk4zVWVCRXZzWUZDbFNVTXZDRzhsRDJvUUNkSDZMZDlldjUzTlRQSmNqRDA4OElFZWdCR2lsMVAxelA2VFNnRDAwaUZtUzNUU1g1eExyWGplZjVCVkpnakFmczVyV1Y2ZUNHbEp4L1dLZjVGYTNqaFFtbG5SMDJueWFxdmVrbXY2djJhYVh0N05rV2Uyb1E1UWdMbnVnQnY3azEyLzBMMDI4RjZmWkMxdjVVPSIsIm1hYyI6ImJiYTgwODI1N2I1YmI5MDIzMTk5Y2Q2YjlkNDFjYTY2MWNlOWEyNTM1N2EwM2Y1ZDJiMmE4YzQ1ZTgxMWJkMzUiLCJ0YWciOiIifQ==",
            "studocu": "eyJpdiI6IktqaDgrRWNPQW94aTF5VURMM1BhVGc9PSIsInZhbHVlIjoiSGZDQ1FNbkVYSlRORmVBQW84YXJPR3A3SHIzUHIrazZkQ25rOGNWelc1QTJxZU9Gc2dhR2pLTGVhV0duZUppRlNmRnRUZHBSQ3hCdVdCNTdpSzc4czA0UHMvZXFSNFNmbi81c2h2UjZDTUJ2WU9zMGcwemd3QkpXc1FVOTBEYXAzd3lJdnEvSUpYVEJMWlZMZ0F1b2FUUC9uZ1J3RjZqOUV5SGg5OU9nN1N0RGdMZWQvUXhHTkFoR0tGSFBQbFMvWSsxRzN5cm1BYVl0bCsvWFpDakhDWG1jbzZIV3J0b2l1TlpXWHVEcmZiNDgxS2ZYc1c0WUtQZ3IrUlh5OEZkVENCMEI3RjFOVmJwMXFjaW9DcVpIUVR0YjZ2cW9OelRLbUc4NktDTm13YXhFWlJwbGFtUXNqanZreXRmU2dhbHgvT2VZL1ZybG1VSzJjSkFjY212RzdkSEtBYVZob2hTb1k3cDVRZGRZbnJqQXVPYzNId0w0N2lsTEdVZ25qTlNaQWJoWWI2Z0hrMDNkNnRNUWhmYlRVT0FoL01WQ3NiQ0JSUCtjckdmNmh0bjViRGh1SDZmOWN4NDVSSVpXejE2dHI4QzF5MEpTblFLQUthNWxTN3V6QkdrT20yUVRDYkEwR3VQY3N5K3N6cW5yOTBrdVlSanpJTjJxUXBMRW9mTkMwTHQ2c2EraVJNalMvL21ZSkd1K0pJbGZRUzFGMDQ3dnlTTE5qM3ZwTHo5VkJlMjZFTDRZLzVUM1g5TzhHT0dQT2ZvSUQ1V0VGS0Rhay9SYzNjRUErdis4b3ZuclNVUVlmbDMyZTUzQnZFUDdsWHZKVEY0SEE3U1lJRmpDb3l2bklCa2ZvMXlKUUs3cFYrNE1kUUNpc1hHanViNXJLUHR2ZFBaVWRZUEZwc3FnZ29tcjVYbHdRMjQ1eUVqdm1mL0trYW81bDhoWS9SZ0doUElESUc3amR4UmIzOTlJUjZqTGNsK3hGRVY4TjZPWm5TcTBGY0o5bDZCUy96SjU0YjZGVmlOWmlQN3BQR0xGSWZsZEN4ZzNwNHk4alBnOVQrNmZaU1BGZ0lKYVVxSEE1c0FlODRmMVBsTFFYVzBmR3Z0UncyK0U0R3ZHWlBSRm05MkV1RGlINjJ1UTUwVGVncHBTTjlxOUhaSUtuTFBIaUVkc09Ub0gwQ3QwSXg1cXYwNHpxQmlUOEhwT0Fzc0k4cW1CZ1NBTXF3Um1oK0dVelVQeUZoTXozQzdhcHd0Wkd4a09qR0pNRGpGWmNKVDFZK1FiRlBLZHpldG5HbjFsM1BkOE1oOFR2enUvU0JRRVVLRUxieFdvSktBVitzeUtzWXUwUFZmVXlhZUdXTFdva0ZlRnRkMklQTjgwdmxCaXRNRWk0VlRJdGFCMUVrcDFOQ0lWRkl6UDdkVWY5VGNEc29EOXpHVnNIalVwWEduY1FkRlFyR0dOS3JnVDhJdHBmb05JS0pZVHhuc3djSkRUcks0RXV6RjYwcnFQVUdLZE4rc2tMRXhSeUxSZVVJaEhNL0M4dThKdjF5YXBicTdicHR4WEhBRlFoK3FCZEFKQmRDajFYdUtiVWEyWG5mdFdGaHk1b0Q0TzNrem9EMG1qbUNPRzJTaXJuWjJhMEdsVVFxQWFrKzVoSmdvMGtOZVgwbFNyV0tiZHdlSHB0U0xPZGI3RkRaRlhtTlBSc0h2Uml3a1RULzhWUkFtdDBJMVV5RUdmaVFuV0YxNHZvWnlPdlI3c3Z5QW82NHQwOWpoUnU1NXBKVm54Q0xDOVJ3ZHE0S0V1ZWtzYW4rRGlaYzFlY2dtNWFlYUpGMm5mOFcxSzJPczdlSStpUzFlSGNlWTlKak5XK2dTcTRMQ3VoaDVlMHFGOE9oU3hKS21GWDk2OFl3VEZOcXNQeU4zUGdKVHEvVS92RllHRVVJYW9hbnBUaS95a2p0Nk55em5aK2pCdkNwWi9HWks2SE9LZ085RVkrZjVEaC9mUHlvem82bm03QmMzZTk2WDdnT3JYc3BOdlNxSE5UQjN3RjlESERmcXFqaDQ3bG9GRk5TakhNRUpwcENmT050UzV0YUcxQTU2cGlCMWo5SG1EOUp3TEdGQy9VL0UrV2d1Sks1Tm4yYk1LRFlBMHVEUTZkQjFHZ1pSMklNM0JoSVVicGFmRytRMUpRdWsycFpjYUIrWG9IeUtWMU5WRWI5YjhESFAyTG0xSThjTWc0SU5haDdpSmZYRXFxcDFwZGVqLzhRPT0iLCJtYWMiOiJjYjQ4N2JkNDQyYTI1ZmU0MDQ5Mzc3YWQ3YjlhOTM4Y2EyMDc2ZDc2NDhlNjlkNmFiMjI3OTEzMTYxY2VkMTE3IiwidGFnIjoiIn0=",
            "studocu_popup": "eyJpdiI6IjRGSHBSeVAvcmtNa1VqR29Nbm9JRVE9PSIsInZhbHVlIjoiTXIwNkRxSG43TTl2c0VHQjFUanNZZXNDMTN5RFNHVFRVRUZXRzU3R3ozUGowQ0lha25xdUdVSlhadkRGTks0aSIsIm1hYyI6IjgxZjdkMmZiOTA1NTlkMzliOGZmZmQ2MDc5MjRhZGNlMjhiNDVhODU1MDk3NWYwNDE5ZWFlMDNlZTc5NTcyNmUiLCJ0YWciOiIifQ==",
            "XSRF-TOKEN": "eyJpdiI6Im1qU2YzQ05BSXgybSt5Q0N0VHJ2Y2c9PSIsInZhbHVlIjoiT2NyMnNRaHZMaHppUjhFS3RjdFNsUHpwVmtJZWprQ2NPQnJJYlhRdkRaWXZOUzBxUG5hTlprU0s1NjdxK081VUh3dVRXSzUyVC9oaU9OajNWeXBaazlZMGNLWWNnNnBFYmd3T2JiQWJrN3N5V25Dc0owbWI3OG5IM05aMGUrVDUiLCJtYWMiOiI4YmNhNDI0YTNlOWFhN2RiNTczYWM0NmNkZWYyZGFjZWEzNzRlNjhjNjg5NzA3ZTMxNDM0ZjA0MzJhZjgzZTBhIiwidGFnIjoiIn0="
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
            "_delighted_web": "{%22vRjf6mEd4ps2NtAE%22:{%22_delighted_fst%22:{%22t%22:%221720933872410%22}%2C%22_delighted_lst%22:{%22t%22:%221720972015744%22%2C%22m%22:{%22token%22:%22iFUzyGFlrTo44VSETcInKAbu%22}}}}",
            "_ga": "GA1.1.1289500183.1727220268",
            "_ga_SCG9G524F3": "GS1.1.1727220267.1.1.1727220372.47.0.0",
            "_gcl_au": "1.1.1826821450.1727220268",
            "ajs_anonymous_id": "$device:192265b0aa38db0-075777412fbb6d-26001051-306000-192265b0aa38db0",
            "OptanonAlertBoxClosed": "2024-07-18T19:23:29.935Z",
            "OptanonConsent": "isGpcEnabled=0&datestamp=Fri+Sep+06+2024+16%3A02%3A46+GMT-0500+(Central+Daylight+Time)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=US%3BTX&AwaitingReconsent=false",
            "_px3": "00b56a0cf50a90e1299f824d331f5d35cced50e95181a779b85c88764898cf21:HiYnkNAIqcnYHm14AWbRFygjHIkZtQ/BE9s3+a0w3dU84KNLwxQsDqODdD1op+gqFyWeaJQLz8nJmOiePCkakQ==:1000:glmiw6jADdWvDunWYbebMzb2+FXPMY96nuTdGIYfVWiAW3OMGyCOYnzUiJWMWva3NDKxDkOWgDVtSJuA48uBQjABqldfXsSj3jvwaJfvNCMvl+cVWJwMMi3Rc71GvDGsNBzYtNTNlBFE7LIu87SHBzpMCtGesMNl+DCE2MUTlX5eP7ztfGjcu6C/3+vvagiX9mN8au2kpq2GVQ9ePEuXjpJDZ2rAnaosNUaGtb7gfb0=",
            "_pxhd": "hAmeIezd4TsXaMC7JTSg3q7k4hgZ6FypXrIyi6/NDIJznMT-DqCbHQQmIzD0O30YguH70YDu1XpBMPijQm98Rw==:fpair/rgQk/HWl48hPJ9k-a3kHxdDYLLKWXwHenEELf2dvNbZtJiM5zeyjNJiTtNKT1EPSh1FU6Oog/Btz1lB/2sYw2xtY60lr1zpRI1mgg=",
            "_pxvid": "61b4d352-419f-11ef-b74a-70d2e6bb2ae4",
            "laravel_session": "eyJpdiI6IlZFQmNMeUdYa0paQXdKWUFnVmxyNWc9PSIsInZhbHVlIjoiNkpKQm1DQ2w3N3RnQkpoMWViczlYYnNsQS9BT1M3aHpKUVlhcWFmMXBVWEQ1V1IvL29ZaXdaVkl6Q0pTTFJWblkvRkFwQnBXSVczNU1nM2NndlIxcTk3ZW1EUzh4Uk0yRXdDY1pIWlprYlByUG1paEg3ZElRZ01vZFRLS2traDEiLCJtYWMiOiJmNGEzMTRhNzUwODA2YzQwYzQ0ZGFhOGY5ZWNhNzk1NDNjMmNlMzA1NTYwMjQ3YjljMTNlMjA4MDM5NGZiZWQyIiwidGFnIjoiIn0=",
            "locale": "eyJpdiI6ImttdEllYnNkd3FYMjlxTzNIL3FmM1E9PSIsInZhbHVlIjoiV0RKbVhYL1RBdUZZVVMwNXNyVG1MQy9UTXZJc09RVnBGdmwwNU04V085ajhUVHFBaURGSHNUQ2htM0JKaTdVayIsIm1hYyI6Ijg4ZTcyMTczNGNmMzAxMTdmOWJjOTNiZDE0ZDgzMTliYTY2MmQ3ZDMzZDEyNjgzNTg5NjAyMTFhOGVlM2M5MzYiLCJ0YWciOiIifQ==",
            "pxcts": "53e6f251-7d2c-11ef-a089-2fe58eae20fa",
            "rel_strat": "3ebce356%7CFALSE",
            "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d": "eyJpdiI6ImRaWGRxNlpla0dkR3krYnkwdFlFWEE9PSIsInZhbHVlIjoiVEkwZnVmbVdEdUo5aThWbnVxV0FkQjJFTjBpSXEvRTR0Q1BwdVFOL29VQm40WjhxejhPRnZpYnRkNktib1dCcm0xMEd2U0d2UHJDekpUVGdTdWxzNWd1YnJyN3N6U1NwWHgraDBzbm1wTVh0M0ZqWjBka3gxcGpiZS9RZDVPNVh3VnNsdEtjNEZocTEzK3Jhc3hRVW9aVmNTUFVRczlNRTR2dGR0dHd3YXpIaXJJQThVSEFJZXdoKzMvbGEzUnVvTG8venE4cGxPcldYNnhGWGFJdXBQKzhPSjFEWE1XWGV1ZVZzNFo4cXg5Zz0iLCJtYWMiOiJhYWI0MzM4YjFiYzlmNjg0YWU4ZmIxYzUxOWYzNDdkMDk1MDYyMmNmNGQxZGZhYTBjZThlZTk4NjZkN2VjZTY5IiwidGFnIjoiIn0=",
            "sd_cid": "393b2e4f-10a9-4834-b600-47e3ef1e60e0",
            "sd_docs": "eyJpdiI6IjFEUFgxWTlTZ0JjYVpxVCszNXJBanc9PSIsInZhbHVlIjoiWTdPdEZKYmhLQ1ErSWE4dWk2amlqSDQ2cXYrc2xQSEU1R1pDSGJwQzlXVSswWGowZU1NRUZUWmNwblN4eUprZVdCZC84OXBjdmhqS3JwNFFOaUo1a25DTzMrcXNZdmxmcTk0WDNRTUc0WU41bENURXRKbW1DZTNYUGRZdklZdE5Ld3h3YjllclEvbkJyYzRUZkk0MXlVRlVkUllxNkhxWjhTOU1CdGxCYjdlenpzcStVMW5LMTFlVk1UaGdnMUUzSFVOZW5XMmxER2tNSkY3UkY0cnQyL3YrVEZQalZWaVNzM3ozS3NuV3NXOWNxUmpHVEJBcEJPc09GZFoxcWp4M2RpbXF0a09FeG5ROVZSYkVPZWJNL1Z4bHhEVHNCWCswSkp5d1ZnVnViSUczV0FoWTNrNHpoTFVYc1QwQ0kwUVAiLCJtYWMiOiI1MWQxODNhZDg3NDIyZTRkMGQ1YWU0NGVkNWQxYzYwZGQ1Mzk4ODdjMjFiNWJhOTI2N2UxNjhkY2IzMDhkODNkIiwidGFnIjoiIn0=",
            "sdab": "eyJpdiI6Ik9XZmZnVVhYQzg5NGI4K3d2aFNsMUE9PSIsInZhbHVlIjoiWG5rS3lZY0U5YlovcERwd2VUSW9nRnFKN2RxUVV5RDhMcGpHTFdVajRWK1BDR1lFTFl6eVdXVUhNK3JmVGFsQnAvMzdhdlM1OEZPN1lOdVhUSjN2YjdZaG0yOHVsd0g3QTczNXNmYStHcjlqWkVaYjhicjJTV2dxOWtiR25UZFRTaEREUllDNWZHSjVJQmNjZ3ZrWnNHcWd5MUdUT3VqU0pTVE45SHZFYUlIMDRReVlxeFA3TisvOUNwOUVPeGZtTk4zVWVCRXZzWUZDbFNVTXZDRzhsRDJvUUNkSDZMZDlldjUzTlRQSmNqRDA4OElFZWdCR2lsMVAxelA2VFNnRDAwaUZtUzNUU1g1eExyWGplZjVCVkpnakFmczVyV1Y2ZUNHbEp4L1dLZjVGYTNqaFFtbG5SMDJueWFxdmVrbXY2djJhYVh0N05rV2Uyb1E1UWdMbnVnQnY3azEyLzBMMDI4RjZmWkMxdjVVPSIsIm1hYyI6ImJiYTgwODI1N2I1YmI5MDIzMTk5Y2Q2YjlkNDFjYTY2MWNlOWEyNTM1N2EwM2Y1ZDJiMmE4YzQ1ZTgxMWJkMzUiLCJ0YWciOiIifQ==",
            "studocu": "eyJpdiI6IktqaDgrRWNPQW94aTF5VURMM1BhVGc9PSIsInZhbHVlIjoiSGZDQ1FNbkVYSlRORmVBQW84YXJPR3A3SHIzUHIrazZkQ25rOGNWelc1QTJxZU9Gc2dhR2pLTGVhV0duZUppRlNmRnRUZHBSQ3hCdVdCNTdpSzc4czA0UHMvZXFSNFNmbi81c2h2UjZDTUJ2WU9zMGcwemd3QkpXc1FVOTBEYXAzd3lJdnEvSUpYVEJMWlZMZ0F1b2FUUC9uZ1J3RjZqOUV5SGg5OU9nN1N0RGdMZWQvUXhHTkFoR0tGSFBQbFMvWSsxRzN5cm1BYVl0bCsvWFpDakhDWG1jbzZIV3J0b2l1TlpXWHVEcmZiNDgxS2ZYc1c0WUtQZ3IrUlh5OEZkVENCMEI3RjFOVmJwMXFjaW9DcVpIUVR0YjZ2cW9OelRLbUc4NktDTm13YXhFWlJwbGFtUXNqanZreXRmU2dhbHgvT2VZL1ZybG1VSzJjSkFjY212RzdkSEtBYVZob2hTb1k3cDVRZGRZbnJqQXVPYzNId0w0N2lsTEdVZ25qTlNaQWJoWWI2Z0hrMDNkNnRNUWhmYlRVT0FoL01WQ3NiQ0JSUCtjckdmNmh0bjViRGh1SDZmOWN4NDVSSVpXejE2dHI4QzF5MEpTblFLQUthNWxTN3V6QkdrT20yUVRDYkEwR3VQY3N5K3N6cW5yOTBrdVlSanpJTjJxUXBMRW9mTkMwTHQ2c2EraVJNalMvL21ZSkd1K0pJbGZRUzFGMDQ3dnlTTE5qM3ZwTHo5VkJlMjZFTDRZLzVUM1g5TzhHT0dQT2ZvSUQ1V0VGS0Rhay9SYzNjRUErdis4b3ZuclNVUVlmbDMyZTUzQnZFUDdsWHZKVEY0SEE3U1lJRmpDb3l2bklCa2ZvMXlKUUs3cFYrNE1kUUNpc1hHanViNXJLUHR2ZFBaVWRZUEZwc3FnZ29tcjVYbHdRMjQ1eUVqdm1mL0trYW81bDhoWS9SZ0doUElESUc3amR4UmIzOTlJUjZqTGNsK3hGRVY4TjZPWm5TcTBGY0o5bDZCUy96SjU0YjZGVmlOWmlQN3BQR0xGSWZsZEN4ZzNwNHk4alBnOVQrNmZaU1BGZ0lKYVVxSEE1c0FlODRmMVBsTFFYVzBmR3Z0UncyK0U0R3ZHWlBSRm05MkV1RGlINjJ1UTUwVGVncHBTTjlxOUhaSUtuTFBIaUVkc09Ub0gwQ3QwSXg1cXYwNHpxQmlUOEhwT0Fzc0k4cW1CZ1NBTXF3Um1oK0dVelVQeUZoTXozQzdhcHd0Wkd4a09qR0pNRGpGWmNKVDFZK1FiRlBLZHpldG5HbjFsM1BkOE1oOFR2enUvU0JRRVVLRUxieFdvSktBVitzeUtzWXUwUFZmVXlhZUdXTFdva0ZlRnRkMklQTjgwdmxCaXRNRWk0VlRJdGFCMUVrcDFOQ0lWRkl6UDdkVWY5VGNEc29EOXpHVnNIalVwWEduY1FkRlFyR0dOS3JnVDhJdHBmb05JS0pZVHhuc3djSkRUcks0RXV6RjYwcnFQVUdLZE4rc2tMRXhSeUxSZVVJaEhNL0M4dThKdjF5YXBicTdicHR4WEhBRlFoK3FCZEFKQmRDajFYdUtiVWEyWG5mdFdGaHk1b0Q0TzNrem9EMG1qbUNPRzJTaXJuWjJhMEdsVVFxQWFrKzVoSmdvMGtOZVgwbFNyV0tiZHdlSHB0U0xPZGI3RkRaRlhtTlBSc0h2Uml3a1RULzhWUkFtdDBJMVV5RUdmaVFuV0YxNHZvWnlPdlI3c3Z5QW82NHQwOWpoUnU1NXBKVm54Q0xDOVJ3ZHE0S0V1ZWtzYW4rRGlaYzFlY2dtNWFlYUpGMm5mOFcxSzJPczdlSStpUzFlSGNlWTlKak5XK2dTcTRMQ3VoaDVlMHFGOE9oU3hKS21GWDk2OFl3VEZOcXNQeU4zUGdKVHEvVS92RllHRVVJYW9hbnBUaS95a2p0Nk55em5aK2pCdkNwWi9HWks2SE9LZ085RVkrZjVEaC9mUHlvem82bm03QmMzZTk2WDdnT3JYc3BOdlNxSE5UQjN3RjlESERmcXFqaDQ3bG9GRk5TakhNRUpwcENmT050UzV0YUcxQTU2cGlCMWo5SG1EOUp3TEdGQy9VL0UrV2d1Sks1Tm4yYk1LRFlBMHVEUTZkQjFHZ1pSMklNM0JoSVVicGFmRytRMUpRdWsycFpjYUIrWG9IeUtWMU5WRWI5YjhESFAyTG0xSThjTWc0SU5haDdpSmZYRXFxcDFwZGVqLzhRPT0iLCJtYWMiOiJjYjQ4N2JkNDQyYTI1ZmU0MDQ5Mzc3YWQ3YjlhOTM4Y2EyMDc2ZDc2NDhlNjlkNmFiMjI3OTEzMTYxY2VkMTE3IiwidGFnIjoiIn0=",
            "studocu_popup": "eyJpdiI6IjRGSHBSeVAvcmtNa1VqR29Nbm9JRVE9PSIsInZhbHVlIjoiTXIwNkRxSG43TTl2c0VHQjFUanNZZXNDMTN5RFNHVFRVRUZXRzU3R3ozUGowQ0lha25xdUdVSlhadkRGTks0aSIsIm1hYyI6IjgxZjdkMmZiOTA1NTlkMzliOGZmZmQ2MDc5MjRhZGNlMjhiNDVhODU1MDk3NWYwNDE5ZWFlMDNlZTc5NTcyNmUiLCJ0YWciOiIifQ==",
            "XSRF-TOKEN": "eyJpdiI6Im1qU2YzQ05BSXgybSt5Q0N0VHJ2Y2c9PSIsInZhbHVlIjoiT2NyMnNRaHZMaHppUjhFS3RjdFNsUHpwVmtJZWprQ2NPQnJJYlhRdkRaWXZOUzBxUG5hTlprU0s1NjdxK081VUh3dVRXSzUyVC9oaU9OajNWeXBaazlZMGNLWWNnNnBFYmd3T2JiQWJrN3N5V25Dc0owbWI3OG5IM05aMGUrVDUiLCJtYWMiOiI4YmNhNDI0YTNlOWFhN2RiNTczYWM0NmNkZWYyZGFjZWEzNzRlNjhjNjg5NzA3ZTMxNDM0ZjA0MzJhZjgzZTBhIiwidGFnIjoiIn0="
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
