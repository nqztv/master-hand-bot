import json
#import logging
import os
import queue
import time

import discord
import gspread
import requests
from discord.ext import commands, tasks

# load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

#logging.basicConfig(filename='perspective_check.log', encoding='utf-8', level=logging.INFO)
#logger = logging.getLogger('perspective')
#logger.setLevel(logging.INFO)
#handler = logging.FileHandler(filename='perspective_check.log', encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)


# set credentials to use on the google sheet
gc = gspread.service_account(filename='credentials.json')

# Open a sheet from a spreadsheet in one go
message_check_sheet = gc.open("Message Check").sheet1

# set perspective api stuff
api_key = str(os.getenv('PERSPECTIVE_API_KEY'))
url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' + '?key=' + api_key)

message_queue = queue.Queue()

class Perspective(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.perspective_check.start()
    
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        #logging.info('Perspective ready')
        print('Perspective ready')

    def cog_unload(self):
        self.perspective_check.cancel()
    
    @commands.Cog.listener("on_message")
    async def queue_message(self, message):
        #logging.info("Queue message: " + message.content)
        message_queue.put([
            str(message.author), 
            str(message.content), 
            str(message.created_at), 
            str(message.edited_at),
            message.id,
            str(message.guild),
            str(message.channel)
        ])
        #logging.info("Queue size: " + str(message_queue.qsize()))
        #await self.bot.process_commands(message)

    @tasks.loop(seconds=2.0)
    async def perspective_check(self):
        if message_queue.empty():
            #print("Queue empty")
            return
    
        message = message_queue.get()

        current_time = time.strftime("%H:%M:%S", time.localtime())

        #logging.info(f'{current_time}: Working on the message "{message[1]}"')

        data_dict = {
            'comment': {'text': message[1]},
            'languages': ['en'],
            'requestedAttributes': {
                'TOXICITY': {},
                'IDENTITY_ATTACK': {},
                'INSULT': {},
                'PROFANITY': {},
                'THREAT': {},
                'SEXUALLY_EXPLICIT': {},
                'FLIRTATION': {},
                'INFLAMMATORY': {},
                'SPAM': {},
                'UNSUBSTANTIAL': {}
            }
        }
        
        response = requests.post(url = url, data = json.dumps(data_dict)) 
        response_dict = json.loads(response.content) 

        perspective_results = [
            response_dict["attributeScores"]["TOXICITY"]["summaryScore"]["value"],
            response_dict["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"],
            response_dict["attributeScores"]["INSULT"]["summaryScore"]["value"],
            response_dict["attributeScores"]["PROFANITY"]["summaryScore"]["value"],
            response_dict["attributeScores"]["THREAT"]["summaryScore"]["value"],
            response_dict["attributeScores"]["SEXUALLY_EXPLICIT"]["summaryScore"]["value"],
            response_dict["attributeScores"]["FLIRTATION"]["summaryScore"]["value"],
            response_dict["attributeScores"]["INFLAMMATORY"]["summaryScore"]["value"],
            response_dict["attributeScores"]["SPAM"]["summaryScore"]["value"],
            response_dict["attributeScores"]["UNSUBSTANTIAL"]["summaryScore"]["value"]
        ]

        message.extend(perspective_results)

        message_check_sheet.append_row(message)

        message_queue.task_done()

        #logging.info(str(message))
        

def setup(bot):
    bot.add_cog(Perspective(bot))
