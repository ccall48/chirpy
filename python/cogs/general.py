import random
from discord.ext import commands
from discord import Embed


class General(commands.Cog, name='General'):
    def __init__(self, client):
        self.client = client

    @commands.group(
        pass_context=True,
        name='meme',
        aliases=['business'],
        hidden=False,
        invoke_without_command=True
    )
    async def meme(self, ctx):
        "Commands to get a blank or random funny meme"
        await ctx.send_help('meme')

    @meme.command(name='blank', aliases=['canvas', 'create'])
    async def imgflip(self, ctx):
        async with self.client.session.get('https://api.imgflip.com/get_memes') as response:
            memes = (await response.json())['data']['memes']
            meme = random.choice(memes)

            embed = Embed(
                title=meme['name'],
                color=random.randint(0, 0xFFFFFF)
            )
            embed.set_image(
                url=meme['url']
            )
        return await ctx.send(embed=embed)

    @meme.command(name='random', aliases=['r'])
    async def memes(self, ctx):
        async with self.client.session.get('https://meme-api.com/gimme/1') as response:
            meme = (await response.json())['memes'][0]

            embed = Embed(
                title=meme['title'],
                color=random.randint(0, 0xFFFFFF)
            )
            embed.set_image(
                url=meme['url']
            )
        return await ctx.send(embed=embed)

    # ----------------------------------------------
    # Cog Tasks
    # ----------------------------------------------

async def setup(client):
    """This is called when the cog is loaded via load_extension"""
    await client.add_cog(General(client))