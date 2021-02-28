import discord
from discord.ext import commands

class Spectator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Spectator Commands ready')

    # Commands
    @commands.command()
    async def bracket (self, ctx):
        embedVar = discord.Embed(title="Link to bracket", description="http://smash.gg/lgpog",color=0x00ff00)
        
        await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(Spectator(bot))