import discord
from discord.ext import commands
import secrets

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun Commands ready')

    # Commands
    @commands.command()
    async def flip(self, ctx):
        coin = "Heads" if secrets.randbelow(2) == 0 else "Tails"
        await ctx.reply(coin)

def setup(bot):
    bot.add_cog(Fun(bot))