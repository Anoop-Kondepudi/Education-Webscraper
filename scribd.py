import discord
from discord.ext import commands
import re

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent explicitly

class ScribdBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.allowed_channels = [1238373226283929641, 1240006256278638662, 1245866164815659123]  # Update with your channel IDs

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Check if the message is in allowed channels
        if message.channel.id not in self.allowed_channels:
            return

        # Find Scribd URLs in the message content
        scribd_url_list = re.findall(r'https:\/\/(?:www\.|id\.|es\.)scribd\.com\/(document|doc|presentation)\/(\d+)\/', message.content)

        if len(scribd_url_list) > 0:
            # Add a checkmark emoji reaction to indicate processing
            await message.add_reaction('✅')

            for type_, doc_id in scribd_url_list:
                embed_link = f'https://www.scribd.com/embeds/{doc_id}/content'
                if type_ == 'document':
                    embed = discord.Embed(
                        title="Scribd Document",
                        description=f"Click [here]({embed_link}) to view the document.",
                        color=discord.Color.green()
                    )
                elif type_ == 'doc':
                    embed = discord.Embed(
                        title="Scribd Document",
                        description=f"Click [here]({embed_link}) to view the document.",
                        color=discord.Color.green()
                    )
                elif type_ == 'presentation':
                    embed = discord.Embed(
                        title="Scribd Presentation",
                        description=f"Click [here]({embed_link}) to view the presentation.",
                        color=discord.Color.green()
                    )
                else:
                    continue
                
                # Adding footer with author's display name and avatar
                embed.set_footer(text=message.author.display_name, icon_url=message.author.avatar.url)
                
                await message.channel.send(embed=embed)

    async def on_error(self, event_method, *args, **kwargs):
        print(f'Error occurred in {event_method}: {args[0]}')

if __name__ == '__main__':
    bot = ScribdBot()
    bot.run('MTI1NDE5MDkyMDQ4NDUyNDE1Mg.GvVh8p.mOjqiBuiPYYyjqbwaxKQemrNTwcZd99HrE-ImA')