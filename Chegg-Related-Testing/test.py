import discord
from discord.ext import commands, tasks
import asyncio
import os
import re
from bs4 import BeautifulSoup

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Ensure message content intent is enabled
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot IDs and paths
response_bot_id = 1258201729179189389  # Replace with the bot ID to send DM to
save_directory = "E:\\egg"  # Replace with your desired directory path
link_file_path = "unique_chegg_links.txt"  # Path to the file with the links
failed_links_path = "failed_processed_links.txt"  # Path to save failed links
failure_count = 0  # Track consecutive failures

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    # Read the first link from the file and send it to the bot
    await process_next_link()

async def process_next_link():
    global failure_count

    # Read the next link from the file
    if os.path.exists(link_file_path):
        with open(link_file_path, 'r') as file:
            links = file.readlines()

        if links:
            chegg_link = links[0].strip()  # Get the first link

            if chegg_link:
                try:
                    # Send the link to the target bot via DM
                    response_bot_user = await bot.fetch_user(response_bot_id)
                    sent_message = await response_bot_user.send(chegg_link)  # Send DM to the bot
                    print(f"Sent DM with Chegg question link: {chegg_link}")

                    # Wait for the response from the bot
                    def check_response(m):
                        return m.author.id == response_bot_id and bot.user.mention in m.content

                    try:
                        response_message = await bot.wait_for('message', check=check_response, timeout=30)  # Wait for 30 seconds
                        await save_delete_and_process_message(response_message)

                        # Remove the link from the file
                        with open(link_file_path, 'w') as file:
                            file.writelines(links[1:])
                        failure_count = 0  # Reset the failure count
                        print(f"Processed and removed the link: {chegg_link}")

                        # Process the next link
                        await process_next_link()

                    except asyncio.TimeoutError:
                        print(f"No response from Bot 2 for: {chegg_link}")
                        await handle_failed_link(chegg_link)
                except Exception as e:
                    print(f"Error sending DM: {e}")
                    await handle_failed_link(chegg_link)
        else:
            print("No more links to process.")
    else:
        print(f"Link file {link_file_path} not found.")

async def save_delete_and_process_message(message):
    global failure_count

    # Check if the message contains an HTML attachment
    html_attachment = None
    for attachment in message.attachments:
        if attachment.filename.endswith('.html'):
            html_attachment = attachment
            break

    if html_attachment:
        # Save the HTML file temporarily before deletion
        temp_path = os.path.join(save_directory, html_attachment.filename)
        await html_attachment.save(temp_path)
        print(f"Saved temporary HTML file to {temp_path}")

        # Delete the message containing the ping
        await message.delete()
        print("Deleted the response message containing the ping.")

        # Now process the saved HTML file after the message is deleted
        await process_html_file(temp_path)

        # Reset failure count as this was successful
        failure_count = 0
    else:
        print("No HTML attachment found in the response.")
        failure_count += 1
        await handle_failed_link(message.content.strip())

async def handle_failed_link(link):
    global failure_count

    # Add the failed link to failed_processed_links.txt
    with open(failed_links_path, 'a') as failed_file:
        failed_file.write(f"{link}\n")

    print(f"Saved failed link: {link}")

    # Remove the failed link from the main list
    if os.path.exists(link_file_path):
        with open(link_file_path, 'r') as file:
            links = file.readlines()

        if links:
            with open(link_file_path, 'w') as file:
                file.writelines(links[1:])
            print(f"Removed failed link from the main list: {link}")

    # If there are 10 consecutive failures, stop the bot
    if failure_count >= 10:
        print("Three consecutive failures detected. Stopping the bot.")
        await bot.close()

    # Process the next link
    await process_next_link()

async def process_html_file(file_path):
    # Modify the saved HTML file
    chegg_question_id = None
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Updated regex to capture the correct question ID at the end of the URL
    chegg_url = soup.find('a', href=re.compile(r'https:\/\/www\.chegg\.com\/homework-help\/questions-and-answers\/[a-zA-Z0-9_-]+-q([0-9]+)$'))
    if chegg_url:
        chegg_question_id = re.search(r'q([0-9]+)$', chegg_url['href']).group(1)
        print(f"Extracted Chegg Question ID: q{chegg_question_id}")
    else:
        print("Chegg question ID not found in HTML content.")

    # Set the final file path with the extracted question ID
    file_name = f"q{chegg_question_id}.html" if chegg_question_id else os.path.basename(file_path)
    final_file_path = os.path.join(save_directory, file_name)

    # Modify the title tag in the HTML
    title_tag = soup.find('title')
    if title_tag:
        title_tag.string = "Study Solutions"
    else:
        # Create a new <title> tag if it doesn't exist
        new_title_tag = soup.new_tag('title')
        new_title_tag.string = "Study Solutions"
        soup.head.append(new_title_tag)

    # Save the modified HTML with the correct filename
    with open(final_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print(f"Updated and saved HTML file as {final_file_path}")

    # Optionally, remove the temporary file if the name has changed
    if file_path != final_file_path:
        os.remove(file_path)

bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GwQg-h.vSozMhcNOIMX3WzoIBMyDt47qsqd6hMHJEIy2s')  # Replace with your bot token
