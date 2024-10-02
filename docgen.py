import aiohttp
import asyncio
import time
import boto3
import discord
from discord.ext import commands
import os
import random
import secrets
import zipfile
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
allowed_channel_ids = [1080721350332792922, 1264247366202953729, 1260659627654123612, 1285650825514979351]  # Add more channel IDs as needed

s3_bucket_name = 'studysolutions'  # Replace with your AWS S3 bucket name
aws_access_key = 'AKIAZQ3DR6XOHHTMTHIE'
aws_secret_key = 'zICOZ3Pb91mzw2H8N0kfGWUgeIK51LdG4TeL6MO4'
aws_region = 'us-east-2'

s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

pdf_folder = "pdfs"  # The folder to store PDFs

if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

class WritePdf:
    def __init__(self, title, questions_data):
        self.title = title.split('-')[0]
        self.questions_data = questions_data
        self.file_paths = []

    def write_pdf(self):
        type = random.choice(['QUIZ', 'MCQS', 'Q&A', 'Puzzler', 'Trivia', "Test"])
        file_name = f"{self.title}{type} {random.randint(0, 100)}.pdf".replace(' ', '_').replace('/', '')
        file_path = os.path.join(pdf_folder, file_name)
        self.file_paths.append(file_path)
        docu = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        doc_style = styles["Heading2"]
        doc_style.alignment = 1
        docc_style = styles["Heading3"]
        docc_style.alignment = 1
        title = Paragraph(f"{self.title} - {type}", doc_style)
        random_date = (datetime(2000, 1, 1) + timedelta(days=random.randint(0, (datetime(2023, 12, 31) - datetime(2000, 1, 1)).days))).strftime('%d/%m/%Y')
        subtitle = Paragraph(f"Date: {random_date}<br /><br />", docc_style)

        flowables = [title, subtitle]

        para_style = ParagraphStyle("FileContent", fontSize=12)

        option_para_style = ParagraphStyle("FileContent", fontSize=12, leftIndent=12)

        flowables.extend([Paragraph(f"{q['question']}<br/><br/>", para_style) for q in self.questions_data])

        docu.build(flowables)

        # Delete the file after 60 seconds
        asyncio.create_task(self.delete_file_after_delay(file_path, 60))

    async def delete_file_after_delay(self, file_path, delay_seconds):
        await asyncio.sleep(delay_seconds)
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")

class Generator:
    def __init__(self, docs_number):
        self.docs_number = docs_number

    async def generate_doc(self, session):
        # Clean up old files
        for file_name in os.listdir(pdf_folder):
            file_path = os.path.join(pdf_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        generated_files = []
        for _ in range(self.docs_number):
            while True:
                trivianerd_id = await self.get_trivianerd_id(session)

                if not trivianerd_id:
                    continue

                questions_data = await self.get_questions_data(session, trivianerd_id)

                if not questions_data:
                    continue

                if len(questions_data["trivia"]["questions"]) >= 13:
                    pdf_writer = WritePdf(questions_data["trivia"]["title"], questions_data["trivia"]["questions"])
                    pdf_writer.write_pdf()
                    generated_files.extend(pdf_writer.file_paths)
                    break

        return generated_files

    async def get_trivianerd_id(self, session):
        async with session.get("https://www.trivianerd.com/random-trivia-generator") as response:
            if response.status == 200:
                text = await response.text()
                trivianerd_id = text.split('<div class="mt-3 trivianerd" data-id="')[1].split('"')[0]
                return trivianerd_id
            else:
                return None

    async def get_questions_data(self, session, trivianerd_id):
        async with session.get(f"https://app.trivianerd.com/api/embed/{trivianerd_id}") as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

    async def start(self):
        async with aiohttp.ClientSession() as session:
            generated_files = await self.generate_doc(session)
        return generated_files

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

queue = asyncio.Queue()

@bot.command(name='d')
async def generate_files(ctx, num_files: int):
    if num_files != 10:
        await ctx.send(f"{ctx.author.mention} Please use the command !d 10 to generate files.")
        return

    await queue.put((ctx, num_files))
    await ctx.send(f"{ctx.author.mention} Your request has been added to the queue.")

async def process_queue():
    while True:
        ctx, num_files = await queue.get()
        
        try:
            if ctx.channel.id not in allowed_channel_ids:
                await ctx.send("This command can only be used in the specified channels.")
                continue

            start_time = time.time()

            generator = Generator(num_files)
            file_paths = await generator.start()

            end_time = time.time()
            generation_speed = int((end_time - start_time) * 1000)

            content = f"{ctx.author.mention} Your files have been generated:"
            embed = discord.Embed(title='File Generation', description='', color=0xff6600)
            embed.add_field(name='For', value=ctx.author.mention, inline=True)
            embed.add_field(name='Generation Speed', value=f'{generation_speed} ms', inline=True)
            progress_bar = 'â– ' * 10
            embed.add_field(name='100%', value=f'[{progress_bar}]', inline=True)
            #question_link = "[View Question](https://www.google.com/)"
            #embed.add_field(name='Question Link', value=question_link, inline=True)

            download_link = await generate_s3_presigned_url(file_paths, generator)
            generated_file_link = await generate_s3_presigned_url(file_paths, generator, expiration_time=3600)
            embed.add_field(name='Generated Files', value=f"[View Generated Files]({generated_file_link})", inline=True)

            embed.set_image(url='https://cdn.discordapp.com/attachments/1093746006241329252/1186381745424191568/standard_1.gif')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1093746006241329252/1186392077790085120/icon.png')
            embed.set_footer(text='File Generation v1', icon_url='https://cdn.discordapp.com/attachments/1093746006241329252/1186391457238634556/a-chegg-unlock-icon-egg-83578698.png')

            await ctx.send(content=content, embed=embed)

        except Exception as e:
            print(f"Error in generate_files command: {e}")
            await ctx.send("An error occurred while generating files. Please check the console for details.")

        finally:
            queue.task_done()

async def generate_s3_presigned_url(file_paths, generator, expiration_time=3600):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.relpath(file_path, pdf_folder))

    zip_buffer.seek(0)

    s3_object_key = f"generated_files_{secrets.token_hex(8)}.zip"
    s3_client.upload_fileobj(zip_buffer, s3_bucket_name, s3_object_key)

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': s3_bucket_name,
            'Key': s3_object_key,
        },
        ExpiresIn=expiration_time
    )
    return presigned_url

async def main():
    async with bot:
        bot.loop.create_task(process_queue())
        await bot.start("MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s")

asyncio.run(main())
