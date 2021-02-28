import discord
from discord.ext import commands, tasks

import gspread
from datetime import datetime
import pytz

# load environment variables from .env
from dotenv import load_dotenv
load_dotenv()


# set credentials to use on the google sheet
gc = gspread.service_account(filename='./credentials.json')

# Open a sheet from a spreadsheet in one go
scheduled_messages_sheet = gc.open("Scheduled Messages").sheet1

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Scheduled Messages ready')

    @tasks.loop(seconds=10.0)
    async def printer(self):
        messages = scheduled_messages_sheet.get_all_values()
        #messages[1][2] = "OVERWRITE"
        status_index = messages[0].index("Status")
        time_index = messages[0].index("Time (Eastern)")
        channel_index = messages[0].index("Channel")
        embed_color_index = messages[0].index("Embed Color")
        embed_title_index = messages[0].index("Embed Title")
        embed_description_index = messages[0].index("Embed Description")
        embed_footer_index = messages[0].index("Embed Footer")
        embed_image_index = messages[0].index("Embed Image")
        embed_thumbnail_index = messages[0].index("Embed Thumbnail")

        for message in messages[1:]:
            if message[status_index] == "Executed":
                continue

            parsed_time = datetime.strptime(message[time_index], '%I:%M %p')
            current_time = datetime.now(pytz.timezone("America/New_York")).time()
            
            message[status_index] = "Valid"

            if (parsed_time.strftime('%H:%M') == current_time.strftime('%H:%M')):
                message[status_index] = "Executed"

                embed_var = discord.Embed()

                if (message[embed_title_index] != ""):
                    embed_var.title = message[embed_title_index]

                if (message[embed_description_index] != ""):
                    embed_var.description = message[embed_description_index]
                
                if (message[embed_color_index] != ""):
                    embed_var.color = int(message[embed_color_index], 0)
                                
                if (message[embed_footer_index] != ""):
                    embed_var.set_footer(text=message[embed_footer_index])

                if (message[embed_image_index] != ""):
                    embed_var.set_image(url=message[embed_image_index])

                if (message[embed_thumbnail_index] != ""):
                    embed_var.set_thumbnail(url=message[embed_thumbnail_index])

                channel = self.bot.get_channel(int(message[channel_index]))
                await channel.send(embed=embed_var)

        scheduled_messages_sheet.update(messages)

def setup(bot):
    bot.add_cog(Schedule(bot))